/* index.js
 * --------
 * Javascript file for the index page
 * Current functionality:
 *   - Set image size text
 */

// select all images, and upon loading
$('.image-block>img').one('load', function() {
	// get the original size of the image in the form 'width x height'
	var text = this.naturalWidth + ' x ' + this.naturalHeight;

	// set the image size span text, based on current html structure
	$(this).parents('.block').find('span.image-size').text(text);
}).each(function() {
	// if the load is complete, trigger the load event
	if (this.complete) {
		$(this).load();
	}
});
