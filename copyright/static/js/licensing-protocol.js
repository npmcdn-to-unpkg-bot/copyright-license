/* licensing-protocol.js
 * ---------------------
 * Event listeners for the licensing protocol form
 */

// ---------------------------------------------- initialization

// set the table inputs to 0
$('table input').val(0);

// toggle all tooltips
$('[data-toggle="tooltip"]').tooltip({
	container: 'body'
});

// ---------------------------------------------- listeners

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

// listener on #credit-format
$('#credit-format').on('change', function(event) {
	// show if either of the firt two options are checked
	var show = $(this).find('input').prop('checked') ||
		$($(this).find('input').get(1)).prop('checked');
	$('#credit-receiver').toggle(show);

	// if not showing, also empty the credit input
	if (!show) {
		$('#credit-receiver > input').val('');
	}
});

// when the form is submitted
$('#submit-btn').on('click', function(event) {
	$('[name]').forEach(function(elem) {
		console.log(elem);
	});
});