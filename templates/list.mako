<%inherit file="/base.mako" />

<%block name="title">Report list — Mistress</%block>

%if tests:
	<ul>
		%for id, data in tests:
			<li><a href="${request.route_path('report.view', test_id=id)}">#${id}&nbsp;&nbsp;&nbsp;<span class="js-date" data-utc-time="${int(data['started'] * 1000)}">...</span></a></li>
		%endfor
	</ul>
%else:
	<span>no tests yet</span>
%endif
