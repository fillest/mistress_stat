<%inherit file="sapyens.crud:templates/admin/base.mako" />

<%!
	page_title = u"Admin panel"
%>


<%block name="title">${page_title}</%block>


<h3>${page_title}</h3>

<ul>
	<li><a href="${request.route_path('admin/project.list')}">Projects</a></li>
	<li><a href="${request.route_path('admin/user.list')}">Users</a></li>
</ul>
