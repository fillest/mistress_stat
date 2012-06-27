<%inherit file="/base.mako" />


<%block name="title">Report list — Mistress</%block>


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
		%for id, data in tests:
			<li><a href="${request.route_path('report.view', test_id=id)}">#${id}&nbsp;&nbsp;&nbsp;<span class="js-date" data-utc-time="${int(data['started'] * 1000)}">...</span></a></li>
		%endfor
	</ul>
%else:
	<span>no tests yet</span>
%endif
