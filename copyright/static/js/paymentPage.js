window.onload = function() {

    $("#hiddenTerms").hide();

    $("#termsToggle").click(function() {
        $("#hiddenTerms").toggle();
    });

    $(".payment-input").on('change', function() {
        var cents = $(this).data('cents');
        var maxViews = $(this).data('views');
        $('#displayAmount').text('Amount is ' + cents + ' cents');
        $('#displayAmountWrapper').removeClass("hidden");
        $('#amount').data('amount', cents);
        $('#maxViews').data('views', maxViews);
    });

};
