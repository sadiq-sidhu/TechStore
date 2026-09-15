// wishlist

$('.plus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    var em1 = (this.parentNode);
    console.log(em1)
    $.ajax({
        type:"GET",
        url:"/cart/pluswishlist/",
        data:{
            prod_id:id
        },
        success:function(data){
            console.log(id)
            window.location.assign(window.location.href);
        }
    })
})

$('.minus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    console.log(id)
    $.ajax({
        type:"GET",
        url:"/cart/minuswishlist/",
        data:{
            prod_id:id
        },
        
        success:function(data){
            console.log(id)
            window.location.assign(window.location.href);
        }
    })
})
