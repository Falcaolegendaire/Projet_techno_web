from typing import Optional
from sqlmodel import Field,SQLModel,create_engine,select  # pour la base de donnée( ORM)

nom_data_base="StudentTrade.db"
connection= create_engine(f"sqlite:///{nom_data_base}",echo=True)

class Utilisateur(SQLModel, table=True):
        id_utilisateur: Optional[int]= Field(default=None,primary_key=True)
        username: str=Field(index=True,unique=True)
        email:str =Field(index=True,unique=True)  # pour l'unicité des emails
        hashed_password:str
        is_active:bool=Field(default=False) #activité de l'utilisateur


class Produit(SQLModel, table=True):
        id_item:  Optional[int]= Field(default=None,primary_key=True)
        id_utilisateur: Optional[int] = Field(default=None, foreign_key="utilisateur.id_utilisateur")
        name_item: str=Field(index=True,unique=False)
        description:str
        price_item:float
        quantity_item:int
        category_item:str=Field(default="autres", nullable=True)  # catégorie de l'article
        image_item: Optional[str] = Field(default=None, nullable=True)  # chemin local de l'image


class Panier(SQLModel, table=True):
    id_panier: Optional[int] = Field(default=None, primary_key=True)
    id_current_user: int
    id_item: Optional[int] = Field(default=None, foreign_key="produit.id_item")
    quantite: int = 1

class NOtification(SQLModel,table=True):
        id_notification: Optional[int]= Field(default=None,primary_key=True)
        id_utilisateur: Optional[int] = Field(default=None, foreign_key="utilisateur.id_utilisateur")
        message: Optional[str]=Field(default=None,nullable=True)

