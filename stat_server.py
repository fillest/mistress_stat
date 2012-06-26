#coding: utf-8
import argparse
import logging
import logging.config
from gevent.pywsgi import WSGIServer, WSGIHandler
from gevent.pool import Pool
import gevent
import gevent.monkey
gevent.monkey.patch_all()
from webob import Request
import time
import sys
import itertools
import re
import json #remember: numeric keys are being converted to strings
import random
import collections
from collections import defaultdict
import gevent.core
from routes import Mapper
import sqlite3
import cPickle as pickle
import zlib
from pyramid.config import Configurator
#from pyramid.paster import (
    #get_appsettings,
    #setup_logging,
#)
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import null_renderer
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import util
import config
import os
import sapyens.helpers


log = logging.getLogger(__name__)


WORKERS_TIMEOUT = 10  #TODO if e.g. 3, "add_stats: test_id not in tests_cache" is somehow raised


class StepsQueue (object):
	def __init__ (self, nodes_num):
		self._buf = defaultdict(dict)
		self._step = 1
		self._nodes_num = nodes_num

	def put (self, data, step, node_id):
		self._buf[step][node_id] = data

	def next (self):
		steps = self._buf.get(self._step)
		if steps and (len(steps) == self._nodes_num):
			self._step += 1
			return steps
		else:
			return None

conn = sqlite3.connect('tests.sqlite')
#conn.text_factory = str  #pickle storing workaround
c = conn.cursor()


class stypes (object):
	CONCUR_USERS_NUM_MAX = 2
	START_SESSION = 3
	RESPONSE_TIME = 4
	RESPONSE_STATUS = 5
	REQUEST_SENT = 6
	CONNECT_TIME = 7
	CONCUR_USERS_NUM_MIN = 8
	CONNECT_ERROR = 9
	RESPONSE_ERROR = 10
	CONCUR_CONNS_NUM_MIN = 11
	CONCUR_CONNS_NUM_MAX = 12
	FINISH_TEST = 13


tests_cache = {}
timers = {}
step_ques = {}
finish_que = defaultdict(dict)
workers_last_activity = {}


def dbdump (o):
	return sqlite3.Binary(pickle.dumps(o, 2))



def check_or_setup_db ():
	with conn:
		c.execute("""SELECT count(*) FROM sqlite_master
			WHERE type = 'table' and name = 'tests'""")
		if not c.fetchone()[0]:
			print "** creating db tables"
			conn.execute("""CREATE TABLE tests(
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				data BLOB
			)""")


@sapyens.helpers.add_route('test.delete', '/test/delete/{id:\d+}')
@view_config(route_name='test.delete')
def test_delete (request):
	test_id = int(request.matchdict['id'])
	c.execute('DELETE FROM tests where id = ?', (test_id,))
	#TODO clear cache

	return HTTPFound(location = request.route_path('report.list'))

@view_config(route_name='test.register', renderer='string')
def test_register (request):
	test = {
		'started': float(request.GET['delayed_start_time']),
		'finished': None,

		'worker_num': int(request.GET['worker_num']),

		'result': defaultdict(list),
		'reqs_total': 0,
		'resp_errors_total': 0,
		'resp_timeouts_total': 0,
		'resp_bad_statuses_total': 0,
		'resp_successful_total': 0,

		'resp_statuses': set(),
		'errors': set(),
		'groups': set(),

		'rx_snapshot': util.get_rx(),
		'tx_snapshot': util.get_tx(),

		#'state': 'created',
	}

	with conn:
		id = c.execute('insert into tests (data) values (?)', (dbdump(test),)).lastrowid
	tests_cache[id] = test

	step_ques[id] = StepsQueue(test['worker_num'])

	workers_last_activity[id] = dict((i, time.time()) for i in range(1, test['worker_num'] + 1)) #TODO send actual ids

	timers[id] = util.start_periodic(1, process_steps, [id])
	timers[id].link_exception()

	log.info("registered test #%s" % id)

	return id


def no_response (_environ, _start_response):
	return []

