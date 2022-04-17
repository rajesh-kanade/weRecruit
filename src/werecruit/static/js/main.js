window.addEventListener("load", function(){
    var checkbox  = document.getElementById('{{form.check.id}}');
    var x = document.getElementById("{{form.current_password.id}}");
    checkbox.addEventListener('change', function() {
        if(this.checked) {
            x.type = 'text'; 
        } else {
            x.type = 'password'; 
        }
    });
});