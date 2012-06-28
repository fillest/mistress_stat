logging = {
	'version': 1,
	'disable_existing_loggers': True,
	'handlers': {
		'stdio': {
			'class': 'logging.StreamHandler',
			'formatter': 'simple',
			'level': 'NOTSET',
			'stream': 'ext://sys.stdout'
		},
	},
#		'root': dict(
#			level = logging.INFO,
#			handlers = ['stdio'],
#		),
	'loggers': {
		'mistress_stat': dict(
			level = 'DEBUG',
			handlers = ['stdio'],

		),
		#'__main__': dict(
			#level = 'DEBUG',
			#handlers = ['stdio'],
		#),
		'sqlalchemy.engine': dict(
			level = 'WARN',
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
