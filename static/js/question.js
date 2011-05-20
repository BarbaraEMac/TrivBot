var MAX_TIME = 30;

window.onLoad = countdown( MAX_TIME );

function countdown ( secs ) {   
    
    if (secs > 0) {
        foo = "countdown(" + (secs-1) + ")";
        setTimeout(foo, 1000);
    } else {
        button = document.getElementById('submit');
        button.style.visibility = 'hidden';

        setTimeout('submit()', 1000);
    }

    msg = secs;
    if ( secs == 0 ) {
        msg += "<br /><object style=\"font-size: 0.7em;\">Submitting!</object>";

    } else if ( secs <= 5 ) {
        msg += "<br /> Hurry!";
    }
    else if ( secs <= (MAX_TIME/2) && secs >= ((MAX_TIME/2) - 3) ){
        msg += "<br /><object style=\"font-size: 0.7em;\">Half-Way!</object>";
    }

    if ( document.getElementById( "cntdwn" ) ) {
        document.getElementById("cntdwn").innerHTML = msg;
    }
}

function submit() {
    document.forms["question_form"].submit.click();
}
