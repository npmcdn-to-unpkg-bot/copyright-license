/* licensing-protocol.js
 * ---------------------
 * Interface to get the licensing protocol questions
 */

// cache the jQuery object for the licensing-protocol div
var $lp = $('#licensing-protocol');

$.get('/licensing-protocol', function(response) {
	var $form = $('<form>').appendTo($lp);

	response.sections.forEach(function(section) {
		var $group = $('<div class="form-group">');

		if (section.title) {
			$('<h3>').text(section.title).appendTo($group);
		}
		section.questions.forEach(function(question) {
			if (question.title) {
				$('<h4>').text(question.title).appendTo($group);
			}
			if (question.subtitle) {
				$('<h5>').text(question.subtitle).appendTo($group);
			}

			if (question.type === 'check') {
				var $form = $('form')
				question.options.forEach(function(option) {
					$('<div class="checkbox"><label><input type="checkbox" value="'
						+ option + '"></input>' + option + '</label></div>').appendTo($group);
				});
			} else if (question.type === 'radio') {
				question.options.forEach(function(option) {
					$('<div class="radio"><label><input type="radio" value="'
						+ option + '" name="' + question.id + '"></input>' +
						option + '</label></div>').appendTo($group);
				});
			} else if (question.type === 'text') {
				$('<input>').attr({
					type: 'text',
					class: 'form-control',
					placeholder: question.placeholder
				}).appendTo($group);
			} else if (question.type === 'table') {
				var $table = $('<table class="table">');
				var header = '<th></th>';

				question.cols.forEach(function(col) {
					header += '<th>' + col + '</th>';
				});
				$table.append('<tr>' + header + '</tr>');

				question.rows.forEach(function(row) {
					var row = '<th>' + row + '</th>';
					question.cols.forEach(function(col) {
						row += '<td><div class="input-group"><span class="input-group-addon">$</span>' + 
						'<input type="number" class="form-control"></input></div></td>';
					});
					$table.append('<tr>' + row + '<tr>');
				});
				$table.appendTo($group);
				$table.find('input').val(0);
			} else {
				console.log(question.type);
			}
		});

		$group.appendTo($lp);
	});
});