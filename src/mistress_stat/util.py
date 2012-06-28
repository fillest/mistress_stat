import gevent
import gevent.pywsgi


def start_periodic (interval, callback, params = None):
	params = params or ()
	def run ():
		while True:
			gevent.sleep(interval)
			callback(*params)
	return gevent.spawn(run)

def get_median (l):
	sv = sorted(l)
	if len(sv) % 2 == 1:
		return sv[(len(sv) + 1) / 2 - 1]
	else:
		lower = sv[len(sv) / 2 - 1]
		upper = sv[len(sv) / 2]

		return (float(lower + upper)) / 2

class LogDisabled (gevent.pywsgi.WSGIHandler):
	def log_request (self):
		pass


def get_rx ():
	with open('/sys/class/net/eth0/statistics/rx_bytes', 'r') as f:
		return int(f.read().strip())

def get_tx ():
	with open('/sys/class/net/eth0/statistics/tx_bytes', 'r') as f:
		return int(f.read().strip())
