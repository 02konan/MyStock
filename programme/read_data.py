import pymysql
from programme.base_donnee import connexion

# def Card_data(agence_id):
#     data_base = connexion()
#     try:
#         with data_base.cursor() as cursor:

#             Localité_sql = """SELECT COUNT(Distinct id) AS total_localite FROM localites WHERE agence_id=%s"""
           
#             ilot_sql = """SELECT COUNT(Distinct id) AS total_ilots FROM ilots WHERE agence_id=%s;"""
            
#             lot_sql = """ SELECT COUNT(Distinct id) AS total_lots FROM lots WHERE agence_id=%s;"""
            
#             Client_sql =""" SELECT COUNT(Distinct id) AS total_clients FROM clients WHERE agence_id=%s;"""

#             lotissment_sql = """ SELECT COUNT(Distinct id) AS total_lotissements FROM lotissements WHERE agence_id=%s;"""

#             ventes_sql =""" SELECT COUNT(Distinct id) AS total_ventes FROM ventes WHERE agence_id=%s;"""

#             Prevision_sql ="""SELECT SUM(prix_total) AS Previsions FROM lots WHERE agence_id=%s;"""
            
#             revenue_sql = """SELECT SUM(prix_vente) AS Revenu FROM ventes WHERE agence_id=%s;"""
            
#             activite_sql="""
#             SELECT
#             ventes.id,
#             clients.nom AS client_nom,
#             clients.prenom AS client_prenom,
#             lots.numero_lot,
#             ventes.prix_vente,
#             ventes.date_vente,
#             lots.superficie
#             FROM ventes
#             JOIN clients ON ventes.client_id = clients.id
#             JOIN lots ON ventes.lot_id = lots.id
#             JOIN agences ON ventes.agence_id = agences.id
#             JOIN ilots ON lots.ilot_id=ilots.id
#             where ventes.agence_id=%s
#             ORDER BY ventes.id DESC
#             """
            
#             propriete_sql="""
#                  SELECT nom_ilot,numero_lot,lots.superficie,lots.statut,lots.prix_total,lots.id
#                    FROM `lots`
#                    JOIN ilots ON lots.ilot_id=ilots.id
#                      JOIN agences ON lots.agence_id=agences.id
#                      WHERE lots.agence_id=%s
#                    ORDER BY lots.id DESC
#                    Limit 10
#                """
           
#             # --- Exécution ---
#             cursor.execute(Localité_sql, (agence_id,))
#             total_localité = cursor.fetchone()[0]

#             cursor.execute(ilot_sql, (agence_id,))
#             total_ilots = cursor.fetchone()[0]

#             cursor.execute(lot_sql, (agence_id,))
#             total_lot = cursor.fetchone()[0]

#             cursor.execute(Client_sql, (agence_id,))
#             total_clients = cursor.fetchone()[0]

#             cursor.execute(lotissment_sql, (agence_id,))
#             total_lotissement = cursor.fetchall()

#             cursor.execute(ventes_sql, (agence_id,))
#             total_ventes = cursor.fetchone()[0]

#             cursor.execute(Prevision_sql, (agence_id,))
#             total_Prevision = cursor.fetchone()[0]

#             cursor.execute(revenue_sql, (agence_id,))
#             total_revenue = cursor.fetchone()[0]

#             cursor.execute(activite_sql, (agence_id,))
#             derniere_activite = cursor.fetchall()

#             cursor.execute(propriete_sql, (agence_id,))
#             propriete = cursor.fetchall()

#             return (
#                 total_localité,
#                 total_ilots,
#                 total_lot,
#                 total_clients,
#                 total_lotissement,
#                 total_ventes,
#                 total_Prevision,
#                 total_revenue,
#                 derniere_activite,
#                 propriete
#             )

