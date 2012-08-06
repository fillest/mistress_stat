<%inherit file="/base.mako" />


<%block name="title">Projects</%block>


<h4>
	проекты
</h4>


%if projects:
	<ul>
		%for project in projects:
			<li>
				<a href="${request.route_path('report.list', project_id = project.id)}">${project.title}</a>
			</li>
		%endfor
	</ul>
%else:
	<span>No projects available.</span>
%endif
