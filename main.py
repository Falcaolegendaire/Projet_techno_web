from studentTrade_BD import Produit, Utilisateur, connection, Panier  # pour la base de donnée
import hashlib
import uvicorn  # serveur pour fastapi 
from fastapi import FastAPI,Request,Form,HTTPException,UploadFile,File,Query  #API
from pydantic import BaseModel # validation des données 
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware  # pour autoriser les requetes
from sqlmodel import Field,SQLModel,create_engine,select,Session # pour la base de donnée( ORM)
from typing import Annotated,Optional
# import multipart
import shutil
import time


app=FastAPI()

# ceci monte les fichiers statiques pour les images et les fichiers css
app.mount("/static", StaticFiles(directory="static"), name="static")
templates=Jinja2Templates(directory="templates")

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


#____________________
#acceuil
@app.get("/",response_class=HTMLResponse)
async def connexion( request:Request):
    return templates.TemplateResponse("connexion.html", {"request":request})
#____________________
#

@app.get("/acceuil.html",response_class=HTMLResponse)
async def home( request:Request):
    return templates.TemplateResponse("acceuil.html", {"request":request})
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
                            where(Produit.category_item == "livre")
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
                    where(Produit.category_item == "mobilier")
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
                            where(Produit.category_item == "electronique")
        produits = cursor.exec(statement).all()

        return templates.TemplateResponse("electronique.html", {
            "request": request,
            "produits": produits
        })
#____________________

@app.get("/notification.html",response_class=HTMLResponse)
async def notification( request:Request):
    return templates.TemplateResponse("notification.html", {"request":request})
#____________________

@app.get("/panier.html",response_class=HTMLResponse)
async def panier( request:Request):
    return templates.TemplateResponse("panier.html", {"request":request})
#____________________

@app.get("/profil.html",response_class=HTMLResponse)
async def profil( request:Request):
    return templates.TemplateResponse("profil.html", {"request":request})
#____________________
#recherche
@app.get("/search",response_class=HTMLResponse)
async def search( request:Request, recherche: str = Query(...)):
    """test pour la recherche"""    
    with Session(connection) as cursor:
        statement = select(Produit, Utilisateur).join(Utilisateur, Produit.id_utilisateur == Utilisateur.id_utilisateur).\
                        where(Produit.name_item.ilike(f"%{recherche}%"))
        results = cursor.exec(statement).all()
        if not results:
            return templates.TemplateResponse("search.html", {"request": request, "produits": [], "message": "Aucun élément trouvé."})
        return templates.TemplateResponse("search.html", {"request": request, "produits": results, "message": recherche})
#_____________________

@app.get("/suggestions.html",response_class=HTMLResponse)
async def suggestions( request:Request):
    with Session(connection) as cursor:
        statement = select(Produit, Utilisateur).join(Utilisateur, Produit.id_utilisateur == Utilisateur.id_utilisateur)
                       
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
                        where(Produit.category_item == "habillement")
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
    id_current_user = 2  # à adapter dynamiquement plus tard

    with Session(connection) as session:
        stmt = select(Panier, Produit, Utilisateur).join(Produit, Produit.id_item == Panier.id_item).\
                        join(Utilisateur, Utilisateur.id_utilisateur == Produit.id_utilisateur).where(Panier.id_current_user == id_current_user)
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
    id_current_user = 2  # À adapter : récupérer depuis session / utilisateur connecté

    with Session(connection) as session:
        # Vérifie si l'article est déjà dans le panier
        statement = select(Panier).where(Panier.id_current_user == id_current_user, Panier.id_item == produit_id, Produit.quantity_item > 0)
        item = session.exec(statement).first()

        if item:
            item.quantite += quantite
            
        else:
            new_item = Panier(id_current_user=id_current_user, id_item=produit_id, quantite=quantite)
            session.add(new_item)
        session.commit()
        
        return RedirectResponse(url="/suggestions.html", status_code=303)

# ____________________

@app.post("/panier/supprimer/{id_item}")
async def supprimer_du_panier(id_item: int, request: Request):
    id_current_user = 2  # À adapter dynamiquement
    temp=0

    with Session(connection) as session:
        stmt = select(Panier).where(Panier.id_current_user == id_current_user, Panier.id_item == id_item)
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
    id_current_user = 2  # À adapter dynamiquement
    temp=0

    with Session(connection) as session:
        stmt = select(Panier).where(Panier.id_current_user == id_current_user, Panier.id_item == id_item)
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

            fill_table_produit(name=name_item,
                            description=description,
                            price=price_item,
                            quantity=quantity_item,
                            category=category_item,
                            image=full_path
                            )
            return RedirectResponse(url="/ajouter_offre.html",status_code=303)

# -----
def fill_table_produit(name:str,description:str,price:float,quantity:int,image:Optional[str]=None,category:str="autres"):
    """ fonction pour remplir la table produit"""""
    with Session(connection) as session:
        session.add(Produit(name_item=name,
                            description=description,
                            price_item=price,
                            quantity_item=quantity,
                            id_utilisateur=1,
                            category_item=category,
                            image_item=image
                            ))
        session.commit() 
        session.close()   #????
#______________________


# ______________________

#validation de commande
@app.post("/panier/commander",  response_class=HTMLResponse)
async def commande(request:Request,
                   Nom_produit:str=Form(...),
                   Prix_unitaire:int=Form(...),
                   Nom_vendeur:str=Form(...),
                   Email_vendeur:str=Form(...),
                   Id_item:int=Form(...),
                   Quantite:int=Form(...),
                   id_commande:int=Form(...)    
                   ):
        
        somme = Quantite*Prix_unitaire
        if update_database(Id_item, Quantite,id_commande):

            sujet="Object: Confirmation commande.\n\n"
            #le nom sam, dans le message est un nom  de test on le remplacera par le nom de l'utilisateur courant
            message=f"{sujet}Bonjour Monsieur/Madame SAM,\n Vous venez de passer la commande de {Quantite} unite de l'article <<{Nom_produit}>>, vous venez d'etre debite de la somme de {somme}€, {Nom_vendeur} vas se charger \
                    d'effectuer la livraison.\n\n Cordialement,\n\n L'équipe de StudentTrade."
            time.sleep(5)  # pour simuler le delai de reception du mail
            return templates.TemplateResponse("simul_mail.html", {
                    "request": request,
                    "email_vendeur": Email_vendeur,
                    "message": message
                    })
        return templates.TemplateResponse("simul_mail.html", {
                    "request": request,
                    "email_vendeur": "",
                    "message": "Stock insuffisant"
                    })
# __________________________

def update_database(Id_item, qte,Id_panier):
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
                cursor.delete(resultat)
                cursor.commit() 
            cursor.close()        
            return True
        return False
    
# ___________________________







    
    

if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)






  

