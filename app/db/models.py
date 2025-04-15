from pydantic import BaseModel
import datetime

class Beneficiaire(BaseModel):
    id: int
    nir: str
    type: str
    nom: str
    prenom: str
    nir: str
    date_naissance: str
    rang_jumeau: str
    date_debut: str
    date_fin: str

class Contrat(BaseModel):
    id: int
    categorie:str
    produit:str
    mutuelle:str
    mutuelle_id:str
    
class Assure(BaseModel):
    id: int
    cntr_id: int
    pers_id: int
    date_debut: datetime.date
    date_fin: str
    statut: str
    motif_debut: str
    motif_fin: str
    mod_paiemt: str
    freq_paiemt: str
    exo_coti: str
    parent_id: str
    valide_du: str
    createur: str
    date_ins : str
    date_modif: str
    pers_id: str
    numero: str
    matricule: str
    numero_ss: str
    nom: str
    prenom: str
    patronyme: str
    date_naiss: str
    regime: str
    grand_regime: str
    sexe: str
    type: str
    rang_jumeau: str
    situation_fam: str
    teletrans: str
    alert_mail: str
    date_cpte_cli: str
    rue_ligne1: str
    rue_ligne2: str
    rue_ligne3: str
    cp: str
    ville: str
    pays: str
    date_adr: str
    email: str
    tel_fixe: str
    tel_mobile: str
    parent_id: str
    date_creation: str
    aut_prelev: str
    date_ins: str
    date_modif: str
    beneficiaires: list
    contrats: list
    services: list

class Entreprise(BaseModel):
    id:int
    categorie: str