@view_config(route_name='test.add_stats', renderer=null_renderer)
def test_add_stats (request):
	test_id = int(request.matchdict['test_id'])
	if test_id not in tests_cache:
		print "** add_stats: test_id not in tests_cache: %s" % test_id  #TODO ?
		return no_response

	pack = json.loads(zlib.decompress(request.body))

	step_ques[test_id].put(pack['data'], pack['step'], pack['node'])

	return no_response

def process_steps (test_id):
	#print "tick", test_id
	#TODO what if this gets interrupted by kill during io?
	#TODO dont forget actual finish time

	test = tests_cache[test_id]

	#new_rx = get_rx()
	#rx = new_rx - test['rx_snapshot']
	#test['rx_snapshot'] = new_rx
	#new_tx = get_tx()
	#tx = new_tx - test['tx_snapshot']
	#test['tx_snapshot'] = new_tx

	while True:
		steps = step_ques[test_id].next()
		if steps:
			buf_statuses = defaultdict(int)
			buf_resp_time = defaultdict(list)
			buf_conn_time = defaultdict(list)
			buf_errors = defaultdict(int)
			buf_concur_users_num_max = 0
			buf_concur_users_num_min = 0
			buf_concur_conns_num_min = 0
			buf_concur_conns_num_max = 0
			buf_start_session = 0
			buf_request_sent = 0

			is_finish_only_step = all(len(data) == 1 and data[0]['type'] == stypes.FINISH_TEST for node_id, data in steps.items())

			for node_id, data in steps.items():
				node_id = int(node_id)
				workers_last_activity[test_id][node_id] = time.time()

				for rec in data:
					data_type = rec['type']
					if data_type == stypes.RESPONSE_STATUS:
						grp, status = rec['value']

						if int(status) not in (200,):  #TODO move to test?
							test['resp_bad_statuses_total'] += 1
						else:
							test['resp_successful_total'] += 1

						status = str(status) + " " + grp
						tests_cache[test_id]['resp_statuses'].add(status)
						buf_statuses[status] += 1
					elif data_type == stypes.RESPONSE_TIME:
						grp_name, resp_time = rec['value']
						buf_resp_time[grp_name].append(resp_time)
						tests_cache[test_id]['groups'].add(grp_name)
					elif data_type == stypes.CONNECT_TIME:
						grp_name, timelen = rec['value']
						buf_conn_time[grp_name].append(timelen)
						tests_cache[test_id]['groups'].add(grp_name)
					elif data_type == stypes.CONCUR_USERS_NUM_MAX:
						buf_concur_users_num_max += rec['value']
					elif data_type == stypes.CONCUR_USERS_NUM_MIN:
						buf_concur_users_num_min += rec['value']
					elif data_type == stypes.CONCUR_CONNS_NUM_MIN:
						buf_concur_conns_num_min += rec['value']
					elif data_type == stypes.CONCUR_CONNS_NUM_MAX:
						buf_concur_conns_num_max += rec['value']
					elif data_type == stypes.START_SESSION:
						buf_start_session += rec['value']
					elif data_type == stypes.REQUEST_SENT:
						test['reqs_total'] += rec['value']

						buf_request_sent += rec['value']
					elif data_type == stypes.CONNECT_ERROR:
						tests_cache[test_id]['errors'].add("connect " + rec['value'])
						buf_errors[rec['value']] += 1
					elif data_type == stypes.RESPONSE_ERROR:
						if "timeout" in rec['value']:
							test['resp_timeouts_total'] += 1
						else:
							test['resp_errors_total'] += 1

						ern = "response " + rec['value']
						tests_cache[test_id]['errors'].add(ern)

						buf_errors[ern] += 1
					elif data_type == stypes.FINISH_TEST:
						finish_que[test_id][node_id] = True
					else:
						raise NotImplementedError(rec['type'])

			if not is_finish_only_step:
				res = test['result']

				rt = {}
				rm = {}
				for grp, times in buf_resp_time.iteritems():
					resp_time_med = util.get_median(times)
					rt[grp] = resp_time_med
					rm[grp] = util.get_median(abs(t - resp_time_med) for t in times)
				res['resp_time'].append(rt)
				res['resp_time_meav'].append(rm)  #TODO rename to med_abs_dev

				rt = {}
				rm = {}
				for grp, times in buf_conn_time.iteritems():
					resp_time_med = util.get_median(times)
					rt[grp] = resp_time_med
					rm[grp] = util.get_median(abs(t - resp_time_med) for t in times)
				res['conn_time'].append(rt)
				res['conn_time_meav'].append(rm)  #TODO rename to med_abs_dev

				res['start_session'].append(buf_start_session)
				res['resp_status'].append(buf_statuses)
				res['req_sent'].append(buf_request_sent)
				res['errors'].append(buf_errors)
				res['concur_users_num_max'].append(buf_concur_users_num_max)
				res['concur_users_num_min'].append(buf_concur_users_num_min)
				res['concur_conns_num_min'].append(buf_concur_conns_num_min)
				res['concur_conns_num_max'].append(buf_concur_conns_num_max)

				#res['network_received'].append(float(rx) / 1024.0)
				#res['network_sent'].append(float(tx) / 1024.0)
		else:
			break

	is_crashed = False
	now = time.time()
	for node_id, ts_last in workers_last_activity[test_id].items():
		if now - ts_last >= WORKERS_TIMEOUT:
			is_crashed = True
			break

	is_finished = len(finish_que[test_id]) == test['worker_num']

	if is_crashed:
		is_finished = True

	if is_finished:
		tests_cache[test_id]['finished'] = (now - WORKERS_TIMEOUT) if is_crashed else now
		with conn:
			c.execute('UPDATE tests SET data = ? WHERE id = ?', (dbdump(tests_cache[test_id]), test_id))
		del tests_cache[test_id]

		del finish_que[test_id]

		del step_ques[test_id]

		del workers_last_activity[test_id]

		gevent.kill(timers[test_id])
		del timers[test_id]

		log.info("finished test #%s%s" % (test_id, " (timeout)" if is_crashed else ""))


