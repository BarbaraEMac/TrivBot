function updateAccount( first_account ) {
    var first_name  = document.getElementById( "first_name" );
    var last_name   = document.getElementById( "last_name" );
    var email       = document.getElementById( "email" );
    var troupe      = document.getElementById( "troupe_1" );
    var daily_email = "first";
    var new_troupe  = "Everyone";

    if ( !first_account ) {
        daily_email = document.getElementById( "daily_email" ).value;
    } 
    if ( troupe ) {
        new_troupe = troupe.value;
    }

    $.ajax({
        url: "/updateAccount", 
        type: "POST",
        data: ({first_name  : first_name.value,
                last_name   : last_name.value,
                email       : email.value,
                daily_email : daily_email,
                troupe      : new_troupe }),
        success: function(response) {
            self.location.reload(true);
        },
        error: function( response ) {
            if ( response.status == 400 ) {
                document.getElementById( 'first_name' ).value = "Invalid first name";
                setTimeout("document.getElementById('first_name').value=\"\"", 1500);
            } else if ( response.status == 401 ) {
                document.getElementById( 'last_name' ).value = "Invalid last name";
                setTimeout("document.getElementById('last_name').value=\"\"", 1500);
            } else if ( response.status == 402 ){
                document.getElementById( 'email' ).value = "Invalid email address";
                setTimeout("document.getElementById('email').value=\"\"", 1500);
            } else if ( response.status == 403 ){
                window.location = "/about";
            }
        }
    });
};

function updateTroupe( ) {
    var troupe_name = document.getElementById( "troupe_name" );
    
    $.ajax({
        url: "/updateTroupe", 
        type: "POST",
        data: ({troupe_name : troupe_name.value }),
        success: function(response) {
            self.location.reload(true);
        },
        error: function( response ) {
            if ( response.status == 400 ) {
                document.getElementById( 'troupe_name' ).value = "Invalid troupe name";
                setTimeout("document.getElementById('troupe_name').value=\"\"", 1500);
            }
        }
    });
};
