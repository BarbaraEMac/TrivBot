function colourTitle () {
    var url = "" + window.location;
    var link;

    if ( url.indexOf( 'account' ) != -1 ) {
        link = document.getElementById( "account_img" );
    } else if ( url.indexOf( 'about' ) != -1 ) {
        link = document.getElementById( "about_img" );
    } else if ( (url.indexOf( 'question' ) != -1) || (url.indexOf( 'willet' ) != -1) || (url.indexOf( 'result' ) != -1) ) {
        link = document.getElementById( "question_img" );
    }
    
    if ( link ) {
        link.style.boxShadow = "3px 3px 4px yellow";
    }
}

function invite( ) {
    var invite = document.getElementById( "invite" );

    $.ajax({
        url: "/invite", 
        type: "POST",
        data: ({ email: invite.value }),
        success: function(response) {
            document.getElementById( 'invite' ).value = "Email sent!";
            setTimeout("document.getElementById('invite').value=\" \"", 1500);
        },
        error: function( response ) {
            document.getElementById( 'invite' ).value = "Invalid email address";
            setTimeout("document.getElementById('invite').value=\" \"", 1500);
        }
    });
}

function submitFeedback( ) {
    var feedback = document.getElementById( "feedback" );

    $.ajax({
        url: "/submitFeedback", 
        type: "POST",
        data: ({ 'feedback': feedback.value }),
        success: function(response) {
            document.getElementById( 'feedback' ).innerHTML = "Thanks!";
            document.getElementById( 'feedback' ).value     = "Thanks!";
            setTimeout( "document.getElementById('feedback').value=\"\"", 1500 );
        },
        failure: function(response) {
        }
    });
}


function maybeSubmit (field, e) {
    var keycode;
    if (window.event) keycode = window.event.keyCode;
    else if (e) keycode = e.which;
    else return true;

    if (keycode == 13)
   {
       invite();
       return false;
   }
    else
       return true;
}
