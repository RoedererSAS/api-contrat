from pydantic import BaseModel


class Beneficiaire(BaseModel):
    id: str
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
    header1 = ['id', 'cntr_id', 'pers_id', 'date_debut', 'date_fin', 'statut', 'motif_debut', 'motif_fin', 'mod_paiemt', 'freq_paiemt', 'exo_coti', 'parent_id', 'valide_du', 'createur', 'date_ins ', 'date_modif']
    header2 = ["pers_id","numero","matricule","numero_ss","nom","prenom","patronyme","date_naiss","regime","grand_regime","sexe","type","rang_jumeau","situation_fam","teletrans","alert_mail","date_cpte_cli","rue_ligne1","rue_ligne2","rue_ligne3","cp","ville","pays","date_adr","email","tel_fixe","tel_mobile","parent_id","date_creation","aut_prelev","date_ins","date_modif"]
    id: int
    exercice: str
    date_effet: str
    demat_active: str
    date_activation: str
    entreprise: str
    categorie: str
    code_compagnie: str
    numero_periodetp: str
    numero_adherent: str
    civilite: str
    nom: str
    numerosecu: str
    datedebutval: str
    datefinval: str
    prenom: str
    ladresse1: str
    ladresse2: str
    ladresse3: str
    codepostalville: str
    pays: str
    telephone: str
    email: str
    numerofabrication: str
    datamatrix: str
    formule: str
    beneficiaires: list

class Entreprise(BaseModel):
    id:int
    categorie: str
