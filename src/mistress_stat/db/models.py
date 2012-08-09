from mistress_stat.db import Reflected, QueryPropertyMixin
from sqlalchemy.orm import relationship


class Test (Reflected, QueryPropertyMixin):
	__tablename__ = 'tests'

class User (Reflected, QueryPropertyMixin):
	__tablename__ = 'users'
	projects = relationship('Project', secondary = 'users__projects')

class Project (Reflected, QueryPropertyMixin):
	__tablename__ = 'projects'
