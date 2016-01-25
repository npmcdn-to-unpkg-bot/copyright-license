/* index.js
 * --------
 * Javascript file for the index page
 * - Remove images that don't load
 * - Apply masonry image layout
 */

// call the masonry function to present an image collage
$(function() {
	// cache the masonry wrapper
	var $wrapper = $('.masonry-wrapper');

	// upon the images loading, apply the masonry layout
	$wrapper.imagesLoaded()
		// for each image
		.progress(function(instance, image) {
			// if an image does not load, delete the image 
			if (!image.isLoaded) {
				$(image.img).remove();
			}
		})
		// after the non-loading images have been removed
		.always(function() {
			// apply the masonry layout
			$wrapper.masonry({
				columnWidth: 60,
				gutter: 5,
				itemSelector: '.masonry-image'
			});
		});
});
