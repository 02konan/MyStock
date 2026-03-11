import pymysql
import os
from dotenv import load_dotenv
load_dotenv()

# Base en production
# def connexion():
#     connection = pymysql.connect(
#         host="mysql-divix.alwaysdata.net",
#         db="divix_gestfoncier",
#         user="divix",
#         password="Biometricifsm@2025",
#         connect_timeout=10
#     )
#     return connection

def connexion():
    connection = pymysql.connect(
        host=os.getenv("APP_HOST"),
        db=os.getenv("APP_DB"),
        user=os.getenv("APP_USER"),
        password=os.getenv("APP_PASSWORD"),
        connect_timeout=10
    )
    return connection
