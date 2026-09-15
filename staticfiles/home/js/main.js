(function($) {
	"use strict"

	// Mobile Nav toggle
	$('.menu-toggle > a').on('click', function (e) {
		e.preventDefault();
		$('#responsive-nav').toggleClass('active');
	})

	// Fix cart dropdown from closing
	$('.cart-dropdown').on('click', function (e) {
		e.stopPropagation();
	});

	/////////////////////////////////////////

	// Products Slick
	$('.products-slick').each(function() {
		var $this = $(this),
				$nav = $this.attr('data-nav');

		$this.slick({
			slidesToShow: 4,
			slidesToScroll: 1,
			autoplay: true,
			infinite: true,
			speed: 300,
			dots: false,
			arrows: true,
			appendArrows: $nav ? $nav : false,
			responsive: [{
	        breakpoint: 991,
	        settings: {
	          slidesToShow: 2,
	          slidesToScroll: 1,
	        }
	      },
	      {
	        breakpoint: 480,
	        settings: {
	          slidesToShow: 1,
	          slidesToScroll: 1,
	        }
	      },
	    ]
		});
	});

	// Products Widget Slick
	$('.products-widget-slick').each(function() {
		var $this = $(this),
				$nav = $this.attr('data-nav');

		$this.slick({
			infinite: true,
			autoplay: true,
			speed: 300,
			dots: false,
			arrows: true,
			appendArrows: $nav ? $nav : false,
		});
	});

	/////////////////////////////////////////

	// Product Main img Slick
	$('#product-main-img').slick({
    infinite: true,
    speed: 300,
    dots: false,
    arrows: true,
    fade: true,
    asNavFor: '#product-imgs',
  });

	// Product imgs Slick
  $('#product-imgs').slick({
    slidesToShow: 3,
    slidesToScroll: 1,
    arrows: true,
    centerMode: true,
    focusOnSelect: true,
		centerPadding: 0,
		vertical: true,
    asNavFor: '#product-main-img',
		responsive: [{
        breakpoint: 991,
        settings: {
					vertical: false,
					arrows: false,
					dots: true,
        }
      },
    ]
  });

	// Product img zoom
	var zoomMainProduct = document.getElementById('product-main-img');
	if (zoomMainProduct) {
		$('#product-main-img .product-preview').zoom();
	}

	/////////////////////////////////////////

		"use strict"
	
		// Mobile Nav toggle
		$('.menu-toggle > a').on('click', function (e) {
			e.preventDefault();
			$('#responsive-nav').toggleClass('active');
		})
	
		// Fix cart dropdown from closing
		$('.cart-dropdown').on('click', function (e) {
			e.stopPropagation();
		});
	
		/////////////////////////////////////////
	
		// Products Slick
		$('.products-slick').each(function() {
			var $this = $(this),
					$nav = $this.attr('data-nav');
	
			$this.slick({
				slidesToShow: 4,
				slidesToScroll: 1,
				autoplay: true,
				infinite: true,
				speed: 300,
				dots: false,
				arrows: true,
				appendArrows: $nav ? $nav : false,
				responsive: [{
				breakpoint: 991,
				settings: {
				  slidesToShow: 2,
				  slidesToScroll: 1,
				}
			  },
			  {
				breakpoint: 480,
				settings: {
				  slidesToShow: 1,
				  slidesToScroll: 1,
				}
			  },
			]
			});
		});
	
		// Products Widget Slick
		$('.products-widget-slick').each(function() {
			var $this = $(this),
					$nav = $this.attr('data-nav');
	
			$this.slick({
				infinite: true,
				autoplay: true,
				speed: 300,
				dots: false,
				arrows: true,
				appendArrows: $nav ? $nav : false,
			});
		});
	
		/////////////////////////////////////////
	
		// // Input number
		// $('.input-number').each(function() {
		// 	var $this = $(this),
		// 		$input = $this.find('input[type="number"]'),
		// 		up = $this.find('.qty-up'),
		// 		down = $this.find('.qty-down');
	
		// 	down.on('click', function() {
		// 		var value = parseInt($input.val()) - 1;
		// 		value = value < 1 ? 1 : value;
		// 		$input.val(value);
		// 		$input.change();
		// 		updatePriceSlider($this, value);
		// 	});
	
		// 	up.on('click', function() {
		// 		var value = parseInt($input.val()) + 1;
		// 		$input.val(value);
		// 		$input.change();
		// 		updatePriceSlider($this, value);
		// 	});
		// });
	
		// var priceInputMax = document.getElementById('price-max'),
		// 	priceInputMin = document.getElementById('price-min');
	
		// priceInputMax.addEventListener('change', function() {
		// 	updatePriceSlider($(this).parent(), this.value);
		// });
	
		// priceInputMin.addEventListener('change', function() {
		// 	updatePriceSlider($(this).parent(), this.value);
		// });
	
		// function updatePriceSlider(elem, value) {
		// 	if (elem.hasClass('price-min')) {
		// 		priceSlider.noUiSlider.set([value, null]);
		// 	} else if (elem.hasClass('price-max')) {
		// 		priceSlider.noUiSlider.set([null, value]);
		// 	}
		// }
	
		// // Price Slider
		// var priceSlider = document.getElementById('price-slider');
		// if (priceSlider) {
		// 	noUiSlider.create(priceSlider, {
		// 		start: [1, 200000],
		// 		connect: true,
		// 		step: 1,
		// 		range: {
		// 			'min': 1,
		// 			'max': 200000
		// 		}
		// 	});
	
		// 	priceSlider.noUiSlider.on('update', function(values, handle) {
		// 		var value = values[handle];
		// 		handle ? priceInputMax.value = Math.round(value) : priceInputMin.value = Math.round(value);
		// 	});
	
		// 	priceSlider.noUiSlider.on('change', applyFilters);
		// }
	
		// $(document).ready(function() {
		// 	// Initialize price slider
		// 	if (priceSlider) {
		// 		noUiSlider.create(priceSlider, {
		// 			start: [1, 200000],
		// 			connect: true,
		// 			step: 1,
		// 			range: {
		// 				'min': 1,
		// 				'max': 200000
		// 			}
		// 		});
	
		// 		priceSlider.noUiSlider.on('update', function(values, handle) {
		// 			var value = values[handle];
		// 			if (handle === 0) {
		// 				$('#price-min').val(Math.round(value));
		// 			} else {
		// 				$('#price-max').val(Math.round(value));
		// 			}
		// 		});
	
		// 		priceSlider.noUiSlider.on('change', applyFilters);
		// 	}
	
		// 	// Initialize filters
		// 	initializeFilters();
	
		// 	// Add event listeners
		// 	$('input[name="brand"]').on('change', applyFilters);
		// 	$('#price-min, #price-max').on('change', applyFilters);
		// 	$('#sort').on('change', applyFilters);
		// 	$('#filter-form').on('submit', function(e) {
		// 		e.preventDefault();
		// 		applyFilters();
		// 	});
		// });
	
		// function initializeFilters() {
		// 	var urlParams = new URLSearchParams(window.location.search);
	
		// 	// Set initial brand checkboxes
		// 	var initialBrands = urlParams.getAll('brand');
		// 	$('input[name="brand"]').each(function() {
		// 		$(this).prop('checked', initialBrands.includes($(this).val()));
		// 	});
	
		// 	// Set initial price range
		// 	var minPrice = urlParams.get('min_price') || $('#price-min').val() || 1;
		// 	var maxPrice = urlParams.get('max_price') || $('#price-max').val() || 200000;
		// 	$('#price-min').val(minPrice);
		// 	$('#price-max').val(maxPrice);
	
		// 	// Set initial sort
		// 	var sort = urlParams.get('sort') || 'default';
		// 	$('#sort').val(sort);
	
		// 	if (priceSlider && priceSlider.noUiSlider) {
		// 		priceSlider.noUiSlider.set([minPrice, maxPrice]);
		// 	}
		// }
	
		// function applyFilters() {
		// 	var searchParams = new URLSearchParams();
	
		// 	// Handle brand selections
		// 	$('input[name="brand"]:checked').each(function() {
		// 		searchParams.append('brand', $(this).val());
		// 	});
	
		// 	// Handle price range
		// 	var minPrice = $('#price-min').val();
		// 	var maxPrice = $('#price-max').val();
		// 	searchParams.set('min_price', minPrice);
		// 	searchParams.set('max_price', maxPrice);
	
		// 	// Handle sort
		// 	var sort = $('#sort').val();
		// 	searchParams.set('sort', sort);
	
		// 	$.ajax({
		// 		url: window.location.pathname,
		// 		method: 'GET',
		// 		data: searchParams.toString(),
		// 		headers: {
		// 			'X-Requested-With': 'XMLHttpRequest'
		// 		},
		// 		success: function(data) {
		// 			$('#product-list').html(data.product_list_html);
		// 			$('#product-count').text(data.product_count);
		// 			updateURL(searchParams);
		// 		},
		// 		error: function(error) {
		// 			console.error('Error applying filters:', error);
		// 		}
		// 	});
		// }
	
		// function updateURL(searchParams) {
		// 	history.pushState(null, '', `${window.location.pathname}?${searchParams.toString()}`);
		// }
})(jQuery);