#     except Exception as e:
#         print("Erreur lors de la lecture des données du tableau de bord (Admin) :", e)
#         return (0, 0, 0,0, 0, 0, 0,0, [], [])
#     except pymysql.MySQLError as e:
#         print("Erreur lors de la lecture des données sql :", e)
#         return (0, 0, 0,0, 0, 0, 0,0, [], [])
def read_document(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT 
                        lotissements.nom_projet,
                        documents_lotissement.numero,
                        CONCAT(documents_lotissement.type_document, '(lotissement)') AS type_document,
                        documents_lotissement.fichier_path,
                        documents_lotissement.created_at AS date_document
                    FROM documents_lotissement
                    JOIN lotissements 
                        ON lotissements.id = documents_lotissement.lotissement_id
                    WHERE lotissements.agence_id = %s
                    
                    UNION ALL
                    
                    SELECT 
                        lots.numero_lot,
                        documents_lot.numero,
                        CONCAT(documents_lot.type_document, '(lot)') AS type_document,
                        documents_lot.fichier_path,
                        documents_lot.created_at AS date_document
                    FROM documents_lot
                    JOIN lots 
                        ON lots.id = documents_lot.lot_id
                    WHERE lots.agence_id = %s;
                """
                cursor.execute(sql, (code_agence, code_agence,))
                return cursor.fetchall()
    except Exception as e:
        print("Erreur :", e)
        return []
def liste_lotis(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql="""
                SELECT lotissements.id,ville,nom_projet,lotissements.superficie_totale as superficie ,nombre_lots,nombre_ilots,statut,lotissements.date as date_lotis
                FROM `lotissements`
                JOIN localites on lotissements.localite_id=localites.id
                JOIN agences on lotissements.agence_id=agences.id
                WHERE agences.id=%s;
                """
                cursor.execute(sql,(code_agence))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []

def liste_utilisateur(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql = """
                SELECT utilisateurs.nom, utilisateurs.email, mpd, 
                role.nom as role
                FROM utilisateurs
                JOIN agences ON agences.id = utilisateurs.agence_id
                JOIN role ON role.id_role = utilisateurs.role
                where agences.id=%s
                """
                cursor.execute(sql, code_agence)
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []

def liste_client(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql = """SELECT
   c.nom,
   c.prenom,
   c.code_client,
   c.email,
   c.telephone,
   c.adresse,
   c.CNI
FROM clients c
join agences on c.agence_id=agences.id
WHERE agences.id=%s
"""
                cursor.execute(sql,code_agence)
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []

def liste_localite(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql = """
                SELECT id,ville,superficie_totale,surperficie_vendue,description,status 
                FROM localites 
                WHERE agence_id=%s
                """
                cursor.execute(sql, (code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []

def liste_lots(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql = """
                   SELECT nom_ilot,numero_lot,lots.superficie,lots.statut,lots.prix_total,lots.id
                   FROM `lots`
                   JOIN ilots ON lots.ilot_id=ilots.id
                   JOIN agences ON lots.agence_id=agences.id
                   WHERE agences.id=%s 
                """
                cursor.execute(sql, (code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []

def liste_ilots(code_agence):
    """Return a list of ilots for the given agency.

    Tuple format:
        (ilot_id, lotissement_id, lotissement_name, nom_ilot,
         superficie, statut, description)
    """
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql = """
                SELECT
                    ilots.id,
                    ilots.lotissement_id,
                    lotissements.nom_projet AS lotissement_name,
                    ilots.nom_ilot,
                    ilots.superficie,
                    ilots.statut,
                    ilots.description
                FROM `ilots`
                JOIN lotissements ON ilots.lotissement_id = lotissements.id
                JOIN agences ON ilots.agence_id = agences.id
                WHERE agences.id = %s;
                """
                cursor.execute(sql, (code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []

def liste_ventes(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql = """
                SELECT
                    ventes.id,
                    clients.nom AS client_nom,
                    clients.prenom AS client_prenom,
                    lots.numero_lot,
                    ventes.prix_vente,
                    ventes.date_vente,
                    lots.superficie,
                    lots.prix_total,
                    ilots.nom_ilot,
                    clients.code_client
                FROM ventes
                JOIN clients ON ventes.client_id = clients.id
                JOIN lots ON ventes.lot_id = lots.id
                JOIN agences ON ventes.agence_id = agences.id
                JOIN ilots ON lots.ilot_id=ilots.id
                WHERE agences.id = %s;
                """
                cursor.execute(sql, (code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []

def read_idrole():
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id_role, nom FROM role")
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []

def read_idlotis(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nom_projet FROM lotissements WHERE agence_id=%s",(code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []   

def read_idlot(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT lots.id, numero_lot FROM lots WHERE lots.agence_id=%s AND lots.statut='Disponible'",(code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []   

def read_idilot(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nom_ilot FROM ilots WHERE agence_id=%s AND statut='Disponible'",(code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []   

def read_client(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nom,prenom FROM clients WHERE agence_id=%s",(code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []   

def read_idlocalite(code_agence):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, ville FROM localites WHERE Status='Actif' AND agence_id=%s",(code_agence,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []

def historique_data():
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql="""
             SELECT DISTINCT e.Nom, p.date_pointage, p.Status,s.NomSection
             FROM pointages p
             JOIN empreintes e ON p.IDEmploye = e.IDEmploye
             JOIN pointeuse pt ON pt.idPointeuse = p.idPointeuse
             JOIN section s ON s.idPointeuse = pt.idPointeuse
             ORDER BY p.date_pointage DESC
            """
                cursor.execute(sql)
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
    except Exception as e:
        print("Erreur générale :", e)
