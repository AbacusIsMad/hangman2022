
/* Submit letter */

$('#letter-form').submit(function(e) {
  var data = $("#letter-form").serialize();
  
  /* Empty input */
  $('#letter-form input').val('');
  
  $.ajax({
    type: "POST",
    url: '',
    data: data,
    
    
    success: function(data) {
      /* Refresh if finished */
      if (data.finished) {
        location.reload();
      }
      else {
        /*if (data.invalidLetter) {
          console.log('invalid!');
          var cell = document.getElementById("letterinput");
          cell.style.border = "2px solid red";
          setTimeout(function(){ cell.style.border = null }, 100);
          setTimeout(function(){ cell.style.border = "2px solid red" }, 200);
          setTimeout(function(){ cell.style.border = null }, 300);
          setTimeout(function(){ cell.style.border = "2px solid red" }, 400);
          setTimeout(function(){ cell.style.border = null }, 500);
        }*/
        if (data.invalidLetter == 1) {
          flash();
        }
        
        /* Update current */
        $('#current').text(data.current);
        //const inside = <h1 id=current class=spaced>{% for letter in data.current %}{% if letter != "_" %}<span class="text-success">{% endif %}{{ letter }}{% if letter != "_" %}</span>{% endif %}{% endfor %}</h1>;
        //$('#current').text(inside);
        //there are no errors here, no no sir!
        
        /* Update errors */
        $('#errors').html(
          'Errors (' + data.errors.length + '/6): ' +
          '<span class="text-danger spaced">' + data.errors + '</span>');
          
        /* Update drawing */
        //updateDrawing(data.errors);
        $('#hangman-drawing').children().slice(0, data.errors.length).show();
        
        /*flicker if invalid letter*/
        if (data.invalidLetter) {
          console.log('invalid!');
          var cell = document.getElementById("letterinput");
          cell.style.border = "2px solid red";
          setTimeout(function(){ cell.style.border = null }, 100);
          setTimeout(function(){ cell.style.border = "2px solid red" }, 200);
          setTimeout(function(){ cell.style.border = null }, 300);
          setTimeout(function(){ cell.style.border = "2px solid red" }, 400);
          setTimeout(function(){ cell.style.border = null }, 500);
        }
      }
    }
  });
  e.preventDefault();
});

//hangman drawing instance here
/*function updateDrawing(errors) {
  $('#hangman-drawing').children().slice(0, errors.length).show();
}*/

/*$('#letter-form').submit(function(e) {
  var data = $("#letter-form").serialize();
  
  $('#letter-form input').val('');
  
  $.ajax({
    type: "POST",
    url: '',
    data: data,
    success: function(data) {
      if (data.finished) {
        location.reload();
      }
      else {
        //$('#current').text(data.current);
        const inside = <h1 id="current" class="spaced">{% for letter in data.current %}{% if letter != "_" %}<span class="text-success">{% endif %}{{ letter }}{% if letter != "_" %}</span>{% endif %}{% endfor %}</h1>;
        $('#current').html(inside);
      }
    }
  });
  e.preventDefault();
});*/
