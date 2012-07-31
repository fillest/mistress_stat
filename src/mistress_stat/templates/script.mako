<%inherit file="/base.mako" />


<%block name="title">Report #${test.id} script — Mistress</%block>


<link href="http://cdn.bitbucket.org/shekharpro/google_code_prettify/downloads/prettify.css" type="text/css" rel="stylesheet" />
<script type="text/javascript" src="http://cdn.bitbucket.org/shekharpro/google_code_prettify/downloads/prettify.js"></script>

<script>
	$(function () {
		prettyPrint();
	});
</script>

<a href="${request.route_path('report.view', test_id=test.id)}">back to #${test.id}</a>


<pre class="prettyprint lang-lua">
	% if test.script:
${test.script}
	% else:
		no script stored for this test
	% endif
</pre>
