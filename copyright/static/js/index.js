/* index.js
 * --------
 * Javascript file for the index page
 * - Remove images that don't load
 * - Apply masonry image layout
 */

$(function() {
	// -------------------------------- MASONRY
	function applyMasonry(isInitial) {
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
				// destroy any previous masonry object
				if (!isInitial) {
					$wrapper.masonry('destroy');
				}

				// apply the masonry layout
				$wrapper.masonry({
					columnWidth: 120,
					gutter: 5,
					itemSelector: '.masonry-image'
				});
			});
	}

	// -------------------------------- PAGINATION
	// helper function to set the current page
	function setPage(i, isInitial) {
		// clear the current active pagination
		clearPaginationActive();

		// cache the relevant pagination tab jQuery object
		var $tab = $($('ul.pagination>li').get(i));

		// set the tab to active
		$tab.addClass('active');

		// append the screen reader note
		$('<span>')
			.addClass('sr-only')
			.text(' (current)')
			.appendTo($tab.children('a'));

		// set the pagination disables as needed
		setPaginationDisabled(i);

		// if not the initial call to set the page
		if (!isInitial) {
			// get the new page with an AJAX call
			$.get('/page?page=' + i, function(response) {
				// remove the previous images
				$('.masonry-wrapper>a').remove();

				// add each of the new images to the DOM
				$.each(response.result, function(index, license) {
					$('.masonry-wrapper')
						.append('<a class="masonry-image" href="/purchase/' + license.id + '">' +
							'<img src="' + license.url + '"></a>');
				});

				applyMasonry(false);
			});
		}
	}

	// helper function to clear all active pagination tabs
	function clearPaginationActive() {
		// cache tabs, remove active, remove span.sr-only
		var $paginationTabs = $('ul.pagination>li');
		$paginationTabs.removeClass('active');
		$paginationTabs.find('span.sr-only').remove();
	}

	// helper function to set the next or previous tabs to disabled if needed
	function setPaginationDisabled(i) {
		var $pagination = $('ul.pagination');
		var $tabs = $pagination.children('li');

		// clear all previous disabled
		$pagination.children('.disabled').removeClass('disabled');

		// set .disabled to the 'next' and 'previous' tabs as needed
		var numTabs = $tabs.length;
		if (i === 1) {
			$($tabs.get(0)).addClass('disabled');
		}

		if (i === numTabs - 2) {
			$($tabs.get(numTabs - 1)).addClass('disabled');
		}
	}

	// click listener for the pagination tabs
	$('ul.pagination').on('click', 'li', function(event) {
		// prevent default to not add '#' to the url
		event.preventDefault();

		var previousPage = page;
		var numTabs = $('ul.pagination>li').length;
		var index = $(this).index();

		if (index === 0) {
			if (page > 1) {
				page--;
			}
		} else if (index === numTabs - 1) {
			if (page < numTabs - 2) {
				page++;
			}
		} else {
			page = index;
		}

		// only set the page if it has changed
		if (previousPage !== page) {
			setPage(page);
		}
	});

	// -------------------------------- INITIALIZATION
	// initialize to page one
	var page = 1;

	// set the page and apply masonry with the isInitial flag true
	setPage(page, true);
	applyMasonry(true);
});
