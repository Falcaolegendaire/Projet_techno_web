let boutons = document.getElementsByClassName("button");
let bouton_offre=document.getElementById("button_offre");
let bouton_ajout_offre=document.getElementById("button_ajouter_offre");
let bouton_suggestion=document.getElementById("button_suggestion");
let bouton_notification=document.getElementById("button_notification");
let bouton_contact=document.getElementById("button_contact");
let bouton_aide=document.getElementById("button_aide");
let bouton_profil=document.getElementById("button_profil");
let bouton_logout=document.getElementById("button_log_out");
let bouton_supprimer_compte=document.getElementById("delete_account");

function redirect_to_another_page(path,target) {
    window.open(path, target);
}
// debut des instructions pour pouvoir rediger les users quand ils vont cliquer sur les boutons
bouton_offre.addEventListener('click',function(){
        redirect_to_another_page("/offre.html","_parent");
});

bouton_ajout_offre.addEventListener('click',function(){
    redirect_to_another_page("/ajouter_offre.html","_parent");
});

bouton_suggestion.addEventListener('click',function(){
    redirect_to_another_page("/suggestions.html","_parent");
});

bouton_notification.addEventListener('click',function(){
    redirect_to_another_page("/notification.html","_parent");
});

bouton_contact.addEventListener('click',function(){
    redirect_to_another_page("/contact.html","_parent");
});

bouton_aide.addEventListener('click',function(){
    redirect_to_another_page("/aide.html","_parent");
});

bouton_profil.addEventListener('click',function(){
    redirect_to_another_page("/profil.html","_parent");
});

bouton_logout.addEventListener('click',function(){
    let bool;
    bool=confirm(" \u26A0\uFE0F voulez vous vraiment vous deconnectez?");
    if (bool){
        alert("deconnexion reussie 	\u2705");
        window.location.replace("/");
    }
    
});

function confirmerSuppression() {
    return confirm("Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.");
}

function confirmation_commande(){

    return confirm("Voulez vous vraiment passer cette commande?")
    
}

function confirmation_message(){

     alert("Message envoyé au vendeur")
     return true
     
}


for (let i = 0; i < boutons.length; i++) {
    boutons[i].addEventListener("mouseover", function() {
        boutons[i].style.backgroundColor = "black"; 
    });

    boutons[i].addEventListener("mouseout", function() {
        boutons[i].style.backgroundColor = ""; 
    });
}