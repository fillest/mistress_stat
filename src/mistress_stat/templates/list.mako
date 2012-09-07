<%inherit file="/base.mako" />


<%block name="title">${project.title} ← reports</%block>


<style>
	a:link {color: #333;}
	a:visited {color: #333;}
	a:hover {color: #888;}
	.report-list {
		line-height: 1.3em;
		margin-left: 2em;
		list-style-type: none;
	}
</style>


<h4>
	<a href="${request.route_path('project.list')}">проекты</a> &rarr;
	${project.title}
</h4>


%if tests:
	<ul class="report-list">
		%for report in tests:
			<li>
				<table><tbody><tr>
					<td style="vertical-align: top;"><a href="${request.route_path('report.view', test_id=report.id)}">#${report.id}&nbsp;&nbsp;&nbsp;<span class="js-date" data-utc-time="${int(to_ts(report.start_time) * 1000)}">...</span></a></td>
					<td><pre style="margin: 0 0 0 1em;">${report.comment}</pre></td>
				</tr></tbody></table>
			</li>
		%endfor
	</ul>
%else:
	<span>no tests yet</span>
%endif
