/* licensing-protocol.js
 * ---------------------
 * Interface to get the licensing protocol questions
 * and generate the corresponding elements on the screen
 */

$.get('/licensing-protocol', function(response) {
	// delete the loading message
	$('#loading-message').remove();

	response.sections.forEach(function(section) {
		// make a new group object to be built up
		var $group = $('<div class="form-group">');

		// append the title of the section
		if (section.title) {
			$('<h3>').text(section.title).appendTo($group);
		}

		// for each question in the section
		section.questions.forEach(function(question) {
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
				question.options.forEach(function(option) {
					$('<div class="checkbox"><label><input type="checkbox" value="'
						+ option + '"></input>' + option + '</label></div>').appendTo($group);
				});

			// radio button questions
			} else if (question.type === 'radio') {
				question.options.forEach(function(option) {
					$('<div class="radio"><label><input type="radio" value="'
						+ option + '" name="' + question.id + '"></input>' +
						option + '</label></div>').appendTo($group);
				});

			// text input questions
			} else if (question.type === 'text') {
				$('<input>').attr({
					type: 'text',
					class: 'form-control',
					placeholder: question.placeholder
				}).appendTo($group);

			// table question: this is currently special cased
			// as requesting numbers in the table
			} else if (question.type === 'table') {
				var $table = $('<table class="table">');

				// construct the header column
				var header = '<th></th>';
				question.cols.forEach(function(col) {
					header += '<th>' + col + '</th>';
				});
				$table.append('<tr>' + header + '</tr>');

				// for each row
				question.rows.forEach(function(row) {
					// the header entry on the far left
					var row = '<th>' + row + '</th>';
					question.cols.forEach(function(col) {
						row += '<td><div class="input-group"><span class="input-group-addon">$</span>' + 
						'<input type="number" class="form-control"></input></div></td>';
					});
					$table.append('<tr>' + row + '<tr>');
				});
				$table.appendTo($group);

				// initialize the inputs to have value 0
				$table.find('input').val(0);
			}
		});

		// append the group to the build
		$group.appendTo('#licenseInfo');
	});

	// append a submit button
	$('<button>').attr({
		type: 'submit',
		class: 'btn btn-default'
	}).text('Create').appendTo('#licenseInfo');
});