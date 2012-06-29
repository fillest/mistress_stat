import logging


logging = {
	'version': 1,
	'disable_existing_loggers': True,
	'handlers': {
		'stdio': {
			'class': 'logging.StreamHandler',
			'formatter': 'simple',
			'level': logging.NOTSET,
			'stream': 'ext://sys.stdout'
		},
	},
	'loggers': {
		'mistress_stat': dict(
			level = logging.DEBUG,
			handlers = ['stdio'],
		),
		'__main__': dict(
			level = logging.DEBUG,
			handlers = ['stdio'],
		),
		'sqlalchemy.engine': dict(
			level = logging.WARN,
			handlers = ['stdio'],
		),
	},

	#http://docs.python.org/library/logging.html#logrecord-attributes
	#http://docs.python.org/library/stdtypes.html#string-formatting-operations
	'formatters': {
		'simple': {
			'format': '%(asctime)sUTC %(levelname)-5s [%(filename)s:%(funcName)s:%(lineno)d]  %(message)s'
		},
	},
}
