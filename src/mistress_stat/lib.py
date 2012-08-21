from collections import defaultdict
import cPickle as pickle


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

def dbdump (o):
	return pickle.dumps(o, 2)

def empty_response_app (_environ, _start_response):
	return []
