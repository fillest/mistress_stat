<%inherit file="/base.mako" />

<%block name="title">Report #${test_id}</%block>


		<script type="text/javascript" src="/static/js/flot/jquery.flot.js"></script>
		<script type="text/javascript" src="/static/js/flot/jquery.flot.crosshair.js"></script>
		##<script type="text/javascript" src="/js/flot/jquery.flot.navigate.js"></script>
		##<script type="text/javascript" src="/js/flot/jquery.flot.navigate.patched.js"></script>

        <script type="text/javascript">
			$(function () {
				'use strict';

				var test_id = "${test_id}";


				function get_tz_offset () {
					return - new Date().getTimezoneOffset() * 60 * 1000;
				}
				function localize_time (data) {
					return $.map(data, function (v) {
						return [[v[0] + get_tz_offset(), v[1]]];
					});
				}


				function showTooltip(x, y, contents) {
					$('<div id="tooltip">' + contents + '</div>').css( {
						position: 'absolute',
						display: 'none',
						top: y + 5,
						left: x + 5,
						border: '1px solid #fdd',
						padding: '2px',
						'background-color': '#fee',
						opacity: 0.80
					}).appendTo("body").show();
				}

				function context_tooltip (event, pos, item) {
					if (item) {
						if ((! $("#tooltip").length) || (window.__last_item != item)) {
							window.__last_item = item;
							$("#tooltip").remove();
							showTooltip(item.pageX, item.pageY,
								item.datapoint[1].toFixed(2) + " (" + item.series.label + ")"
								+ "<br/><br/>" + $.plot.formatDate(new Date(item.datapoint[0]), "%H:%M:%S")
							);
						}
					} else {
						$("#tooltip").remove();
					}
				}
				$('.js-plot').bind("plothover", context_tooltip);



				window.__plots = {};
				function make_hover_handler (plot_to_exclude) {
					return function (event, pos, item) {
						$.each(window.__plots, function (_k, plot) {
							if (plot !== plot_to_exclude) {
								plot.setCrosshair(pos);
							}
						});
					};
				}

				//=====================
				function make_opts (container, add_y_time_opts) {
					return {
							//zoom: {interactive: true}, pan: {interactive: true},
								//_plot1.getAxes().yaxis.options.transform  =undefined;
								//_plot1.getAxes().yaxis.options.inverseTransform  =undefined;
								//_plot1.setupGrid()
								//_plot1.draw()

						points: {radius: 2},
						crosshair: { mode: "x" },
						legend: { position: "nw", container: container},
						grid: { hoverable: true},
						series: { shadowSize: 0, lines: { show: true }, points: { show: true } },
						xaxis: { mode: "time",
						//zoomRange: [0.1, 10], panRange: [-10, 10]
						},
						yaxes: [
							$.extend({
								//zoomRange: [0.1, 10], panRange: [-10, 10],
								labelWidth: 70, reserveSpace: true
							}, add_y_time_opts ? {
									tickFormatter: function (val, axis) { return val.toFixed(axis.tickDecimals)+ "&nbsp;s"; },
									tickDecimals: 3,
									transform:  function(v) {return Math.log(v + 0.2) ;},
									inverseTransform: function (v) { return Math.exp(v - 0.2); }
								} : {}
							),
							{
								//zoomRange: [0.1, 10], panRange: [-10, 10],
								labelWidth: 50, reserveSpace: true, position: 'right'
							}
						]
					};
				}


				__plots.resp = $.plot($("#plot_resp"), [], make_opts('#legend_resp', true));
				$("#plot_resp").bind("plothover", make_hover_handler(__plots.resp));
				__plots.resp1 = $.plot($("#plot_resp1"), [], make_opts('#legend_resp1', true));
				$("#plot_resp1").bind("plothover", make_hover_handler(__plots.resp1));

				__plots.conn = $.plot($("#plot_conn"), [], make_opts('#legend_conn', true));
				$("#plot_conn").bind("plothover", make_hover_handler(__plots.conn));
				__plots.conn1 = $.plot($("#plot_conn1"), [], make_opts('#legend_conn1', true));
				$("#plot_conn1").bind("plothover", make_hover_handler(__plots.conn1));

				__plots.rps = $.plot($("#plot_rps"), [], make_opts('#legend_rps'));
				$("#plot_rps").bind("plothover", make_hover_handler(__plots.rps));
				__plots.errors = $.plot($("#plot_errors"), [], make_opts('#legend_errors'));
				$("#plot_errors").bind("plothover", make_hover_handler(__plots.errors));

				__plots.concur = $.plot($("#plot_concur"), [], make_opts('#legend_concur'));
				$("#plot_concur").bind("plothover", make_hover_handler(__plots.concur));

				/*__plots.network = $.plot($("#plot_network"), [], make_opts('#legend_network'));
				$("#plot_network").bind("plothover", make_hover_handler(__plots.network));
*/


				window.stop = false;
				function load_plots_data () {
					if (! window.stop) {
						$.ajax({
							url: "/get_data/" + test_id,
							method: 'GET',
							dataType: 'json',
							cache: false,
							error: function (jqXHR, textStatus, errorThrown) {
								window.console && console.log(jqXHR);
							},
							success: function onDataReceived(data) {
								if (data.finished) {
									window.stop = true;
								}

								var diff = (data.finished - data.started) * 1000;
								var vhourDiff = Math.floor(diff/1000/60/60);  // in hours
								diff -= vhourDiff*1000*60*60;
								var vmindiff = Math.floor(diff/1000/60); // in minutes
								diff -= vmindiff*1000*60;
								var vsecdiff= Math.floor(diff/1000);  // in seconds
								//Text formatting
								var hourtext = '00';
								if (vhourDiff > 0){ hourtext = String(vhourDiff);}
								if (hourtext.length == 1){hourtext = '0' + hourtext};
								var mintext = '00';
								if (vmindiff > 0){ mintext = String(vmindiff);}
								if (mintext.length == 1){mintext = '0' + mintext};
								var sectext = '00';
								if (vsecdiff > 0){ sectext = String(vsecdiff);}
								if (sectext.length == 1){sectext = '0' + sectext};

								$('#test_duration_value').html(hourtext + ":" + mintext + ':' + sectext);


								$('#test_reqs_total_value').html(data.reqs_total);
								$('#test_resp_errors_total_value').html(data.resp_errors_total + ' (' + (data.resp_errors_total / data.reqs_total * 100).toFixed(1) + '%)');
								$('#test_resp_timeouts_total_value').html(data.resp_timeouts_total + ' (' + (data.resp_timeouts_total / data.reqs_total * 100).toFixed(1) + '%)');
								$('#test_resp_bad_statuses_total_value').html(data.resp_bad_statuses_total + ' (' + (data.resp_bad_statuses_total / data.reqs_total * 100).toFixed(1) + '%)');
								$('#test_resp_successful_total_value').html(data.resp_successful_total + ' (' + (data.resp_successful_total / data.reqs_total * 100).toFixed(1) + '%)');


								//plot.getData()[1].color = "rgba(175,216,248, 0.1)"
								//plot.draw()
								//http://groups.google.com/group/flot-graphs/browse_thread/thread/cbe64499abf9a5a1?pli=1


								//=================================================

								var d = [];
								var d1 = [];
								$.each(data.resp_time, function (grp, values) {
									(grp == 'static' ? d1 : d).push({label: "resp_time <strong>" + grp + '</strong>', data: localize_time(values)});
								});
								$.each(data.resp_time_meav, function (grp, values) {
									(grp == 'static' ? d1 : d).push({label: "resp_time med abs dev <strong>" + grp + '</strong>', data: localize_time(values)});
								});
								__plots.resp.setData(d);
								__plots.resp.setupGrid();
								__plots.resp.draw();
								__plots.resp1.setData(d1);
								__plots.resp1.setupGrid();
								__plots.resp1.draw();


								var d = [];
								var d1 = [];
								$.map(data.conn_time, function(values, grp) {
									(grp == 'static' ? d1 : d).push({label: "conn_time <strong>" + grp + '</strong>', data: localize_time(values)});
								});
								$.map(data.conn_time_meav, function(values, grp) {
									(grp == 'static' ? d1 : d).push({label: "conn_time med abs dev <strong>" + grp + '</strong>', data: localize_time(values)});
								});
								__plots.conn.setData(d);
								__plots.conn.setupGrid();
								__plots.conn.draw();
								__plots.conn1.setData(d1);
								__plots.conn1.setupGrid();
								__plots.conn1.draw();


								var d = [];
								var d1 = [];
								$.each(data.statuses, function(status, values) {
									if (status.slice(0, '200'.length) == '200') {
										d.push({label: "resp/s http" + status, data: localize_time(values)});
									} else {
										d1.push({label: "resp/s http" + status, data: localize_time(values)});
									}
								});
								$.each(data.errors, function(status, values) {
									d1.push({label: "error " + status + ' <span style="color: #aaa;">(right axis)</span>', data: localize_time(values), yaxis: 2});
								});
								d.push({label: "req/sec", data: localize_time(data.req_sent)});
								__plots.rps.setData(d);
								__plots.rps.setupGrid();
								__plots.rps.draw();
								__plots.errors.setData(d1);
								__plots.errors.setupGrid();
								__plots.errors.draw();


								var d = [
									{label: 'concur_users_max <span style="color: #aaa;">(left axis)</span>', data: localize_time(data.concur_users_num_max)},
									{label: 'concur_users_min <span style="color: #aaa;">(left axis)</span>', data: localize_time(data.concur_users_num_min)},
									{label: 'concur_conns_min <span style="color: #aaa;">(left axis)</span>', data: localize_time(data.concur_conns_num_min)},
									{label: 'concur_conns_max <span style="color: #aaa;">(left axis)</span>', data: localize_time(data.concur_conns_num_max)},
									{label: 'sessions_started <span style="color: #aaa;">(right axis)</span>', data: localize_time(data.start_session), yaxis: 2}
								];
								__plots.concur.setData(d);
								__plots.concur.setupGrid();
								__plots.concur.draw();

								//=================================================network
								/*
								var d = [];
								d.push({label: "KBytes received", data: localize_time(data.network_received)});
								d.push({label: "KBytes sent", data: localize_time(data.network_sent)});
								__plots.network.setData(d);
								__plots.network.setupGrid();
								__plots.network.draw();
								*/
							}
						});
					}

					setTimeout(load_plots_data, 3000);
				}
				load_plots_data();
			});
		</script>

		<style type="text/css">
			hr {border: 0; height: 1px; color: #000; background-color: #000;}
			.plots {border-collapse: collapse;}
			.plots .legend {border:1px solid #ddd; margin-top:1em;}
			.plots > tbody > tr > td {
				vertical-align: top;
				border-bottom: 1px dotted #999;
				padding: 1em 0 1em 0;
				margin: 0;
			}
			.xAxis .tickLabel:nth-child(even) {color: #aaa;}
			.nav a {margin-right: 1em;}
			.js-plot {width: 1100px;}
			.nav-icon:hover {opacity: 0.5;}
		</style>


		##<button onclick="window.stop = ! window.stop;">pause/resume</button>

		<div class="nav">
			<a href="${request.route_path('report.list', project_id = report.project.id)}"><img class="nav-icon" title="back to list" src="/static/img/glyphicons_small/glyphicons_114_list.png" style="width: 16px;" alt="back to report list" /></a>
			##<a href="/report/${test_id}"><img class="nav-icon" title="link to this report" src="/static/img/glyphicons_small/glyphicons_050_link.png" style="width: 13px;" alt="#" /></a>
			<a href="${request.route_path('test.script', id = test_id)}"><img class="nav-icon" title="test script" src="/static/img/glyphicons_small/glyphicons_351_book_open.png" style="width: 15px;" alt="test script" /></a>
		</div>

		<hr />

		<div>
			<img title="Comment" src="/static/img/glyphicons_small/glyphicons_309_comments.png" alt="Comment" />
			<form action="${request.route_path('test.save_comment', id = test_id)}" method="post" style="display: inline;">
				<textarea name="comment" rows="2" cols="100" style="vertical-align: top; margin-left: 0.5em;">${report.comment}</textarea>
				<input type="submit" value="update">
			</form>
		</div>

		<hr />

		<div class="nav">
			<span>Report #${test_id}</span>
			% if request.has_permission('test.delete'):
				<a href="${request.route_path('test.delete', id = test_id)}">delete</a>
			% endif
			<table><tbody>
				<tr><td>Test duration</td><td style="padding-left: 1em;"><span id="test_duration_value">...</span> (<span class="js-date" data-utc-time="${int(started * 1000)}">...</span> - <span class="js-date" data-utc-time="${int(finished * 1000) if finished else 0}">...</span>)</td></tr>
				<tr><td>Requests total</td><td style="padding-left: 1em;"><span id="test_reqs_total_value">...</span></td></tr>
				<tr><td>Successful responses total</td><td style="padding-left: 1em;"><span id="test_resp_successful_total_value">...</span></td></tr>
				<tr><td>Response bad statuses total</td><td style="padding-left: 1em;"><span id="test_resp_bad_statuses_total_value">...</span></td></tr>
				<tr><td>Response timeouts total</td><td style="padding-left: 1em;"><span id="test_resp_timeouts_total_value">...</span></td></tr>
				<tr><td>Response errors total</td><td style="padding-left: 1em;"><span id="test_resp_errors_total_value">...</span></td></tr>
			</tbody></table>
		</div>

		<hr />

		<div style="">
			<table class="plots"><tbody>
				<tr>
					<td>Response latency<div class="legend" id="legend_resp"></div></td>
					<td><div class="js-plot" id="plot_resp" style="height: 400px"></div></td>
					<td>
						##<label><input type="checkbox" checked="checked" autocomplete="off" />log-scale Y axis</label>
						##<br/><br/>
					</td>
				</tr>
				<tr style="display:none;">
					<td>Response latency<div class="legend" id="legend_resp1"></div></td>
					<td><div class="js-plot" id="plot_resp1" style="height: 400px"></div></td>
					<td></td>
				</tr>
				<tr>
					<td>Connection latency<div class="legend" id="legend_conn"></div></td>
					<td><div class="js-plot" id="plot_conn" style="height: 200px"></div></td>
					<td></td>
				</tr>
				<tr style="display:none;">
					<td>Connection latency<div class="legend" id="legend_conn1"></div></td>
					<td><div class="js-plot" id="plot_conn1" style="height: 200px"></div></td>
					<td></td>
				</tr>
				<tr>
					<td>Throughput<div class="legend" id="legend_rps"></div></td>
					<td><div class="js-plot" id="plot_rps" style="height: 300px"></div></td>
					<td></td>
				</tr>
				<tr>
					<td>Errors<div class="legend" id="legend_errors"></div></td>
					<td><div class="js-plot" id="plot_errors" style="height: 300px"></div></td>
					<td></td>
				</tr>
				<tr>
					<td>Concurrency<div class="legend" id="legend_concur"></div></td>
					<td><div class="js-plot" id="plot_concur" style="height: 150px"></div></td>
					<td></td>
				</tr>
				<%doc>
				<tr>
					<td>
						Network usage<br/>(total within computer)
						<div class="legend" id="legend_network"></div>
					</td>
					<td><div class="js-plot" id="plot_network" style="height: 150px"></div></td>
					<td></td>
				</tr>
				</%doc>
			</tbody></table>
		</div>
