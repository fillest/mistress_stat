<%inherit file="/base.mako" />


<%block name="title">Report list — Mistress</%block>


<div style="text-align: right;">
	% if authenticated_userid (request):
		${authenticated_userid(request)} - <a href="${request.route_path('logout')}">Log out</a>
	% else:
		<a href="${request.route_path('login')}">Log in</a>
	% endif

	|
	<a href="${request.route_path('admin/project.list')}">projects</a>
</div>


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


%if tests:
	<ul class="report-list">
		%for report, data in tests:
			<li>
				<table><tbody><tr>
					<td style="vertical-align: top;"><a href="${request.route_path('report.view', test_id=report.id)}">#${report.id}&nbsp;&nbsp;&nbsp;<span class="js-date" data-utc-time="${int(data['started'] * 1000)}">...</span></a></td>
					<td><pre style="margin: 0 0 0 1em;">${report.comment}</pre></td>
				</tr></tbody></table>
			</li>
		%endfor
	</ul>
%else:
	<span>no tests yet</span>
%endif
