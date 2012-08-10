import mistress_stat.db
import mistress_stat.db.models as models
import sapyens.script
import sqlalchemy


class Script (sapyens.script.Script):
	def _setup_arg_parser (self, parser):
		parser.add_argument('name', help = "user name")
		parser.add_argument('password', help = "user password")
		parser.add_argument('group', help = "user group")

	def run (self, args, settings, log):
		mistress_stat.db.init(sqlalchemy.engine_from_config(settings, 'sqlalchemy.'))

		user = models.User(
			name = args.name,
			group = args.group,
			password = args.password,
		)
		mistress_stat.db.DBSession.add(user)
		mistress_stat.db.DBSession.commit()

		log.info("user was successfully created, id = %s" % user.id)


main = Script().main
