<%inherit file="/base.mako" />


<%block name="title">Report #${test.id} script — Mistress</%block>


<link rel="stylesheet" href="/static/highlight/styles/default.css">
<script src="/static/highlight/highlight.pack.js"></script>


<script>
	hljs.tabReplace = "    ";
	hljs.initHighlightingOnLoad();
</script>

<a href="${request.route_path('report.view', test_id=test.id)}">back to #${test.id}</a>


<pre><code class="lua">
	% if test.script:
${test.script}
	% else:
		no script stored for this test
	% endif
</code></pre>
