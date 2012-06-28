from pyramid.view import view_config
from db.models import Test
import cPickle as pickle


@view_config(route_name='report.list', renderer='list.mako')
def report_list (request):
	tests = []
	for t in Test.query.order_by(Test.id.desc()):
		tests.append((t, pickle.loads(str(t.data))))

	return {
		'tests': tests
	}
