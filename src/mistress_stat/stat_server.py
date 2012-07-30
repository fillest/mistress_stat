#coding: utf-8
import gevent.monkey
gevent.monkey.patch_all()
import psycogreen.gevent.psyco_gevent
psycogreen.gevent.psyco_gevent.make_psycopg_green()
import argparse
import logging
import logging.config
from gevent.pywsgi import WSGIServer, WSGIHandler
from gevent.pool import Pool
import gevent
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
import cPickle as pickle
import zlib
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import null_renderer
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import util
import os
import sapyens.helpers
import sapyens.db
from sqlalchemy import engine_from_config
import db
from db import DBSession
from mistress_stat.db.models import Test
import psycopg2
import pyramid.paster
import pyramid.session
from mistress_stat.lib import StepsQueue, stypes, dbdump, no_response
import pyramid.tweens


log = logging.getLogger(__name__)


WORKERS_TIMEOUT = 60  #TODO if e.g. 3, "add_stats: test_id not in tests_cache" is somehow raised


tests_cache = {}
timers = {}
step_ques = {}
finish_que = defaultdict(dict)
workers_last_activity = {}


@sapyens.helpers.add_route('test.register', '/new_test')
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

	t = Test(data = dbdump(test))
	DBSession.add(t)
	DBSession.commit()
	id = t.id

	tests_cache[id] = test

	step_ques[id] = StepsQueue(test['worker_num'])

	workers_last_activity[id] = dict((i, time.time()) for i in range(1, test['worker_num'] + 1)) #TODO send actual ids

	timers[id] = util.start_periodic(1, process_steps, [id])
	timers[id].link_exception()

	log.info("registered test #%s" % id)
	return id




@sapyens.helpers.add_route('test.add_stats', '/add_stats/{test_id}')
@view_config(route_name='test.add_stats', renderer=null_renderer)
def test_add_stats (request):
	test_id = int(request.matchdict['test_id'])
	if test_id not in tests_cache:
		log.error("add_stats: test_id not in tests_cache: %s" % test_id)  #TODO ?
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

			is_finish_only_step = all(len(data) == 1 and data[0]['type'] == stypes.FINISH_TEST for _node_id, data in steps.items())

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
	for _node_id, ts_last in workers_last_activity[test_id].items():
		if now - ts_last >= WORKERS_TIMEOUT:
			is_crashed = True
			break

	is_finished = len(finish_que[test_id]) == test['worker_num']

	if is_crashed:
		is_finished = True

	if is_finished:
		tests_cache[test_id]['finished'] = (now - WORKERS_TIMEOUT) if is_crashed else now
		#DBSession.query(Test).filter_by(id = test_id).update({Test.data: dbdump(tests_cache[test_id])})
		t = DBSession.query(Test).filter_by(id = test_id).one()
		t.data = dbdump(tests_cache[test_id])
		DBSession.add(t)
		DBSession.commit()

		del tests_cache[test_id]

		del finish_que[test_id]

		del step_ques[test_id]

		del workers_last_activity[test_id]

		gevent.kill(timers[test_id])
		del timers[test_id]

		log.info("finished test #%s%s" % (test_id, " (timeout)" if is_crashed else ""))


@sapyens.helpers.add_route('report.get_data', '/get_data/{test_id}')
@view_config(route_name='report.get_data', renderer='json')
def report_get_data (request):
	test_id = int(request.matchdict['test_id'])
	if test_id in tests_cache:
		test = tests_cache[test_id]
	else:
		t = Test.query.filter_by(id = test_id).first()
		if not t:
			return HTTPNotFound()
		test = pickle.loads(str(t.data))

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


def autocommit_tween_factory (handler, registry):
	def tween (request):
		try:
			response = handler(request)
			DBSession.commit()
		except:
			DBSession.rollback()
			raise
		finally:
			DBSession.remove()

		return response
	return tween

def make_wsgi_app (settings):
	config = Configurator(
		settings = settings,
		session_factory = pyramid.session.UnencryptedCookieSessionFactoryConfig(
			'secret_shit', cookie_name = 's', timeout = 60*60*24*3, cookie_max_age = 60*60*24*3,
		),
	)

	config.add_tween('mistress_stat.stat_server.autocommit_tween_factory', under = pyramid.tweens.EXCVIEW)

	config.add_static_view('static', 'static', cache_max_age=3600)

	config.scan(package = 'mistress_stat')

	return config.make_wsgi_app()

def run ():
	parser = argparse.ArgumentParser()
	parser.add_argument('config')
	parser.add_argument('--port', type = int, default = 7777)
	parser.add_argument('--host', default = '0.0.0.0')
	args = parser.parse_args()

	os.environ['TZ'] = 'UTC'
	time.tzset()

	pyramid.paster.setup_logging(args.config)

	settings = pyramid.paster.get_appsettings(args.config)
	db.init(engine_from_config(settings, 'sqlalchemy.'))

	host = args.host
	port = args.port
	log.info("Serving on %s:%s..." % (host, port))
	try:
		WSGIServer((host, port), make_wsgi_app(settings), handler_class=util.LogDisabled, spawn=Pool(100), environ={}).serve_forever()
	except KeyboardInterrupt:
		log.info("interrupted")


if __name__ == '__main__':
	run()
