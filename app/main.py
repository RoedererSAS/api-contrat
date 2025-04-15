#!/usr/bin/python3
import os

import logging
from app.db.database import connect_to_as400
from fastapi import FastAPI, status, Path
from typing import Optional, Union, Annotated
from fastapi.responses import JSONResponse, Response
from app.db.models import Assure, Entreprise, Contrat, Beneficiaire

db_name=os.getenv("CW_AS400_DATABASE")
app = FastAPI(
    title="API Contrats",
    description="API exposant les données de l'infocentre",
    summary="Accéder aux informations sur les contrats, adherents, bénéficiaires et services",
    version="0.0.1",
    openapi_url=f"/api/v1/openapi.json",
    docs_url=f"/api/v1/docs",
    redoc_url=f"/api/v1/redoc",
    root_path="/contrats",
    contact={
        "name": "c24b <Constance de Quatrebarbes>",
        "email": "ext.cdequarebarbes@roederer.fr",
    },
)

@app.get("/assures/{id:int}", summary="Consulter les informations d'un assuré",
    description=f"""## GET ASSURE 

Cette méthode prend en paramètre un numéro d'assuré principal(entier positif) 
et renvoie:
- un code de status 
- ainsi que les informations associées à l'assuré:
    - les élément d'identification de l'assuré
    - les bénéficiaires
    - les services 
    - les contrats
""")
def get_assure(id: Annotated[int, Path(title="Numéro de la personne assurée")]):

    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        pers_id:int = id*100
        cursor.execute(f"SELECT * FROM {db_name}.DTWADHE AS ADH INNER JOIN {db_name}.DTWPERS AS PERS ON ADH.ADHE_PERS_ID = PERS.PERS_ID WHERE PERS.PERS_ID = {str(pers_id)}")
        # AND (ADH.ADHE_DATE_FIN > DATE '{str(Y3_AGO)}' OR ADH.ADHE_DATE_FIN is NULL) AND PERS.PERS_TYPE='AP'
        rows = cursor.fetchall()
        if rows is None or len(rows) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"Assuré N°<{id}> not found.")
        header1:list = ['id', 'cntr_id', 'pers_id', 'date_debut', 'date_fin', 'statut', 'motif_debut', 'motif_fin', 'mod_paiemt', 'freq_paiemt', 'exo_coti', 'parent_id', 'valide_du', 'createur', 'date_ins ', 'date_modif']
        header2:list = ["pers_id","numero","matricule","numero_ss","nom","prenom","patronyme","date_naiss","regime","grand_regime","sexe","type","rang_jumeau","situation_fam","teletrans","alert_mail","date_cpte_cli","rue_ligne1","rue_ligne2","rue_ligne3","cp","ville","pays","date_adr","email","tel_fixe","tel_mobile","parent_id","date_creation","aut_prelev","date_ins","date_modif"]
        header:list = header1+header2    
        contrats = set()
        parent_ids = set()
        mutuelles = set()
        entreprises = set()
        for row in rows:
            assure = dict(zip(header, row))
            contrats.add(assure["cntr_id"])
            
            if assure["parent_id"] is not None:
                parent_ids.add(assure["parent_id"])
            del assure["cntr_id"]
            del assure["parent_id"]
        assure["contrats"] = [get_contrat(id).get("contrat") for id in list(contrats)]
        # mutuelles = list(set([c["agen_id"] for c in assure["contrats"]]))
        # entreprises = list(set([c["entr_id"] for c in assure["contrats"]]))
        # produits = list(set([c["prd_id"] for c in assure["contrats"]]))
        # assure["mutuelles"] = [get_mutuelle(m).get("mutuelle") for m in mutuelles]
        # assure["entreprises"] = [get_entreprise(e).get("entreprise") for e in entreprises]
        # assure["produits"] = [get_produit(p).get("produit") for p in produits]
        # assure["categorie"] = assure["contrats"][0]["categorie"]
        # assure["parents"] = list(parent_ids)# je ne sais pas à quoi ca sert pour le moment
        
        # Assure.model_validate(assure)
        return assure
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")
    

# @app.get("/entreprises/{id:int}", summary="Consulter les informations d'une entreprise",
#     description=f"""## GET entreprise    
# Cette méthode prend en paramètre un numéro d'adhérent entreprise un entier positif 
# et renvoie:
# un code de status ainsi que les informations associées à l'entreprise
# - les element d'identification de l'entreprise
# - les assurés
# - les bénéficiaires
# - les services 
# - les contrats
# """)
def get_entreprise(id:int):
    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {db_name}.DTWENTR AS ENT WHERE ENT.ENTR_ID = {str(id)}")
        rows = cursor.fetchall()
        if rows is None or len(rows) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"ENtreprise N°<{id}> not found.")
        
        header1 = ["id","raison_sociale","siret","code_ape","code_naf","fjur","rue_ligne1","rue_ligne2","rue_ligne3","dpt","cp","ville","pays","tel","centre_gest","atc","charge_cpte","date_creation","date_ins","date_modif"]
        # header2 = ["deco_id","cntr_id","entr_id","agen_id","catg_code","prdt_id","date_debut","date_fin","date_suspension","motif_debut","motif_fin","num_charge_cpte","charge_compte","statut","responsable","terme_appel","ordre_decptage","assistance","mode_paiement","impaye_per","impaye_mnt","date_mise_dem","exo_coti","date_modif_erp","date_arrete","date_ins","date_modif"]
        # header:list = header1+header2   
        return {"id":id, "entreprises": [dict(zip(header1,r)) for r in rows], "count": len(rows)}
    return {"status": "ok"}


