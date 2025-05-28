from studentTrade_BD import Produit,connection  # pour la base de donnée
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
import multipart
import shutil
app=FastAPI()
# ceci monte les fichiers statiques pour les images et les fichiers css
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
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

@app.get("/",response_class=HTMLResponse)
async def connexion( request:Request):
    return templates.TemplateResponse("connexion.html", {"request":request})

@app.get("/ajouter_offre.html",response_class=HTMLResponse)
async def home( request:Request):
    return templates.TemplateResponse("ajouter_offre.html", {"request":request})

@app.get("/acceuil.html",response_class=HTMLResponse)
async def home( request:Request):
    return templates.TemplateResponse("acceuil.html", {"request":request})


@app.get("/search",response_class=HTMLResponse)
#fonction qui permet de rechercher des produits grace à la barre de recherche du site 
async def search( request:Request, recherche: str = Query(...)):
    """test pour la recherche"""
    
    with Session(connection) as cursor:
        # la fonction marche il faut juste gerer l'affichage des résultats dans une page html
        statement = select(Produit)
        results = cursor.exec(statement.where(Produit.name_item.ilike(f"%{recherche}%"))).all()
        if not results:
            return " Aucun element retrouvé"
        else:
            for element in results:
                 print(element.name_item, element.description, element.price_item, element.quantity_item, element.category_item, element.image_item)
    


@app.post("/submit_offer",response_class=HTMLResponse)
async def add_item( request:Request,
                 name_item: str = Form(...),
                 description: str = Form(...),
                 price_item: float = Form(...),
                 quantity_item: int = Form(...),
                 image: UploadFile = File(...),
                 category_item:str=Form(...)):
                  
              
            image_name=image.filename
            image_path=f"templates/Images/{image_name}"
            with open(image_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                        
            fill_table_produit(name=name_item,
                            description=description,
                            price=price_item,
                            quantity=quantity_item,
                            category=category_item,
                            image=image_path
                            )
            return RedirectResponse(url="/ajouter_offre.html",status_code=303)




def  fill_table_produit(name:str,description:str,price:float,quantity:int,image:Optional[str]=None,category:str="autres"):
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
         # fonctionnel mais a besoin d'inserer l'id_utilisateur courant pour lié le produit à l'utilisateur
         session.commit() 

# il va falloir  rajouter des routes vers les pages html du projet pour que le serveur ne face pas un code 404 

if __name__=="__main__":
    
    uvicorn.run(app, host="127.0.0.1", port=8000)






  

