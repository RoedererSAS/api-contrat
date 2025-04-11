#!/usr/bin/venv/python3
# MAIN API

import datetime
from app.db.database import connect_to_as400
from fastapi import FastAPI, status
import logging
import os
from dataclasses import dataclass
from fastapi.responses import JSONResponse
from datetime import date
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = FastAPI()

def cast_value(key, value):
    '''Simple method to cast value given name of the key'''
    if isinstance(value, str):
        value = value.strip()
        if "numero" or "id" or "matricule" in key:
            try:
                return (key, int(value))
            except Exception as e:
                logging.warning(e)
                return (key, value)
        if "date" in key:
            if "T" in value:
                try:
                    return (key, datetime.date.strptime(value, "%Y-%m-%dT%H-%M-%S.%Z"))
                except Exception as e:
                    pass
            try:
                return (key, datetime.date.strptime(value, "%Y-%m-%d"))
            except Exception as e:
                logging.warning(e)
                return (key, value)
    return (key, value)
    
    

def cast_dict(dict_r):
    return dict(cast_value(k,v) for k,v in dict_r.items())


@app.get("/contrats/{id:int}")
def get_contrats(id: int):
    conn = connect_to_as400()
    if conn:
        cursor = conn.cursor()
        db_name=os.getenv('CW_AS400_DATABASE')
        cursor.execute(f"SELECT * FROM {db_name}.DTWCNTR AS CNTR {db_name}.DTWENTR AS ENTR {db_name}.DTWAGEN as AGENCE {db_name}.DTWPRD AS PRD WHERE CNTR.CNTR_ID = {id} AND CNRT.AGEN_ID = ENTR.ENTR_ID AND CNRT.CNRT_ENTR_ID = ENTR.ENTR_ID")
        row = cursor.fetchall()
        contrat_h = ["cntr_id","entr_id","agen_id","catg_code","prdt_id","date_debut","date_fin","date_suspension","motif_debut","motif_fin","num_charge_cpte","charge_compte","statut","responsable","terme_appel","ordre_decptage","assistance","mode_paiement","impaye_per","impaye_mnt","date_mise_dem","exo_coti","date_modif_erp","date_arrete","date_ins","date_modif"]
        if len(row) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"Le ou les contrats pour l'adhérent `{id}` not found or no longer active")
        else:
            return row

@app.get("/assures/{id:int}")
def get_adherents(id: int):
    """
    Renvoie les informations d'un ou plusieurs adhérents.

    :param int id: Le numéro d'assuré.
    """
    #L'identifiant de l'assuré correspond a l'identifiant de personne * 100
    # Parce qu'on part du principe qu'il s'agit de l'assuré principal
    # Sinon on pourrait filtrer par RANG ou par type AP: 'Assuré Principal'
    
    today = date.today()
    Y3_AGO = (today.replace(year=today.year - 3).replace(day=today.day-1)).strftime("%Y-%m-%d")    
    #COLUMN_KEYS sub ADHE_ + lower()
    header1 = ['id', 'cntr_id', 'pers_id', 'date_debut', 'date_fin', 'statut', 'motif_debut', 'motif_fin', 'mod_paiemt', 'freq_paiemt', 'exo_coti', 'parent_id', 'valide_du', 'createur', 'date_ins ', 'date_modif']
    header2 = ["pers_id","numero","matricule","numero_ss","nom","prenom","patronyme","date_naiss","regime","grand_regime","sexe","type","rang_jumeau","situation_fam","teletrans","alert_mail","date_cpte_cli","rue_ligne1","rue_ligne2","rue_ligne3","cp","ville","pays","date_adr","email","tel_fixe","tel_mobile","parent_id","date_creation","aut_prelev","date_ins","date_modif"]
    header = header1+header2
    db_name=os.getenv("CW_AS400_DATABASE")
    conn = connect()
    if conn:
        cursor = conn.cursor()
        pers_id = id*100
        cursor.execute(f"SELECT * FROM {db_name}.DTWADHE AS ADH INNER JOIN {db_name}.DTWPERS AS PERS ON ADH.ADHE_PERS_ID = PERS.PERS_ID WHERE PERS.PERS_ID = {str(pers_id)}")
        # AND (ADH.ADHE_DATE_FIN > DATE '{str(Y3_AGO)}' OR ADH.ADHE_DATE_FIN is NULL) AND PERS.PERS_TYPE='AP'
        row = cursor.fetchall()
        if row is not None or len(row) == 0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"Adhérent N°<{id}> not found.")
        
        adherents = [cast_dict(dict(zip(header, r))) for r in row]
        print(len(adherents))
        for a in adherents:
            print(a["cntr_id"])
        final_answer = dict(adherents[0] ^ adherents[1])
        # else:
        #     adherent["contrats"] = [cast_dict(dict(zip(contrat_h, r))) for r in row]
        return {"adherents": final_answer}
        
    conn.close()

@app.get("/healthcheck", status_code=200)
def healthcheck():
    return {"status":"ok"}

