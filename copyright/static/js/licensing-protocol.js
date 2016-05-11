/* licensing-protocol.js
 * ---------------------
 * Interface to get the licensing protocol questions
 * and generate the corresponding elements on the screen
 */

$.get('/licensing-protocol', function(response) {
	// delete the loading message
	$('#loading-message').remove();

	response.sections.forEach(function(section) {

		// append the title of the section
		if (section.title) {
			$('<h3>').text(section.title).appendTo('#licenseInfo');
		}

		// append the description of the section
		if (section.description) {
			section.description.forEach(function(line) {
				if (line === 'BREAK') {
					$('<br>').appendTo('#licenseInfo');
				} else {
					$('<p>').text(line).appendTo('#licenseInfo');
				}
			});
		}

		// for each question in the section
		section.questions.forEach(function(question) {
			// make a new group object to be built up
			var $group = $('<div class="form-group">');
			if (question.id) $group.attr('id', question.id);

			// append the title of the question
			if (question.title) {
				$('<h4>').text(question.title).appendTo($group);
			}

			// append the subtitle of the question
			if (question.subtitle) {
				$('<h5>').text(question.subtitle).appendTo($group);
			}

			// create input elements, split by the "type" attribute

			// checkbox questions
			if (question.type === 'check') {
				question.options.forEach(function(option, i) {
					$('<div class="checkbox"><label><input type="checkbox" value="'
						+ i + '" name="' + question.name + '"></input>' + option +
						'</label></div>').appendTo($group);
				});

			// radio button questions
			} else if (question.type === 'radio') {
				question.options.forEach(function(option, i) {
					$('<div class="radio"><label><input type="radio" value="'
						+ i + '" name="' + question.name + '"></input>' +
						option + '</label></div>').appendTo($group);
				});

			// text input questions
			} else if (question.type === 'text') {
				$('<input>').attr({
					type: 'text',
					class: 'form-control',
					name: question.name,
					placeholder: $('<p>').html(question.placeholder).text() // to decode html entity
				}).appendTo($group);

			// table question: this is currently special cased
			// as requesting numbers in the table
			} else if (question.type === 'table') {
				var $table = $('<table class="table">');

				// construct the header column
				var header = '<th></th>';
				question.cols.forEach(function(col) {
					header += '<th'
					if (col.tooltip) {
						header += ' data-toggle="tooltip" data-placement="top" title="' + col['tooltip-text'] + '"'
					}
					header += '>' + col.text + '</th>';
				});
				$table.append('<tr>' + header + '</tr>');

				// for each row
				question.rows.forEach(function(row, i) {
					// the header entry on the far left
					var tr = '<th'
					if (row.tooltip) {
						tr += ' data-toggle="tooltip" data-placement="right" title="' + row['tooltip-text'] + '"'
					}
					tr += '>' + row.text + '</th>';

					question.cols.forEach(function(col, j) {
						tr += '<td><div class="input-group"><span class="input-group-addon">$</span>' + 
						'<input type="number" class="form-control" name="price' + i + j + '"' +
						'step="0.01", min="0"></input></div></td>';
					});
					$table.append('<tr>' + tr + '<tr>');
				});
				$table.appendTo($group);

				// initialize the inputs to have value 0
				$table.find('input').val(0);
			}

			// append the group to the build
			$group.appendTo('#licenseInfo');
		});
	});

	// append a submit button
	$('<button>').attr({
		type: 'submit',
		class: 'btn btn-default'
	}).text('Create').appendTo('#licenseInfo');

	// toggle all tooltips
	$('[data-toggle="tooltip"]').tooltip({
		container: 'body'
	});

	// listener on #set-fees-boolean 
	$('#set-fees-boolean').on('change', function(event) {
		// get whether to disable the matrix, and set the property
		var disable = $(this).find('input').prop('checked');
		$('#price-matrix input').prop('disabled', disable);

		// if disabling, also set all values to 0
		if (disable) {
			$('#price-matrix').find('input').val(0);
		}
	});
});