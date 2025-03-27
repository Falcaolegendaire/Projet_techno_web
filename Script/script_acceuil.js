let boutons = document.getElementsByClassName("button");
// let deconnexion=document.getElementById("button_log_out");
for (let i = 0; i < boutons.length; i++) {
    boutons[i].addEventListener("mouseover", function() {
        boutons[i].style.backgroundColor = "rgb(186, 218, 213)"; 
    });

    boutons[i].addEventListener("mouseout", function() {
        boutons[i].style.backgroundColor = ""; 
    });

function logout(){
    let bool;
    bool=confirm("voulez vous vraiment vous deconnectez?");
    if(bool){
        window.open("./connexion.html", "_parent"); // par defaut le script est consideré comme etant dans le dossier du fichier html dont il est relié
        }
    } 
}