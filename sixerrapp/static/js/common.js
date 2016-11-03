$( document ).ready(function() {
    console.log( "ready!" );
    //var prises = document.querySelectorAll('[id^=price]')
    var gig_home_page = $('#gig_home_page');
    console.log(gig_home_page.length);
    var size = document.querySelectorAll('[class^=green]').length;
    for ( var i = 1; i <= size; i++ ){
    	console.log("Hey, Mom ------ ");
    	var counter = i;
    	var price_id = "price-"+counter.toString();
    	var price = document.getElementById(price_id).innerHTML;
    	var number = price.replace( /^\D+/g, '');
    	if (number < 20) {
    		document.getElementById(price_id).style.color = "red";
    	}    	
	}
});