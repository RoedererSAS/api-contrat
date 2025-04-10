#!/usr/bin/python3
import os
import logging
from app.db.database import connect_to_as400
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from models import Assure, Entreprise, Contrat, Beneficiaire, Service

db_name=os.getenv("CW_AS400_DATABASE")
print(db_name)
app = FastAPI()


@app.get("/assures/{id:int}", summary="Consulter les informations d'un assuré",
    description=f"""## GET ASSURE    
Cette méthode prend en paramètre un numéro d'assuré (entier positif) 
et renvoie:
- un code de status 
- ainsi que les informations associées à l'assuré:
    - les élément d'identification de l'assuré
    - les bénéficiaires
    - les services 
    - les contrats
""")
def get_assure(id:int):
    header1 = ['id', 'cntr_id', 'pers_id', 'date_debut', 'date_fin', 'statut', 'motif_debut', 'motif_fin', 'mod_paiemt', 'freq_paiemt', 'exo_coti', 'parent_id', 'valide_du', 'createur', 'date_ins ', 'date_modif']
    header2 = ["pers_id","numero","matricule","numero_ss","nom","prenom","patronyme","date_naiss","regime","grand_regime","sexe","type","rang_jumeau","situation_fam","teletrans","alert_mail","date_cpte_cli","rue_ligne1","rue_ligne2","rue_ligne3","cp","ville","pays","date_adr","email","tel_fixe","tel_mobile","parent_id","date_creation","aut_prelev","date_ins","date_modif"]
    header = header1+header2
    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        pers_id = id*100
        cursor.execute(f"SELECT * FROM {db_name}.DTWADHE AS ADH INNER JOIN {db_name}.DTWPERS AS PERS ON ADH.ADHE_PERS_ID = PERS.PERS_ID WHERE PERS.PERS_ID = {str(pers_id)}")
        # AND (ADH.ADHE_DATE_FIN > DATE '{str(Y3_AGO)}' OR ADH.ADHE_DATE_FIN is NULL) AND PERS.PERS_TYPE='AP'
        row = cursor.fetchone()
        if row is None or len(row) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"Assuré N°<{id}> not found.")
        else:
            assure = dict(zip(header, row))
            assure["contrats"] = get_contrats(assure["cntr_id"])
        return {"assure": assure}
    
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"Erreur de connexion à la BDD")
    

@app.get("/entreprises/{id:int}", summary="Consulter les informations d'une entreprise",
    description=f"""## GET entreprise    
Cette méthode prend en paramètre un numéro d'adhérent entreprise un entier positif 
et renvoie:
un code de status ainsi que les informations associées à l'entreprise
- les element d'identification de l'assuré
- les bénéficiaires
- les services 
- les contrats
""")
def get_assure(id:int):
    return {"status": "ok"}


@app.get("/contrats/{id:int}", summary="Consulter les informations d'un contrat",
    description=f"""## GET CONTRAT
    
Cette méthode prend en paramètre un numéro de contrat (un entier positif )
et renvoie:
un code de status ainsi que les informations associées au contrat
""")
def get_contrats(id:int):
    return {"status": "ok"}

@app.get("/beneficiaires/{id:int}", summary="Consulter la liste des bénéficiaires",
    description=f"""## GET BENEFICIAIRE
Cette méthode prend en paramètre un numéro d'assuré (un entier positif )
et renvoie:
un code de status ainsi que la liste des bénéficiaires""")
def get_beneficiaires(id:int) -> list[Beneficiaire]| JSONResponse:
    Beneficiaire.parse_obj(row)
    return [Beneficiaire(), ]

@app.get("/healthcheck", status_code=200)
def healthcheck():
    return {"status": "ok"}