$(function() {
    $('#btnSignUp').click(function() {
 
        $.ajax({
            url: '/signUp',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log('response: '+response);
                alert(response);
            },
            error: function(error) {
                console.log(error);
                alert(error);
            }
        });
    });
});
