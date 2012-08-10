#coding: utf-8
from mistress_stat.db import DBSession, models
import sapyens.crud
import wtforms as w
import wtforms.validators as v
import wtforms.widgets as ww


class Form (sapyens.crud.SecureForm):
	name = w.TextField(u'Title', [v.Length(min = 1, max = 20), v.Required()])
	password = w.TextField(u'Password', [v.Length(min = 1, max = 20), v.Required()])
	group = w.TextField(u'Group', [v.Length(min = 1, max = 20), v.Required()])
	projects = sapyens.crud.make_relation_field(models.Project, u'Projects')

New, Edit, Create, Update, List, Delete = sapyens.crud.make_view_classes('admin/user', DBSession)

List.edit_title = lambda _, obj: obj.name

@sapyens.helpers.include_to_config()
class UserCrud (sapyens.crud.Crud):
	model = models.User
	form = Form

	new = New
	edit = Edit
	create = Create
	update = Update
	list = List
	delete = Delete
