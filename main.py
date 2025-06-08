from studentTrade_BD import Produit, Utilisateur, connection, Panier, NOtification # pour la base de donnée
import uvicorn  # serveur pour fastapi 
from fastapi import FastAPI,Request,Form,HTTPException,UploadFile,File,Query  #API
from pydantic import BaseModel # validation des données 
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware  # pour autoriser les requetes
from sqlmodel import Field,SQLModel,create_engine,select,Session,delete # pour la base de donnée( ORM)
from typing import Annotated,Optional
import shutil
import os
from security import get_password_hash, verify_password, ALGORITHM, SECRET_KEY
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets # module pour definir une clé secrete pour le middleware

app=FastAPI()

# ceci monte les fichiers statiques pour les images et les fichiers css
app.mount("/static", StaticFiles(directory="static"), name="static")
templates=Jinja2Templates(directory="templates")

key=secrets.token_hex(32)
# autoriser les requetes et l'utilisation des methodes 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# fonction de creation de la basse de donnée
def create_data_base():
    SQLModel.metadata.create_all(connection)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           

create_data_base()  # initialisation de la base de donnée


#inscription
@app.post("/register")
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    hashed_pw = get_password_hash(password)
    new_user = Utilisateur(username=username, email=email, hashed_password=hashed_pw, is_active=True)

    with Session(connection) as session:
        existing_user = session.exec(select(Utilisateur).where(Utilisateur.email == email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        session.add(new_user)
        session.commit()
        return RedirectResponse(url="/", status_code=303)
    


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


#____________________

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    with Session(connection) as session:
        user = session.exec(select(Utilisateur).where(Utilisateur.email == email)).first()
        if not user or not verify_password(password, user.hashed_password):
          return templates.TemplateResponse("connexion.html", {"request":request,
                                                                "error":True,
                                                                "style":"border: 2px solid red;"})

        access_token = create_access_token(data={"sub": str(user.id_utilisateur)})
        response = RedirectResponse(url="/acceuil.html", status_code=303)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    
    #vérification de l'utilisateur connecté


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    with Session(connection) as session:
        user = session.get(Utilisateur, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        return user

#____________________
@app.get("/",response_class=HTMLResponse)
async def connexion( request:Request):
    return templates.TemplateResponse("connexion.html", {"request":request, "error":False,
                                                         "Style":""})

@app.get("/connexion.html",response_class=HTMLResponse)
async def page_connexion( request:Request):
    return templates.TemplateResponse("connexion.html", {"request":request, "error":False,
                                                         "style":""})
#____________________
#____________________


@app.get("/acceuil.html",response_class=HTMLResponse)
async def home( request:Request):
    user= get_current_user(request)
    name_current_user=user.username

    return templates.TemplateResponse("acceuil.html", {"request":request, "utilisateur":name_current_user})
#____________________

@app.get("/ajouter_offre.html",response_class=HTMLResponse)
async def ajouter_offre( request:Request):
    return templates.TemplateResponse("ajouter_offre.html", {"request":request})
#____________________

@app.get("/aide.html",response_class=HTMLResponse)
async def aide( request:Request):
    return templates.TemplateResponse("aide.html", {"request":request})

#____________________

@app.get("/contact.html",response_class=HTMLResponse)
async def contact( request:Request):
    return templates.TemplateResponse("contact.html", {"request":request})
#____________________

@app.get("/document.html",response_class=HTMLResponse)
async def document( request:Request):
    return templates.TemplateResponse("document.html", {"request":request})
#____________________

#afficher les livres
@app.get("/livre.html",response_class=HTMLResponse)
async def livre( request:Request):
    with Session(connection) as cursor:
        statement = select(Produit, Utilisateur).join(Utilisateur, Produit.id_utilisateur == Utilisateur.id_utilisateur).\
                            where(Produit.category_item == "livre",Produit.quantity_item>0)
        produits = cursor.exec(statement).all()

        return templates.TemplateResponse("livre.html", {
            "request": request,
            "produits": produits
        })
#____________________

#afficher les mobiliers
@app.get("/mobilier.html",response_class=HTMLResponse)
async def meuble( request:Request):
    with Session(connection) as cursor:
        statement = select(Produit, Utilisateur).join(Utilisateur, Produit.id_utilisateur == Utilisateur.id_utilisateur).\
                    where(Produit.category_item == "mobilier",Produit.quantity_item>0)
        produits = cursor.exec(statement).all()

        return templates.TemplateResponse("mobilier.html", {
            "request": request,
            "produits": produits
        })
#____________________

#afficher electroniques
@app.get("/electronique.html",response_class=HTMLResponse)
async def meuble( request:Request):
    with Session(connection) as cursor:
        statement = select(Produit, Utilisateur).join(Utilisateur, Produit.id_utilisateur == Utilisateur.id_utilisateur).\
                            where(Produit.category_item == "electronique",Produit.quantity_item>0)
        produits = cursor.exec(statement).all()

        return templates.TemplateResponse("electronique.html", {
            "request": request,
            "produits": produits
        })

#____________________

@app.get("/panier.html",response_class=HTMLResponse)
async def panier( request:Request):
    return templates.TemplateResponse("panier.html", {"request":request})
#____________________

@app.get("/profil.html", response_class=HTMLResponse)
async def profil(request: Request, message: str = ""):
    user = get_current_user(request)

    with Session(connection) as session:
        produits = session.exec(select(Produit).where(Produit.id_utilisateur == user.id_utilisateur)).all()

    return templates.TemplateResponse("profil.html", {
        "request": request,
        "user": user,
        "produits": produits,
        "message": message
    })

# suppression de l'utilisateur satisfaisant les règles(RGPD)
@app.post("/supprimer/profil", response_class=HTMLResponse)
async def delete_profil(request: Request):
    user = get_current_user(request)

    with Session(connection) as session:
        query_1=delete(Panier).where(Panier.id_current_user==user.id_utilisateur)
        query_2=select(Produit).where(Produit.id_utilisateur==user.id_utilisateur)
        query_3=select(Utilisateur).where(Utilisateur.id_utilisateur==user.id_utilisateur)
        query_4=delete(NOtification).where(NOtification.id_utilisateur==user.id_utilisateur)
      
        
        session.exec(query_1)
        session.exec(query_4)
        result_2=session.exec(query_2).all()
        result_3=session.exec(query_3).first()
        notifiacations =session.exec(select(NOtification)).all()
        
        for produit in result_2:
            produit.description="None"
            produit.category_item="None"
            if produit.image_item and os.path.exists(produit.image_item):
                os.remove(produit.image_item) 
            produit.image_item="None"
            produit.quantity_item=0
            produit.price_item=0
            produit.name_item="None"

        for notif in notifiacations:
            mot="commande"
            # ici je modifie juste les notifications qui n'indiquent pas de commande car les notifications de commandes peuvent faire preuve de
            # recu pour le client qui commande 
            if (result_3.username in notif.message and mot not in notif.message):
                new_nom="<<Cette utilisateur n'utilise plus ce site>>"
                new_email="<< Email indisponible car l'utilisateur n'utilise plus ce site>>"
                notif.message=notif.message.replace(result_3.username,new_nom)
                notif.message=notif.message.replace(result_3.email,new_email)

        result_3.username="None"
        result_3.email="None"
        result_3.hashed_password="None"
        result_3.is_active=0
        
        session.add_all(result_2)
        session.add(result_3)
        session.add_all(notifiacations)
        session.commit()
        
    return RedirectResponse(url="/", status_code=303)




@app.post("/profil/update")
async def update_profil(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(None)
):
    user = get_current_user(request)

    with Session(connection) as session:
        db_user = session.get(Utilisateur, user.id_utilisateur)
        db_user.username = username
        db_user.email = email
        if password:
            db_user.hashed_password = get_password_hash(password)
        session.add(db_user)
        session.commit()

    return RedirectResponse(url="/profil.html?message=Profil+mis+à+jour", status_code=303)
    
@app.post("/offre/supprimer/{id_item}")
async def supprimer_offre(id_item: int, request: Request):
    user = get_current_user(request)

    with Session(connection) as session:
        produit = session.get(Produit, id_item)

        if not produit or produit.id_utilisateur != user.id_utilisateur:
            raise HTTPException(status_code=403, detail="Non autorisé")
        
        if os.path.exists(produit.image_item):
            os.remove(produit.image_item)
        session.delete(produit)
        session.commit()

    return RedirectResponse(url="/profil.html", status_code=303)


#recherche
@app.get("/search",response_class=HTMLResponse)
async def search( request:Request, recherche: str = Query(...)):
    """test pour la recherche"""    
    with Session(connection) as cursor:

        statement = select(Produit, Utilisateur).join(Utilisateur, Produit.id_utilisateur == Utilisateur.id_utilisateur).\
                        where(Produit.name_item.ilike(f"%{recherche}%"),Produit.quantity_item>0)
        results = cursor.exec(statement).all()
        if not results:
            return templates.TemplateResponse("search.html", {"request": request, "produits": [], "message": "Aucun élément trouvé."})
        return templates.TemplateResponse("search.html", {"request": request, "produits": results, "message": recherche})
#_____________________

@app.get("/suggestions.html",response_class=HTMLResponse)
async def suggestions( request:Request):
    with Session(connection) as cursor:
        statement = select(Produit, Utilisateur).join(Utilisateur, Produit.id_utilisateur == Utilisateur.id_utilisateur).where(Produit.quantity_item>0)
                       
        results = cursor.exec(statement).all()
        if not results:
            return templates.TemplateResponse("suggestions.html", {"request": request, "produits": [], "message": "Aucun élément trouvé."})
        return templates.TemplateResponse("suggestions.html", {"request": request, "produits": results, "message": results})
#____________________

#vetements
@app.get("/habillement.html",response_class=HTMLResponse)
async def afficher_vetement( request:Request):  
    with Session(connection) as cursor:
        statement = select(Produit, Utilisateur).join(Utilisateur, Produit.id_utilisateur == Utilisateur.id_utilisateur).\
                        where(Produit.category_item == "habillement",Produit.quantity_item>0)
        produits = cursor.exec(statement).all()

        return templates.TemplateResponse("habillement.html", {
            "request": request,
            "produits": produits
        })
#_____________________

#details produits
@app.get("/produit/{produit_id}", response_class=HTMLResponse)
async def voir_details(request: Request, produit_id: int):
    with Session(connection) as session:
        statement = select(Produit).where(Produit.id_item == produit_id)
        produit = session.exec(statement).first()
        if not produit:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        return templates.TemplateResponse("details.html", {
            "request": request,
            "produit": produit
        })


#_____________________

#afficher le panier
@app.get("/panier", response_class=HTMLResponse)
async def afficher_panier(request: Request):
    user= get_current_user(request)
    current_user_id=user.id_utilisateur
    with Session(connection) as session:
        stmt = select(Panier, Produit, Utilisateur).join(Produit, Produit.id_item == Panier.id_item).\
                        join(Utilisateur, Utilisateur.id_utilisateur == Produit.id_utilisateur).where(Panier.id_current_user == current_user_id)
        resultats = session.exec(stmt).all()

        panier_items = []
        total_global = 0

        for panier, produit, utilisateur in resultats:
            sous_total = panier.quantite * produit.price_item
            panier_items.append({
                "produit": produit,
                "quantite": panier.quantite,
                "sous_total": sous_total,
                "utilisateur": utilisateur,
                "id_commande": panier.id_panier
                
            })
            total_global += sous_total

    return templates.TemplateResponse("panier.html", {
        "request": request,
        "items": panier_items,
        "total_global": total_global
    })


#______________________

#ajouter au panier
@app.post("/panier/ajouter", response_class=RedirectResponse)
async def ajouter_au_panier(request: Request, produit_id: int = Form(...), quantite: int = Form(default=1)):

    user= get_current_user(request)
    current_user_id=user.id_utilisateur

    with Session(connection) as session:
        # Vérifie si l'article est déjà dans le panier
        statement = select(Panier).where(Panier.id_current_user == current_user_id, Panier.id_item == produit_id, Produit.quantity_item > 0)
        item = session.exec(statement).first()

        if item:
            item.quantite += quantite
            
        else:
            new_item = Panier(id_current_user=current_user_id, id_item=produit_id, quantite=quantite)
            session.add(new_item)
        session.commit()
        
        return RedirectResponse(url="/suggestions.html", status_code=303)

# ____________________

@app.post("/panier/supprimer/{id_item}")
async def supprimer_du_panier(id_item: int, request: Request):
    temp=0
    user= get_current_user(request)
    current_user_id=user.id_utilisateur

    with Session(connection) as session:
        stmt = select(Panier).where(Panier.id_current_user == current_user_id, Panier.id_item == id_item)
        item = session.exec(stmt).first()

        temp = item.quantite
        item.quantite = temp - 1
        
        if item:
            session.add(item)
            session.commit()
        if(item.quantite == 0):
                session.delete(item)
                session.commit() 
        session.close()

    return RedirectResponse(url="/panier", status_code=303)


# ______________________

@app.post("/panier/ajouter/{id_item}")
async def supprimer_du_panier(id_item: int, request: Request):
    temp=0
    user= get_current_user(request)
    current_user_id=user.id_utilisateur
    with Session(connection) as session:
        stmt = select(Panier).where(Panier.id_current_user == current_user_id, Panier.id_item == id_item)
        item = session.exec(stmt).first()

        temp = item.quantite
        item.quantite = temp  +1
        
        if item:
            session.add(item)
            session.commit()
        session.close()
  
    return RedirectResponse(url="/panier", status_code=303)


# ______________________

@app.get("/offre.html", response_class=HTMLResponse)
async def afficher_offres(request: Request):
    return templates.TemplateResponse("offre.html", {"request":request})
# ___________________

#poster une annonce
@app.post("/submit_offer",response_class=HTMLResponse)
async def add_item( request:Request,
                name_item: str = Form(...),
                description: str = Form(...),
                price_item: float = Form(...),
                quantity_item: int = Form(...),
                image: UploadFile = File(...),
                category_item:str=Form(...)):

            image_name = image.filename
            image_path = f"Images/{image_name}" 
            full_path = f"static/{image_path}"

            with open(full_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            fill_table_produit(request,name=name_item,
                            description=description,
                            price=price_item,
                            quantity=quantity_item,
                            category=category_item,
                            image=full_path
                            )
            return RedirectResponse(url="/ajouter_offre.html",status_code=303)

# -----
def fill_table_produit(request:Request,name:str,description:str,price:float,quantity:int,image:Optional[str]=None,category:str="autres"):
    """ fonction pour remplir la table produit"""""
    user= get_current_user(request)
    current_user_id=user.id_utilisateur

    with Session(connection) as session:
        session.add(Produit(name_item=name,
                            description=description,
                            price_item=price,
                            quantity_item=quantity,
                            id_utilisateur=current_user_id,
                            category_item=category,
                            image_item=image
                            ))
        session.commit() 
        session.close()   #????
#______________________

#contacter le vendeur
@app.post("/contact_seller",response_class=HTMLResponse)
async def mail_to_seller(request:Request,
                  email_vendeur:str=Form(...),
                  produit:str=Form(...),
                  message:str=Form(...),
                  nom_vendeur:str=Form(...),
                  id_vendeur:int=Form(...)):
        user= get_current_user(request)
        name_current_user=user.username
        email_cuurent_user=user.email

        notification=f"Bonjour Monsieur/Madame {nom_vendeur},\n Vous avez recu un message de la part de {name_current_user} pour votre article <<{produit}>>.\n\n Voici le message:  <<{message}>>  Vous pouvez repondre à ce message en repondant à l'email suivant:{email_cuurent_user} \n\n Cordialement,\n\n L'équipe de StudentTrade."
        with Session(connection) as session:
            session.add(NOtification(id_utilisateur=id_vendeur,message=notification))
            session.commit()
        return RedirectResponse(url="/panier", status_code=303)

@app.get("/notification.html",response_class=HTMLResponse)
async def notification( request:Request):
    user= get_current_user(request)
    current_user_id=user.id_utilisateur

    with Session(connection) as cursor:
        query=select(NOtification).where(NOtification.id_utilisateur==current_user_id)
        notification=cursor.exec(query).all()
    return templates.TemplateResponse("notification.html", {
                    "request": request,
                    "notification": notification
                    })
# _______________________

@app.post("/notification/supprimer/{id_notif}")
async def supprimer_de_notification(id_notif: int, request: Request):
    with Session(connection) as session:
        stmt = select(NOtification).where(NOtification.id_notification == id_notif)
        result = session.exec(stmt).first()
        session.delete(result)
        session.commit()
    return RedirectResponse(url="/notification.html",status_code=303)



#validation de commande
@app.post("/panier/commander",  response_class=HTMLResponse)
async def commande(request:Request,
                   Nom_produit:str=Form(...),
                   Prix_unitaire:int=Form(...),
                   Nom_vendeur:str=Form(...),
                   Email_vendeur:str=Form(...),
                   Id_item:int=Form(...),
                   Quantite:int=Form(...),
                   id_commande:int=Form(...),
                   id_vendeur:int=Form(...)  
                   ):
        user= get_current_user(request)
        current_user_id=user.id_utilisateur
        name_current_user=user.username
        somme = Quantite*Prix_unitaire
        if allow_order(Id_item, Quantite,id_commande):
            notification_acheteur=f"Bonjour Monsieur/Madame {name_current_user},\n Vous venez de passer la commande de {Quantite} unite de l'article <<{Nom_produit}>>, vous venez d'etre debite de la somme de {somme}€, {Nom_vendeur} vas se charger \
                    d'effectuer la livraison.\n\n Cordialement,\n\n L'équipe de StudentTrade."
            notification_vendeur=f"Bonjour Monsieur/Madame {Nom_vendeur},\n Vous avez une commande de {Quantite} unité(s) de votre produit <<{Nom_produit}>> de la part du client {name_current_user} veillez à acheminer la commande dans un delai de 5 jours maximun\
                  \n\n Cordialement,\n\n L'équipe de StudentTrade."
            with Session(connection) as session:
                session.add(NOtification(id_utilisateur=id_vendeur,message=notification_vendeur))
                session.add(NOtification(id_utilisateur=current_user_id,message=notification_acheteur))
                session.commit()
        return RedirectResponse(url="/panier",status_code=303)
# __________________________
# verifie si le site a assez de stock pour la commamande et met à jour les stock de produits
def allow_order(Id_item, qte,Id_panier):
    with Session(connection) as cursor:
        temp = 0

        query=select(Panier).where(Panier.id_panier == Id_panier)
        result=cursor.exec(query).first()

        statement = select(Produit).where(Produit.id_item == Id_item)
        resultat = cursor.exec(statement).first()
        if(qte <= resultat.quantity_item):

            temp = resultat.quantity_item -qte
            resultat.quantity_item = temp

            cursor.add(resultat)
            cursor.delete(result)
            cursor.commit()
            if(resultat.quantity_item == 0):
                image_path = resultat.image_item
                if os.path.exists(image_path):
                    os.remove(image_path) # ca permet de nettoyer les images sur le disque lors de la suppression d'un produit
                cursor.add(resultat)
                cursor.delete(resultat)
            cursor.commit() 
                
            return True
        return False
    
# ___________________________







    
    

if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)






  

