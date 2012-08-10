from mistress_stat.db import Reflected, QueryPropertyMixin
from sqlalchemy.orm import relationship


class Test (Reflected, QueryPropertyMixin):
	__tablename__ = 'tests'

class User (Reflected, QueryPropertyMixin):
	__tablename__ = 'users'
	projects = relationship('Project', secondary = 'users__projects')

	def has_access_to (self, project):
		return project in self.projects

class Project (Reflected, QueryPropertyMixin):
	__tablename__ = 'projects'
	tests = relationship('Test', backref = 'project')
