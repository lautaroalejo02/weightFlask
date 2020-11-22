function locura(selectObject){
    var input = document.getElementById("genders").value;
    var hola = selectObject.value;
    if( hola == "O") {
        document.getElementById("speci").style.visibility = 'visible';
    }else {

        document.getElementById("speci").style.visibility = 'hidden';

    }
  
}
function register(){
    var input = document.getElementById("speci").value;
    document.getElementById("others").value = input;


}

function hola(){
    console.log("hola");
}