@view_config(route_name='report.get_data', renderer='json')
def report_get_data (request):
	test_id = int(request.matchdict['test_id'])
	if test_id in tests_cache:
		test = tests_cache[test_id]
	else:
		res = c.execute('SELECT data FROM tests where id = ?', (test_id,)).fetchone()
		if not res:
			return HTTPNotFound()
		test = pickle.loads(str(res[0]))

	t = test['started']
	r = test['result']
	result = defaultdict(list)

	result['started'] = test['started']
	result['finished'] = test['finished']

	result['reqs_total'] = test['reqs_total']
	result['resp_errors_total'] = test['resp_errors_total']
	result['resp_timeouts_total'] = test['resp_timeouts_total']
	result['resp_bad_statuses_total'] = test['resp_bad_statuses_total']
	result['resp_successful_total'] = test['resp_successful_total']

	result['statuses'] = defaultdict(list)
	result['errors'] = defaultdict(list)
	result['resp_time'] = defaultdict(list)
	result['resp_time_meav'] = defaultdict(list)
	result['conn_time'] = defaultdict(list)
	result['conn_time_meav'] = defaultdict(list)
	i = itertools.izip(r['resp_time'], r['resp_time_meav'], r['conn_time'], r['conn_time_meav'], r['start_session'], r['resp_status'], r['req_sent'], r['errors'],
			r['concur_users_num_max'], r['concur_users_num_min'], r['concur_conns_num_min'], r['concur_conns_num_max']
			#, r['network_received'], r['network_sent']
			)
	for (resp_time, resp_time_meav, conn_time, conn_time_meav, start_session, statuses, req_sent, errors,
			concur_users_num_max, concur_users_num_min, concur_conns_num_min, concur_conns_num_max) in i: #, network_received, network_sent
		js_t = int(t * 1000)

		for grp in test['groups']:
			result['resp_time'][grp].append((js_t, resp_time.get(grp, 0)))
			result['resp_time_meav'][grp].append((js_t, resp_time_meav.get(grp, 0)))
			result['conn_time'][grp].append((js_t, conn_time.get(grp, 0)))
			result['conn_time_meav'][grp].append((js_t, conn_time_meav.get(grp, 0)))

		for status in test['resp_statuses']:
			result['statuses'][status].append((js_t, statuses.get(status, 0)))
		for error in test['errors']:
			result['errors'][error].append((js_t, errors.get(error, 0)))
		result['req_sent'].append((js_t, req_sent))
		result['concur_users_num_max'].append((js_t, concur_users_num_max))
		result['concur_users_num_min'].append((js_t, concur_users_num_min))
		result['concur_conns_num_min'].append((js_t, concur_conns_num_min))
		result['concur_conns_num_max'].append((js_t, concur_conns_num_max))
		result['start_session'].append((js_t, start_session))
		#result['network_received'].append((js_t, network_received))
		#result['network_sent'].append((js_t, network_sent))

		t += 1

	return result

