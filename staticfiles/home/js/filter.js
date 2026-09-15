(function($) {
    "use strict";

    // Input number
    $('.input-number').each(function() {
        var $this = $(this),
            $input = $this.find('input[type="number"]'),
            up = $this.find('.qty-up'),
            down = $this.find('.qty-down');

        down.on('click', function() {
            var value = parseInt($input.val()) - 1;
            value = value < 1 ? 1 : value;
            $input.val(value);
            $input.change();
            updatePriceSlider($this, value);
        });

        up.on('click', function() {
            var value = parseInt($input.val()) + 1;
            $input.val(value);
            $input.change();
            updatePriceSlider($this, value);
        });
    });

    var priceInputMax = document.getElementById('price-max'),
        priceInputMin = document.getElementById('price-min');

    priceInputMax.addEventListener('change', function() {
        updatePriceSlider($(this).parent(), this.value);
    });

    priceInputMin.addEventListener('change', function() {
        updatePriceSlider($(this).parent(), this.value);
    });

    function updatePriceSlider(elem, value) {
        if (elem.hasClass('price-min')) {
            priceSlider.noUiSlider.set([value, null]);
        } else if (elem.hasClass('price-max')) {
            priceSlider.noUiSlider.set([null, value]);
        }
    }

    // Price Slider
    var priceSlider = document.getElementById('price-slider');
    if (priceSlider) {
        noUiSlider.create(priceSlider, {
            start: [1, 200000],
            connect: true,
            step: 1,
            range: {
                'min': 1,
                'max': 200000
            }
        });

        priceSlider.noUiSlider.on('update', function(values, handle) {
            var value = values[handle];
            console.log('Price slider updated:', values);
            handle ? priceInputMax.value = Math.round(value) : priceInputMin.value = Math.round(value);
        });

        priceSlider.noUiSlider.on('change', function() {
            console.log('Price slider changed');
            applyFilters();
        });
    }

    $(document).ready(function() {
        // Initialize filters
        initializeFilters();

        // Add event listeners
        $('input[name="brand"]').on('change', function() {
            console.log('Checkbox changed:', this.value, this.checked);
            applyFilters();
        });
        $('#price-min, #price-max').on('change', applyFilters);
        $('#sort').on('change', applyFilters);
        $('#filter-form').on('submit', function(e) {
            e.preventDefault();
            console.log('Filter form submitted');
            applyFilters();
        });
    });

    function initializeFilters() {
        var urlParams = new URLSearchParams(window.location.search);

        // Set initial brand checkboxes
        var initialBrands = urlParams.getAll('brand');
        $('input[name="brand"]').each(function() {
            $(this).prop('checked', initialBrands.includes($(this).val()));
        });

        // Set initial price range
        var minPrice = urlParams.get('min_price') || $('#price-min').val() || 1;
        var maxPrice = urlParams.get('max_price') || $('#price-max').val() || 200000;
        $('#price-min').val(minPrice);
        $('#price-max').val(maxPrice);

        // Set initial sort
        var sort = urlParams.get('sort') || 'default';
        $('#sort').val(sort);

        if (priceSlider && priceSlider.noUiSlider) {
            priceSlider.noUiSlider.set([minPrice, maxPrice]);
        }
    }

    window.applyFilters = function() {
        var searchParams = new URLSearchParams();

        // Handle brand selections
        $('input[name="brand"]:checked').each(function() {
            searchParams.append('brand', $(this).val());
        });

        // Handle price range
        var minPrice = $('#price-min').val();
        var maxPrice = $('#price-max').val();
        searchParams.set('min_price', minPrice);
        searchParams.set('max_price', maxPrice);

        // Handle sort
        var sort = $('#sort').val();
        searchParams.set('sort', sort);

        console.log('Applying filters:', searchParams.toString());

        $.ajax({
            url: window.location.pathname,
            method: 'GET',
            data: searchParams.toString(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                $('#product-list').html(data.product_list_html);
                $('#product-count').text(data.product_count);
                updateURL(searchParams);
                console.log('Filters applied successfully');
                console.log('Received data:', data);
            },
            error: function(error) {
                console.error('Error applying filters:', error);
            }
        });
    };

    function updateURL(searchParams) {
        history.pushState(null, '', `${window.location.pathname}?${searchParams.toString()}`);
    }
})(jQuery);