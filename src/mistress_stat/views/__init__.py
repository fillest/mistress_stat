from pyramid.view import view_config
import cPickle as pickle
from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPForbidden
import sapyens.helpers
from mistress_stat.db.models import Test
from mistress_stat.db import DBSession
import mistress_stat.db.models as models
import pyramid.security

def current_user (request):
	return models.User.query.filter_by(name = pyramid.security.authenticated_userid(request)).one()

@sapyens.helpers.add_route('report.list', '/project/{project_id:\d+}')
@view_config(route_name='report.list', renderer='list.mako', permission='project.view')
def report_list (request):
	project = models.Project.try_get(id = request.matchdict['project_id'])

	if ((not request.has_permission('admin')) and (not current_user(request).has_access_to(project))):
		raise HTTPForbidden()

	tests = []
	for t in Test.query.filter_by(project_id = request.matchdict['project_id']).order_by(Test.id.desc()):
		tests.append((t, pickle.loads(str(t.data))))

	return {
		'project': project,
		'tests': tests,
	}

@sapyens.helpers.add_route('root', '/')
@view_config(route_name = 'root')
def root_stub (request):
	return HTTPFound(location = request.route_url('project.list'))

@sapyens.helpers.add_route('test.delete', '/test/delete/{id:\d+}')
@view_config(route_name='test.delete', permission = 'test.delete')
def test_delete (request):
	test_id = int(request.matchdict['id'])

	project_id = DBSession.query(Test.project_id).filter(Test.id == test_id).scalar() or sapyens.helpers.raise_not_found()

	Test.query.filter_by(id = test_id).delete()
	DBSession.commit()

	#TODO clear cache

	return HTTPFound(location = request.route_path('report.list', project_id = project_id))

@sapyens.helpers.add_route('report.view', '/report/{test_id:\d+}')
@view_config(route_name='report.view', renderer='test.mako')
def report_view (request):
	test_id = request.matchdict['test_id']
	#if test_id == 'latest':
		#res = c.execute('SELECT max(id) FROM tests').fetchone()
		#if not res or not res[0]:
			#return HTTPNotFound()
		#test_id = res[0]
	#else:
	if True:
		#test_id = int(test_id)
		t = Test.query.filter_by(id = test_id).first()
		if not t:
			return HTTPNotFound()

	data = pickle.loads(str(t.data))

	return {
		'test_id': test_id,
		'started': data['started'],
		'finished': data.get('finished'),
		'report': t,
	}

@sapyens.helpers.add_route('test.save_comment', '/test/save_comment/{id:\d+}')
@view_config(route_name='test.save_comment')
def test_save_comment (request):
	test_id = int(request.matchdict['id'])

	DBSession.query(Test).filter_by(id = test_id).update({Test.comment: request.POST['comment']})
	DBSession.commit()

	return HTTPFound(location = request.route_path('report.view', test_id = test_id))

@sapyens.helpers.add_route('test.script', '/test/{id}/script')
@view_config(route_name='test.script', renderer='script.mako')
def report_script (request):
	test = Test.try_get(id = request.matchdict['id'])

	return {
		'test': test,
	}

@sapyens.helpers.add_route('project.list', '/project')
@view_config(route_name = 'project.list', renderer='project/list.mako')
def projects (request):
	projects = models.Project.query.all()

	return {
		'projects': projects,
	}

@sapyens.helpers.add_route('admin.index', '/admin')
@view_config(route_name = 'admin.index', renderer='admin/index.mako', permission='admin')
def admin_index (request):
	return {}
