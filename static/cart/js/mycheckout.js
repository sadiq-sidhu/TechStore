function submitNewAddress(){
    // var name=$('#name').val();
    // var phone=$('#tel').val();
    // var addressType=$('#type').val();
    // var locality=$('#locality').val();
    // var city=$('#city').val();
    // var state=$('#state').val();
    // var zip=$('#zip-code').val();

    var formData = {
        'name': $('#name').val(),
        'phone': $('#tel').val(),
        'address_type': $('#type').val(),
        'locality': $('#locality').val(),
        'city': $('#city').val(),
        'state': $('#state').val(),
        'zip': $('#zip-code').val(),
        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };
    
    // console.log('Name:', name);
    // console.log('Phone:', phone);
    // console.log('Address Type:', addressType);
    // console.log('Locality:', locality);
    // console.log('City:', city);
    // console.log('State:', state);
    // console.log('ZIP Code:', zip);

    $.ajax({
        type:'POST',
        url:'/cart/save_address/',
        data: formData,
    
        success: function(data){
            console.log('AJAX Success:', data);
            if (data.status === 'success'){
                alert(data.message);
                location.reload();
            } else {
                alert(data.message);
            }
        },
        error: function(error){
            console.error('AJAX error;',error)
            alert("Eroor adding address.");
        }
    });
}


// const applyCouponUrl = "{% url 'apply_coupon' %}";  // Django resolves this URL here
// const removeCouponUrl= '{% url "remove_coupon" %}';
// console.log("Script loaded");
// document.getElementById('apply_coupon_button').addEventListener('click', function(event) {
//     console.log("Apply coupon button clicked"); 
//     event.preventDefault();  

//     const couponCodeInput = document.getElementById('coupon_code');
//     const couponCode = couponCodeInput.value;

//     console.log("Coupon code:", couponCode);  
//     fetch(applyCouponUrl, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': '{{ csrf_token }}'
//         },
//         body: JSON.stringify({ code: couponCode })
//     })
//     .then(response => {
//         console.log("Received response");  // Debug message
//         return response.json();
//     })
//     .then(data => {
//         console.log("Response data:", data);  // Debug message
//         const messageDiv = document.getElementById('coupon_message');
//         const discountDiv = document.getElementById('discount_display');
//         const totalAmountDisplay = document.getElementById('total_amount');
//         const applyButton = document.getElementById('apply_coupon_button');
//         const removeButton = document.getElementById('remove_coupon_button');

//         if (data.success) {
//             messageDiv.textContent = 'Coupon applied successfully!';
//             discountDiv.textContent = `Discount: $${data.discount_amount}`;
//             totalAmountDisplay.textContent = `After applying coupon: $${data.final_total}`;

//             applyButton.disabled = true;
//             applyButton.style.backgroundColor = 'gray';
//             couponCodeInput.placeholder = couponCode;
//             couponCodeInput.value = '';
//             couponCodeInput.readOnly = true;

//             removeButton.style.display = 'inline-block';
//         } else {
//             messageDiv.textContent = data.error;
//             discountDiv.textContent = '';
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// });


// // Event listener for removing the coupon
// document.getElementById('remove_coupon_button').addEventListener('click', function() {
//     const couponCodeInput = document.getElementById('coupon_code');
//     const messageDiv = document.getElementById('coupon_message');
//     const discountDiv = document.getElementById('discount_display');
//     const totalAmountDisplay = document.getElementById('total_amount');
//     const applyButton = document.getElementById('apply_coupon_button');
//     const removeButton = document.getElementById('remove_coupon_button');

//     // Reset the discount and message areas
//     messageDiv.textContent = '';
//     discountDiv.textContent = '';
//     totalAmountDisplay.textContent = `Total Amount: ${{ total_amount }}`;  // Reset to original total

//     // Enable the apply button and reset styles
//     applyButton.disabled = false;
//     applyButton.style.backgroundColor = '';  // Reset button color
//     couponCodeInput.placeholder = 'Enter coupon code';  // Reset placeholder
//     couponCodeInput.readOnly = false;  // Make input editable

//     // Hide the remove button
//     removeButton.style.display = 'none';

//     // Clear session discount on the server side
//     fetch(removeCouponUrl, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': '{{ csrf_token }}'
//         }
//     }).then(response => response.json())
//       .then(data => {
//           if (data.success) {
//               console.log('Coupon removed successfully');
//           }
//       });
// });
