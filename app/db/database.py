#!/usr/bin/python3

import pyodbc
import logging 
import os
# from dotenv import load_dotenv
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# load_dotenv(dotenv_path)


logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG,
                    filename='app.log',
                    format='%(asctime)s:%(levelname)s:%(message)s',)


def connect_to_as400():
    """
    Se connecte à une base AS400 via pyodbc.
    
    :param system: Adresse IP ou nom du système AS400
    :param username: Nom d'utilisateur pour la connexion
    :param password: Mot de passe pour la connexion
    :param driver: Driver ODBC pour AS400
    :return: Connexion à la base de donnéescd app   
    """
    login=os.getenv('CW_AS400_USER_ID')
    password=os.getenv("CW_AS400_USER_PWD")
    try:
        logging.info("Tentative de connexion à AS400...")
        # Construire la chaîne de connexion
        connection_string = (
            f"DRIVER=IBM i Access ODBC Driver;"  # Driver ODBC pour AS400
            f"SYSTEM=10.10.44.153;"  # Adresse IP ou nom du système AS400
            f"UID={login};"  # Remplacez par votre nom d'utilisateur
            f"PWD={password};"  # Remplacez par votre mot de passe
        )
        # Établir la connexion
        # print(connection_string)
        connection = pyodbc.connect(connection_string, autocommit=True, readonly=True)
        logging.debug(connection_string)
        logging.info("Connexion réussie à AS400 !")
        return connection
    except pyodbc.Error as e:
        logging.error("Erreur lors de la connexion à AS400 : ", e)
        return None