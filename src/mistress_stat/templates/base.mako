<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title><%block name="title">Mistress</%block></title>

		<script type="text/javascript" src="https://raw.github.com/timrwood/moment/1.5.0/min/moment.min.js"></script>

		<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
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
        ${next.body()}
    </body>
</html>
