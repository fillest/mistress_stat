#coding: utf-8
from mistress_stat.db import DBSession, models
import sapyens.crud
import wtforms as w
import wtforms.validators as v


class Form (sapyens.crud.SecureForm):
	title = w.TextField(u'Title', [v.Length(min = 1, max = 20), v.Required()])
	slug = w.TextField(u'Slug', [v.Length(min = 1, max = 20), v.Required()])


New, Edit, Create, Update, List, Delete = sapyens.crud.make_view_classes('admin/project', DBSession)

List.edit_title = lambda _, obj: obj.title


@sapyens.helpers.include_to_config()
class ProjectCrud (sapyens.crud.Crud):
	model = models.Project
	form = Form

	new = New
	edit = Edit
	create = Create
	update = Update
	list = List
	delete = Delete
