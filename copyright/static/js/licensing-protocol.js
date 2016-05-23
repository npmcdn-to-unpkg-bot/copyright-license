/* licensing-protocol.js
 * ---------------------
 * Event listeners for the licensing protocol form
 */

// ---------------------------------------------- initialization

// hide the "how do you want to be credited?" question for now
$('#credit_type-wrapper').toggle(false);

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
	$('[name]').each(function(elem) {
		console.log(elem);
	});
});

// listener for whether to show the credit type question,
// where 1 is the value for showing and 2 is value for hiding
$('#credit-wrapper').on('click', 'input', function(event) {
	$('#credit_type-wrapper').toggle($(this).val() === '1');
});
