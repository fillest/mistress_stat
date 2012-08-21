from mistress_stat.db import Reflected, QueryPropertyMixin, Model
from sqlalchemy.orm import relationship


class Test (Model):
	__tablename__ = 'tests'

class User (Model):
	__tablename__ = 'users'
	projects = relationship('Project', secondary = 'users__projects')

	def has_access_to (self, project):
		return project in self.projects

class Project (Model):
	__tablename__ = 'projects'
	tests = relationship('Test', backref = 'project')
