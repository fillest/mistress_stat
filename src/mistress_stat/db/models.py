from mistress_stat.db import Reflected, QueryPropertyMixin


class Test (Reflected, QueryPropertyMixin):
	__tablename__ = 'tests'

class User (Reflected, QueryPropertyMixin):
	__tablename__ = 'users'

class Project (Reflected, QueryPropertyMixin):
	__tablename__ = 'projects'
