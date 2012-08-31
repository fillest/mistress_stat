from pyramid.view import view_config, forbidden_view_config
from sapyens.helpers import raise_not_found, get_by_id, add_route
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
import pyramid.security
from pyramid.security import remember
import mistress_stat.db.models as models


@add_route('logout', '/logout')
@view_config(route_name = 'logout')
def logout (request):
	resp = HTTPFound(location = request.route_url('root'))
	resp.headerlist.extend(pyramid.security.forget(request))
	return resp

@forbidden_view_config(renderer = 'string', xhr = True)
def acess_denied (request):
	request.response.status = 403
	return 'error: not authorized'

@add_route('login', '/login')
@view_config(route_name = 'login', renderer = '/login.mako')
@forbidden_view_config(renderer = '/login.mako')
def login (request):
	#referrer = request.url
	#if referrer == request.route_url('login'):
		#referrer = request.route_url('section.list')
	#redirect_url = request.POST.get('redirect_url', referrer)
	redirect_url = request.route_url('root')

	if request.method.upper() == 'POST':
		username = request.POST['username']

		user = models.User.query.filter_by(name = username).first()
		if user:
			if request.POST['password'] == user.password:
				resp = HTTPFound(location = redirect_url)
				resp.headerlist.extend(pyramid.security.remember(request, username))
				return resp
			else:
				auth_failed = True
		else:
			auth_failed = True
	else:
		auth_failed = False

		username = ""

	return {
		'auth_failed': auth_failed,
		'redirect_url': redirect_url,
		'username': username,
	}
