(function($) {
    "use strict";

    console.log('filter.js loaded, jQuery version:', $.fn.jquery);

    // Input number
    $('.input-number').each(function() {
        var $this = $(this),
            $input = $this.find('input[type="number"]'),
            up = $this.find('.qty-up'),
            down = $this.find('.qty-down');

        down.on('click', function() {
            console.log('Price down clicked');
            var value = parseInt($input.val()) - 1;
            value = value < 1 ? 1 : value;
            $input.val(value);
            $input.trigger('change');
        });

        up.on('click', function() {
            console.log('Price up clicked');
            var value = parseInt($input.val()) + 1;
            $input.val(value);
            $input.trigger('change');
        });
    });

    $(document).ready(function() {
        console.log('Document ready, initializing filters');
        // Initialize filters
        initializeFilters();

        // Add event listeners
        $('input[name="brand"]').on('change', function() {
            console.log('Brand filter changed:', $(this).val());
            applyFilters();
        });
        $('input[name^="attr_"]').on('change', function() {
            console.log('Attribute filter changed:', $(this).attr('name'), $(this).val());
            applyFilters();
        });
        $('#sort').on('change', function() {
            console.log('Sort changed:', $(this).val());
            applyFilters();
        });
        $('#filter-form').on('submit', function(e) {
            e.preventDefault();
            console.log('Filter form submitted');
            applyFilters();
        });
    });

    function initializeFilters() {
        console.log('Initializing filters');
        var urlParams = new URLSearchParams(window.location.search);

        // Set initial brand checkboxes
        var initialBrands = urlParams.getAll('brand');
        $('input[name="brand"]').each(function() {
            $(this).prop('checked', initialBrands.includes($(this).val()));
            console.log('Brand checkbox:', $(this).val(), $(this).prop('checked'));
        });

        // Set initial attribute checkboxes
        $('input[name^="attr_"]').each(function() {
            var attrName = $(this).attr('name');
            var initialValues = urlParams.getAll(attrName);
            $(this).prop('checked', initialValues.includes($(this).val()));
            console.log('Attribute checkbox:', attrName, $(this).val(), $(this).prop('checked'));
        });

        // Set initial price range
        var minPrice = urlParams.get('min_price') || $('#price-min').val();
        var maxPrice = urlParams.get('max_price') || $('#price-max').val();
        $('#price-min').val(minPrice);
        $('#price-max').val(maxPrice);
        console.log('Initial price range:', minPrice, maxPrice);

        // Set initial sort
        var sort = urlParams.get('sort') || 'default';
        $('#sort').val(sort);
        console.log('Initial sort:', sort);

        if (priceSlider && priceSlider.noUiSlider) {
            priceSlider.noUiSlider.set([minPrice, maxPrice]);
            console.log('Price slider set:', minPrice, maxPrice);
        } else {
            console.error('Price slider not found or not initialized');
        }
    }

    window.applyFilters = function() {
        console.log('applyFilters called');
        var searchParams = new URLSearchParams();

        // Handle brand selections
        $('input[name="brand"]:checked').each(function() {
            searchParams.append('brand', $(this).val());
        });

        // Handle attribute selections
        $('input[name^="attr_"]:checked').each(function() {
            searchParams.append($(this).attr('name'), $(this).val());
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
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(data) {
                console.log('AJAX success, updating product list');
                $('#product-list').html(data.product_list_html);
                $('.store-qty').text(`Showing ${data.product_count} products`);
                updateURL(searchParams);
                console.log('Filters applied successfully, data:', data);
            },
            error: function(error) {
                console.error('Error applying filters:', error);
            }
        });
    };

    function updateURL(searchParams) {
        console.log('Updating URL:', searchParams.toString());
        history.pushState(null, '', `${window.location.pathname}?${searchParams.toString()}`);
    }
})(jQuery);