@app.get("/{id:int}", summary="Consulter les informations d'un contrat",
    description=f"""## GET CONTRAT
Cette méthode prend en paramètre un numéro de contrat (un entier positif )
et renvoie :
- un code de status 
- un contrat
""")
def get_contrat(id:int):
    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {db_name}.DTWCNTR AS CNTR WHERE CNTR.CNTR_ID = {str(id)}")
        row = cursor.fetchone()
        if row is None or len(row) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"Contrat N°<{id}> not found.")
        
        header1 = ["id","entr_id","agen_id","catg_code","prdt_id","date_debut","date_fin","date_suspension","motif_debut","motif_fin","num_charge_cpte","charge_compte","statut","responsable","terme_appel","ordre_decptage","assistance","mode_paiement","impaye_per","impaye_mnt","date_mise_dem","exo_coti","date_modif_erp","date_arrete","date_ins","date_modif"]
        contrat = dict(zip(header1,row))
        contrat["entreprise"]= get_entreprise(contrat["entr_id"]).get("entreprise")
        del contrat["entr_id"]
        contrat["produit"] = get_produit(contrat["prdt_id"]).get("produit")
        del contrat["prdt_id"]
        contrat["categorie"] = get_categorie(contrat["catg_code"].strip()).get("categorie")
        del contrat["catg_code"]
        contrat["mutuelle"] = get_mutuelle(contrat["agen_id"]).get("mutuelle")
        del contrat["agen_id"]
        return contrat
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")


# @app.get("/mutuelle/{id:int}", summary="Consulter les informations d'une mutuelle",
#     description=f"""## GET MUTUELLE
# Cette méthode prend en paramètre un code de mutuelle (un entier positif )
# et renvoie:
# un code de status ainsi que la mutuelle""")
def get_mutuelle(id:int):
    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {db_name}.DTWAGEN AS MUT WHERE MUT.AGEN_ID = {str(id)}")
        row = cursor.fetchone()
        if row is None or len(row) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"Mutuelle N°<{id}> not found.")
        
        header1 = ["id","libelle","portefeuille"]
        return {"mutuelle": dict(zip(header1,row))}
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")

# @app.get("/produit/{id:int}", summary="Consulter les informations d'un produit",
#     description=f"""## GET PRODUIT
# Cette méthode prend en paramètre un code de produit (un entier positif )
# et renvoie:
# un code de status ainsi que le produit""")
def get_produit(id:int):
    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {db_name}.DTWPRDT AS PRDT WHERE PRDT.PRDT_ID = {str(id)}")
        row = cursor.fetchone()
        if row is None or len(row) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"PRODUIT N°<{id}> not found.")
        header1 = ["id","produit","option","libelle","libelle_court","code_famille","famille","type_gamme","date_ins","date_modif"]
        return {"produit": dict(zip(header1,row))}
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")

# @app.get("/categorie/{code:str}", summary="Consulter les informations d'une catégorie",
#     description=f"""## GET CATEGORIE
# Cette méthode prend en paramètre un code de catégorie (une chaine de caractères)
# et renvoie:
# un code de status ainsi que la catégorie""")
def get_categorie(code:str):
    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM {db_name}.DTWCATG AS CATG WHERE CATG.CATG_CODE = '{code}'"
        try:
            cursor.execute(query)
        except Exception as e:
             return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=""f"Erreur de connexion à la BDD: {e}")
        row = cursor.fetchone()
        if row is None or len(row) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"CATEGORIE CODE <{code}> not found.")
        header1 = ["code","libelle","grd_college","famille_coti"]
        return {"categorie": dict(zip(header1,row))}
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")

# @app.get("/beneficiaires/{id:int}", summary="Consulter la liste des bénéficiaires",
#     description=f"""## GET BENEFICIAIRE
# Cette méthode prend en paramètre un numéro d'assuré (un entier positif )
# et renvoie:
# un code de status ainsi que la liste des bénéficiaires""")
# def get_beneficiaires(id:int):
#     # Beneficiaire.parse_obj(row)
#     return []


# def check_database():
#     try:
#         connection = connect_to_as400()
#         if connection:
#             return True
#         return False
#     except:
#         return False

# def check_docs():
#     try:
#         response = requests.get('/docs')
#         return response.status_code == 200
#     except:
#         return False
    
@app.get("/healthcheck", status_code=200)
def healthcheck():
    # conn = connect_to_as400()
    # if conn:
    return {"status": "ok"}
    # return {"status": "ko", "message": "Database connection failed."}
    # return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="API is down. Checkout logs for more details.")
    