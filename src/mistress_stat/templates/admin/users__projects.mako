<%page args="field"/>


<script>
	$('body').on('click', '.js-remove-project', function () {
		$(this).closest('li').remove();
		return false;
	});

	$('body').on('click', '.js-add-project', function () {
		$('#myModal').modal();
		return false;
	});

	function link_project (proj_id, proj_title) {
		if ($('#relation-items input').length) {
			var next_i = parseInt($('#relation-items input').last().attr('name').match(/(\d+)$/)[1]) + 1;
		} else {
			var next_i = 0;
		}

		$('<li><a class="btn btn-small js-remove-project" href="#"><i class="icon-remove"></i></a>'
			+ ' ' + proj_title
			+ '<input id="projects-'+next_i+'" name="projects-'+next_i+'" type="hidden" value="'+proj_id+'"></li>'
			).appendTo($('#relation-items'));

		$('#myModal').modal('hide');

		return false;
	}
</script>

<div>
	<div>Projects</div>

	<ul class="unstyled" id="relation-items">
		##${field.short_name}
		% for subfield in field:
			<li>
				<a class="btn btn-small js-remove-project" href="#"><i class="icon-remove"></i></a>
				${subfield.data.title}

				${subfield(value = subfield.data.id)}
			</li>
		% endfor
	</ul>

	<div><a class="btn btn-small js-add-project" href="#"><i class="icon-plus"></i> add</a></div>
</div>

<div class="modal hide" id="myModal">
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal">×</button>
		<h3>Choose project</h3>
	</div>
	<div class="modal-body">
		<p>
			<ul>
				% for project in field.widget.all_projects():
					<li>
						<a href="#" onclick="return link_project(${project.id}, '${project.title}');">${project.title}</a>
					</li>
				% endfor
			</ul>
		</p>
	</div>
	##<div class="modal-footer">
		##<a href="#" class="btn" data-dismiss="modal">Close</a>
		##<a href="#" class="btn btn-primary">Save changes</a>
	##</div>
</div>
