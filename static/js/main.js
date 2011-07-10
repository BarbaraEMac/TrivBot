function colourTitle () {
    var url = "" + window.location;
    var link;

    if ( url.indexOf( 'account' ) != -1 ) {
        link = document.getElementById( "account_img" );
    } else if ( url.indexOf( 'about' ) != -1 ) {
        link = document.getElementById( "about_img" );
    } else if ( (url.indexOf( 'question' ) != -1) || (url.indexOf( 'result' ) != -1) ) {
        link = document.getElementById( "question_img" );
    }

    /*
    if ( url.indexOf( 'account' ) != -1 ) {
        link = document.getElementById( "account_link" );
    } else if ( url.indexOf( 'about' ) != -1 ) {
        link = document.getElementById( "about_link" );
    } else if ( (url.indexOf( 'question' ) != -1) || (url.indexOf( 'result' ) != -1) ) {
        link = document.getElementById( "question_link" );
    }
    */
    
    if ( link ) {
        link.style.boxShadow = "3px 3px 4px #yellow";
    }
}

function foo( ) {
       $.ajax({
        url: "/logout", 
        type: "POST",
        data: ({ }),
        success: function(response) {
            self.location.reload(true);
        },
        error: function( response ) {
        }
    });
}

function invite( ) {
    var invite = document.getElementById( "invite" );

    $.ajax({
        url: "/invite", 
        type: "POST",
        data: ({ email: invite.value }),
        success: function(response) {
            document.getElementById( 'invite' ).value = "Email sent!";
            setTimeout("document.getElementById('invite').value=\"\"", 1500);
        },
        error: function( response ) {
            document.getElementById( 'invite' ).value = "Invalid email address";
            setTimeout("document.getElementById('invite').value=\"\"", 1500);
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

function clear_me( elem ) {
    if ( elem ) {
        elem.value = "";
    }
};
