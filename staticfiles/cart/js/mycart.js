$(document).ready(function(){
    // Prevent rapid clicks by disabling buttons during AJAX
    function toggleButtons($element, disable) {
        $element.closest('.cart-item').find('.plus-cart, .minus-cart, .remove-cart').prop('disabled', disable);
    }

    // Display message with auto-close
    function showMessage(message, type) {
        var $messages = $('.messages');
        if ($messages.length) {
            $messages.empty(); // Clear previous messages
            var $alert = $('<div class="alert alert-' + type + '" data-auto-close="4000">' + message + '<button type="button" class="close" data-dismiss="alert">&times;</button></div>');
            $messages.append($alert);
            setTimeout(function() {
                $alert.fadeOut(300, function() {
                    $(this).remove();
                });
            }, 4000);
        } else {
            console.warn('Messages div not found.');
            alert(message);
        }
    }

    // Update cart count and toggle empty cart
    function updateCartCount(count) {
        var $header = $('.card-header h5');
        if ($header.length) {
            $header.text('Cart - ' + count + ' items');
        } else {
            console.warn('Cart header not found.');
        }
        if (count === 0) {
            $('.card.mb-4').hide();
            $('.col-md-4 .card.mb-4').hide();
            $('.col-md-8').html(
                '<p>Your cart is empty.</p>' +
                '<a href="' + window.homeUrl + '" style="color: #D10024; text-transform: uppercase; font-weight: 500;">' +
                '<i class="fa fa-long-arrow-left me-2"></i>Back to Shop</a>'
            );
        }
    }

    // Render summary with per-product subtotals
    function updateSummary(data) {
        var $summaryList = $('#summary-list');
        var $amount = $('#amount');
        var $total = $('#total');
        if (!$summaryList.length) {
            console.error('Summary list not found.');
            return;
        }
        if (!$amount.length || !$total.length) {
            console.error('Amount or Total element not found. Amount:', $amount.length, 'Total:', $total.length);
            showMessage('Page error: Required elements missing.', 'error');
            return;
        }
        $summaryList.empty();
        if (data.subtotals && data.subtotals.length > 0) {
            $.each(data.subtotals, function(index, item) {
                $summaryList.append(
                    '<li style="display: flex; justify-content: space-between; padding: 10px 0;">' +
                    '<span>' + item.product_name + ' (' + item.quantity + ' units)</span>' +
                    '<span>₹' + item.subtotal.toFixed(2) + '</span>' +
                    '</li>'
                );
            });
            $amount.text('₹' + (data.amount || 0).toFixed(2));
            $total.text('₹' + (data.total || 0).toFixed(2));
        } else {
            $summaryList.append(
                '<li style="display: flex; justify-content: space-between; padding: 10px 0;">' +
                '<span>No products</span>' +
                '<span>₹0.00</span>' +
                '</li>'
            );
            $amount.text('₹0.00');
            $total.text('₹0.00');
        }
    }

    $('.plus-cart').click(function(){
        var id = $(this).attr("pid").toString();
        var $input = $(this).closest('.input-number').find('input');
        var $button = $(this);
        var $amount = $('#amount');
        var $total = $('#total');
        console.log('Plus Cart - Input:', $input.length, 'Amount:', $amount.length, 'Total:', $total.length);
        if (!$input.length || !$amount.length || !$total.length) {
            console.error('Elements not found. Input:', $input.length, 'Amount:', $amount.length, 'Total:', $total.length);
            showMessage('Page error: Required elements missing.', 'error');
            return;
        }
        toggleButtons($button, true);
        console.log('Plus Cart:', id);
        $.ajax({
            type: 'GET',
            url: '/cart/pluscart/',
            data: { prod_id: id },
            success: function(data) {
                console.log('Plus Cart Response:', data);
                if (data.error) {
                    showMessage(data.error, 'error');
                } else if (data.quantity) {
                    $input.val(data.quantity);
                    updateSummary(data);
                    updateCartCount(data.count);
                }
                toggleButtons($button, false);
            },
            error: function(xhr) {
                console.error('Plus Cart Error:', xhr.responseJSON ? xhr.responseJSON.error : xhr.statusText);
                var errorMsg = xhr.responseJSON ? xhr.responseJSON.error : 'Error updating cart.';
                showMessage(errorMsg, 'error');
                toggleButtons($button, false);
            }
        });
    });

    $('.minus-cart').click(function(){
        var id = $(this).attr("pid").toString();
        var $input = $(this).closest('.input-number').find('input');
        var $row = $(this).closest('.cart-item');
        var $button = $(this);
        var $amount = $('#amount');
        var $total = $('#total');
        console.log('Minus Cart - Input:', $input.length, 'Amount:', $amount.length, 'Total:', $total.length);
        if (!$input.length || !$amount.length || !$total.length) {
            console.error('Elements not found. Input:', $input.length, 'Amount:', $amount.length, 'Total:', $total.length);
            showMessage('Page error: Required elements missing.', 'error');
            return;
        }
        toggleButtons($button, true);
        console.log('Minus Cart:', id);
        $.ajax({
            type: 'GET',
            url: '/cart/minuscart/',
            data: { prod_id: id },
            success: function(data) {
                console.log('Minus Cart Response:', data);
                if (data.error) {
                    showMessage(data.error, 'error');
                } else if (data.quantity === 0) {
                    $row.remove();
                } else {
                    $input.val(data.quantity);
                }
                updateCartCount(data.count);
                updateSummary(data);
                toggleButtons($button, false);
            },
            error: function(xhr) {
                console.error('Minus Cart Error:', xhr.responseJSON ? xhr.responseJSON.error : xhr.statusText);
                var errorMsg = xhr.responseJSON ? xhr.responseJSON.error : 'Error updating cart.';
                showMessage(errorMsg, 'error');
                toggleButtons($button, false);
            }
        });
    });

    $('.remove-cart').click(function(){
        var id = $(this).attr("pid").toString();
        var $row = $(this).closest('.cart-item');
        var $button = $(this);
        var $amount = $('#amount');
        var $total = $('#total');
        console.log('Remove Cart - Amount:', $amount.length, 'Total:', $total.length);
        if (!$amount.length || !$total.length) {
            console.error('Amount or Total element not found. Amount:', $amount.length, 'Total:', $total.length);
            showMessage('Page error: Amount or Total element missing.', 'error');
            toggleButtons($button, false);
            return;
        }
        toggleButtons($button, true);
        console.log('Remove Cart:', id);
        $.ajax({
            type: 'GET',
            url: '/cart/removecart/',
            data: { prod_id: id },
            success: function(data) {
                console.log('Remove Cart Response:', data);
                $row.remove();
                updateCartCount(data.count);
                updateSummary(data);
                if (data.message) {
                    showMessage(data.message, 'success');
                }
                toggleButtons($button, false);
            },
            error: function(xhr) {
                console.error('Remove Cart Error:', xhr.responseJSON ? xhr.responseJSON.error : xhr.statusText);
                var errorMsg = xhr.responseJSON ? xhr.responseJSON.error : 'Error removing item.';
                showMessage(errorMsg, 'error');
                toggleButtons($button, false);
            }
        });
    });

    // Close button functionality for AJAX messages
    $(document).on('click', '.messages .close', function() {
        $(this).parent().remove();
    });
});