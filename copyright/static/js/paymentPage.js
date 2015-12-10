window.onload = function() {

    $("#termsToggle").click(function() {
        $("#hiddenTerms").toggle();
    });

    $(".payment-input").on('change', function() {
        var cents = $(this).data('cents');
        var maxViews = $(this).data('views');
        $('#displayedAmount').text('Amount is ' + cents + ' cents');
        $('#amount').data('amount', cents);
        $('#maxViews').data('views', maxViews);
        $('#paymentButton').show();
    });

};
