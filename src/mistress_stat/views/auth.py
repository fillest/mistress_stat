from pyramid.view import view_config, forbidden_view_config
from sapyens.helpers import raise_not_found, get_by_id, add_route
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
import pyramid.security
from pyramid.security import remember
import mistress_stat.db.models as models


@forbidden_view_config(renderer = 'string', xhr = True)
def acess_denied (request):
	request.response.status = 403
	return 'error: not authorized'
