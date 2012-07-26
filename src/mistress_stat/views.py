from pyramid.view import view_config
import cPickle as pickle
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import sapyens.helpers
from mistress_stat.db.models import Test
from mistress_stat.db import DBSession


@sapyens.helpers.add_route('report.list', '/report/list')
@view_config(route_name='report.list', renderer='list.mako')
def report_list (request):
	tests = []
	for t in Test.query.order_by(Test.id.desc()):
		tests.append((t, pickle.loads(str(t.data))))

	return {
		'tests': tests
	}

@sapyens.helpers.add_route('root', '/')
@view_config(route_name = 'root')
def root_stub (request):
	return HTTPFound(location = request.route_url('report.list'))

@sapyens.helpers.add_route('test.delete', '/test/delete/{id:\d+}')
@view_config(route_name='test.delete')
def test_delete (request):
	test_id = int(request.matchdict['id'])

	Test.query.filter_by(id = test_id).delete()
	DBSession.commit()

	#TODO clear cache

	return HTTPFound(location = request.route_path('report.list'))

@sapyens.helpers.add_route('report.view', '/report/{test_id}')
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
