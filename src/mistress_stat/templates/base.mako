<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title><%block name="title">Untitled</%block> — Mistress</title>

		<script type="text/javascript" src="http://cdnjs.cloudflare.com/ajax/libs/moment.js/1.6.2/moment.min.js"></script>

		<script type="text/javascript" src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.7.2.min.js" charset="UTF-8"></script>
		##<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
		##<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js"></script>
		##<script type="text/javascript" src="/js/flot/jquery.js"></script>

		<script type="text/javascript">
			var l = window.console ? console.log : function () {};

			$(function () {
				$('.js-date').html(function(_index, oldhtml) {
					var el = $(this);
					var time = parseInt(el.attr('data-utc-time'));
					return time ? moment(time).format("dddd, MMMM Do YYYY, HH:mm:ss") : oldhtml;
				});
			});
		</script>
    </head>
    <body>
		<div style="text-align: right;">
			% if request.has_permission('admin'):
				<a href="${request.route_path('admin.index')}">admin panel</a>
				|
			% endif

			% if authenticated_userid (request):
				${authenticated_userid(request)} - <a href="${request.route_path('logout')}">Log out</a>
			% else:
				<a href="${request.route_path('login')}">Log in</a>
			% endif
		</div>

        ${next.body()}
    </body>
</html>
