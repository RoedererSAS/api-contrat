#!/usr/bin/python3
import os

import logging
from app.db.database import connect_to_as400
from fastapi import FastAPI, status, Path
from typing import Optional, Union, Annotated
from fastapi.responses import JSONResponse, Response
from app.db.models import Assure, Entreprise, Contrat, Beneficiaire
from fastapi.openapi.docs import (
    get_swagger_ui_html,
)
from starlette.requests import Request
# from dotenv import load_dotenv
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# load_dotenv(dotenv_path)

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
@app.get("/adherent/{id:int}", summary="Consulter les informations d'un assuré",
    description=f"""## GET ADHERENTCette méthode prend en paramètre un numéro d'assuré principal(entier positif) 
et renvoie:
- un code de status 
- ainsi que les informations associées à l'assuré:
    - les élément d'identification de l'assuré
    - les bénéficiaires
    - les services 
    - les contrats
""")    
def get_adherent(id: Annotated[int, Path(title="Numéro de la personne assurée")]):
    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        pers_id:int = id*100
        cursor.execute(f"SELECT * FROM {db_name}.DTWADHE AS ADH WHERE ADH.ADHE_PERS_ID = {str(pers_id)}")
        rows = cursor.fetchall()
        if rows is None or len(rows) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"Adhérent N°<{id}> not found.")
        adherents = []
        contrats = set()
        parent_ids = []
        header:list = ['id', 'cntr_id', 'pers_id', 'date_debut', 'date_fin', 'statut', 'motif_debut', 'motif_fin', 'mod_paiemt', 'freq_paiemt', 'exo_coti', 'parent_id', 'valide_du', 'createur', 'date_ins ', 'date_modif']
        for row in rows:
            assure = dict(zip(header, row))
            # assure["id"] = assure["pers_id"]
            # del assure["pers_id"]
            contrats.add(get_contrat(assure["cntr_id"]))
            parent_ids.append(assure["parent_id"])
            del assure["cntr_id"]
        assure["contrats"] = contrats
        assure["parents"] = parent_ids
        return {"adherent":assure}
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")    

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
        row = cursor.fetchone()
        if row is None or len(row) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"Assuré N°<{id}> not found.")
        header1:list = ['id', 'cntr_id', 'pers_id', 'date_debut', 'date_fin', 'statut', 'motif_debut', 'motif_fin', 'mod_paiemt', 'freq_paiemt', 'exo_coti', 'parent_id', 'valide_du', 'createur', 'date_ins ', 'date_modif']
        header2:list = ["pers_id","numero","matricule","numero_ss","nom","prenom","patronyme","date_naiss","regime","grand_regime","sexe","type","rang_jumeau","situation_fam","teletrans","alert_mail","date_cpte_cli","rue_ligne1","rue_ligne2","rue_ligne3","cp","ville","pays","date_adr","email","tel_fixe","tel_mobile","parent_id","date_creation","aut_prelev","date_ins","date_modif"]
        header:list = header1+header2    
        assure = dict(zip(header, row))
        assure["contrats"] = get_contrats(assure["cntr_id"])
        assure["beneficiaires"] = []
        assure["services"] = []
        # Assure.model_validate(assure)
        return assure
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")
    

@app.get("/entreprises/{id:int}", summary="Consulter les informations d'une entreprise",
    description=f"""## GET entreprise    
Cette méthode prend en paramètre un numéro d'adhérent entreprise un entier positif 
et renvoie:
un code de status ainsi que les informations associées à l'entreprise
- les element d'identification de l'entreprise
- les assurés
- les bénéficiaires
- les services 
- les contrats
""")
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


@app.get("/contrats/{id:int}", summary="Consulter les informations d'un ou plusieurs contrats",
    description=f"""## GET CONTRAT
    
Cette méthode prend en paramètre un numéro de contrat (un entier positif )
et renvoie:
un code de status ainsi qu'un contrat
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
        entreprises = get_entreprise(contrat["entr_id"])
        if entreprises["count"] > 1:
            contrat["entreprises"]= entreprises["entreprises"]
        else:
            contrat["entreprise"]= entreprises["entreprises"][0]
        contrat["produit"] = get_produit(contrat["prdt_id"]).get("produit")
        contrat["categorie"] = get_categorie(contrat["catg_code"].strip()).get("categorie")
        contrat["mutuelle"] = get_mutuelle(contrat["agen_id"]).get("mutuelle")
        return {"contrat": contrat}
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")


@app.get("/mutuelle/{id:int}", summary="Consulter les informations d'une mutuelle",
    description=f"""## GET MUTUELLE
Cette méthode prend en paramètre un code de mutuelle (un entier positif )
et renvoie:
un code de status ainsi que la mutuelle""")
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

@app.get("/produit/{id:int}", summary="Consulter les informations d'un produit",
    description=f"""## GET PRODUIT
Cette méthode prend en paramètre un code de produit (un entier positif )
et renvoie:
un code de status ainsi que le produit""")
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

@app.get("/categorie/{code:str}", summary="Consulter les informations d'une catégorie",
    description=f"""## GET CATEGORIE
Cette méthode prend en paramètre un code de catégorie (une chaine de caractères)
et renvoie:
un code de status ainsi que la catégorie""")
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

@app.get("/beneficiaires/{id:int}", summary="Consulter la liste des bénéficiaires",
    description=f"""## GET BENEFICIAIRE
Cette méthode prend en paramètre un numéro d'assuré (un entier positif )
et renvoie:
un code de status ainsi que la liste des bénéficiaires""")
def get_beneficiaires(id:int):
    # Beneficiaire.parse_obj(row)
    return []

@app.get("/healthcheck", status_code=200)
def healthcheck():
    return {"status": "ok"}