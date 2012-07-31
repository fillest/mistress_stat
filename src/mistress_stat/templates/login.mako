<%inherit file="/base.mako" />

<%block name="title">log in</%block>


<script type="text/javascript">
    window.addEvent('domready', function () {
        $('username').focus();
    });
</script>

<form action="${request.route_path('login')}" method="post">
    %if auth_failed:
        <div style="color: red;">auth failed</div>
    %endif

    <input type="hidden" name="redirect_url" value="${redirect_url}" />

    <br /><label>username <input id="username" type="text" name="username" value="${username}" /></label>
    <br /><label>password <input type="password" name="password" value="" /></label>
    <br /><input type="submit" value="log in" />
</form>