@view_config(route_name='report.view', renderer='test.mako')
def report_view (request):
	test_id = request.matchdict['test_id']
	if test_id == 'latest':
		res = c.execute('SELECT max(id) FROM tests').fetchone()
		if not res or not res[0]:
			return HTTPNotFound()
		test_id = res[0]
	else:
		test_id = int(test_id)
		if not c.execute('SELECT count(*) FROM tests where id = ?', (test_id,)).fetchone()[0]:
			return HTTPNotFound()

	data = pickle.loads(str(c.execute('SELECT data FROM tests where id = ?', (test_id,)).fetchone()[0]))

	return {
		'test_id': test_id,
		'started': data['started'],
		'finished': data.get('finished'),
	}

@view_config(route_name='report.list', renderer='list.mako')
def report_list (request):
	tests = []
	for v in c.execute('SELECT id, data FROM tests order by id desc'):
		tests.append((v[0], pickle.loads(str(v[1]))))

	return {
		'tests': tests
	}


def papp ():
	#~ settings = get_appsettings('test.ini')
	settings = {
		'pyramid.reload_templates': True,
		'pyramid.debug_authorization': False,
		'pyramid.debug_notfound': False,
		'pyramid.debug_routematch': False,
		'pyramid.default_locale_name': 'en',
		'pyramid.includes': ['pyramid_debugtoolbar'],

		'debugtoolbar.hosts': '10.40.25.155',

		'mako.directories': 'templates',
		'mako.module_directory': '/tmp/mistress_statserver/compiled_templates',
		'mako.strict_undefined': 'true',
    }

	config = Configurator(
		settings = settings,
	)

	config.add_static_view('js', 'static/js', cache_max_age=3600)

	_init_routes(config)

	config.scan()

	return config.make_wsgi_app()

def _init_routes (config):
	config.add_route('report.list', '/report/list')
	config.add_route('report.view', '/report/{test_id}')
	config.add_route('report.get_data', '/get_data/{test_id}')
	config.add_route('test.register', '/new_test')
	config.add_route('test.finish', '/finish_test/{test_id}')
	config.add_route('test.add_stats', '/add_stats/{test_id}')



def run ():
	parser = argparse.ArgumentParser()
	parser.add_argument('port', metavar='port', type=int, default=7777, nargs='?')
	parser.add_argument('host', metavar='host', type=str, default='0.0.0.0', nargs='?')
	args = parser.parse_args()

	os.environ['TZ'] = 'UTC'
	time.tzset()

	logging.config.dictConfig(config.logging)

	check_or_setup_db()

	host = args.host
	port = args.port
	log.info("Serving on %s:%s..." % (host, port))
	try:
		WSGIServer((host, port), papp(), handler_class=util.LogDisabled, spawn=Pool(100), environ={}).serve_forever()
	except KeyboardInterrupt:
		log.info("interrupted")


if __name__ == '__main__':
	run()
