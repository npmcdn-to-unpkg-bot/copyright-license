window.onload = function() {

    $("#termsToggle").click(function() {
        $("hiddenTerms").toggle();
    });

    $(".payment-input").on('selected', function() {
        var cents = $(this).attr('data-cents');
        console.log('SELECTED ' + cents);
        $('#displayedAmount').text('Amount is ' + cents + ' cents');
        $('#stripeButton').attr('data-amount', cents);   //IS THIS HOW TO GET DATA
    });

};
