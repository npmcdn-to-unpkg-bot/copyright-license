window.onload = function() {
    $(".payment-input").on('change', function() {
        var price = $('#price_base').data('cents');

        input_names = ['is_commercial', 'is_derivative'];
        for (var i=0; i<input_names.length; i++) {
            input_name = input_names[i];
            input = $('input[name="' + input_name + '"]:checked');
            input_val = input.val();
            if (input_val == 'True') {
                price += parseInt(input.data('cents'));
            }
        }
        
        $('#displayCost').text(price);
        $('#displayCost').data('cents', price);
    });
};

$('#toggleTerms').on('click', function(e) {
    $('.terms-list').toggle();
});