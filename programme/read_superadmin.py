import pymysql
from programme.base_donnee import connexion

def Card_data(agence_id):
    data_base = connexion()
    try:
        with data_base.cursor() as cursor:

            Localité_sql = """SELECT COUNT(Distinct id) AS total_localite FROM localites WHERE agence_id=%s"""
           
            ilot_sql = """SELECT COUNT(Distinct id) AS total_ilots FROM ilots WHERE agence_id=%s;"""
            
            lot_sql = """ SELECT COUNT(Distinct id) AS total_lots FROM lots WHERE agence_id=%s;"""
            
            Client_sql =""" SELECT COUNT(Distinct id) AS total_clients FROM clients WHERE agence_id=%s;"""

            lotissment_sql = """ SELECT COUNT(Distinct id) AS total_lotissements FROM lotissements WHERE agence_id=%s;"""

            ventes_sql =""" SELECT COUNT(Distinct id) AS total_ventes FROM ventes WHERE agence_id=%s;"""

            Prevision_sql ="""SELECT SUM(prix_total) AS Previsions FROM lots WHERE agence_id=%s;"""
            
            revenue_sql = """SELECT SUM(prix_vente) AS Revenu FROM ventes WHERE agence_id=%s;"""
            
            activite_sql="""
            SELECT
            ventes.id,
            clients.nom AS client_nom,
            clients.prenom AS client_prenom,
            lots.numero_lot,
            ventes.prix_vente,
            ventes.date_vente,
            lots.superficie
            FROM ventes
            JOIN clients ON ventes.client_id = clients.id
            JOIN lots ON ventes.lot_id = lots.id
            JOIN agences ON ventes.agence_id = agences.id
            JOIN ilots ON lots.ilot_id=ilots.id
            where ventes.agence_id=%s
            ORDER BY ventes.id DESC
            """
            
            propriete_sql="""
                 SELECT nom_ilot,numero_lot,lots.superficie,lots.statut,lots.prix_total,lots.id
                   FROM `lots`
                   JOIN ilots ON lots.ilot_id=ilots.id
                     JOIN agences ON lots.agence_id=agences.id
                     WHERE lots.agence_id=%s
                   ORDER BY lots.id DESC
                   Limit 10
               """
            chart_revenue_sql="""
            SELECT 
            l.nom_projet AS lotissements,
            SUM(v.prix_vente) AS revenu
            FROM ventes v
            JOIN lots lo ON v.lot_id = lo.id
            JOIN ilots i ON lo.ilot_id = i.id
            JOIN lotissements l ON i.lotissement_id = l.id
            WHERE v.agence_id = %s
            GROUP BY l.id, l.nom_projet
            ORDER BY l.nom_projet;
            """
           
            # --- Exécution ---
            cursor.execute(Localité_sql, (agence_id,))
            total_localité = cursor.fetchone()[0]

            cursor.execute(ilot_sql, (agence_id,))
            total_ilots = cursor.fetchone()[0]

            cursor.execute(lot_sql, (agence_id,))
            total_lot = cursor.fetchone()[0]

            cursor.execute(Client_sql, (agence_id,))
            total_clients = cursor.fetchone()[0]

            cursor.execute(lotissment_sql, (agence_id,))
            total_lotissement = cursor.fetchall()

            cursor.execute(ventes_sql, (agence_id,))
            total_ventes = cursor.fetchone()[0]

            cursor.execute(Prevision_sql, (agence_id,))
            total_Prevision = cursor.fetchone()[0]

            cursor.execute(revenue_sql, (agence_id,))
            total_revenue = cursor.fetchone()[0]

            cursor.execute(activite_sql, (agence_id,))
            derniere_activite = cursor.fetchall()

            cursor.execute(propriete_sql, (agence_id,))
            propriete = cursor.fetchall()
            cursor.execute(chart_revenue_sql, (agence_id,))
            chart_revenue = cursor.fetchall()

            return (
                total_localité,
                total_ilots,
                total_lot,
                total_clients,
                total_lotissement,
                total_ventes,
                total_Prevision,
                total_revenue,
                derniere_activite,
                propriete,
                chart_revenue
            )

    except Exception as e:
        print("Erreur lors de la lecture des données du tableau de bord (Admin) :", e)
        return (0, 0, 0,0, 0, 0, 0,0, [], [], [])
    except pymysql.MySQLError as e:
        print("Erreur lors de la lecture des données sql :", e)
        return (0, 0, 0,0, 0, 0, 0,0, [], [], [])

# def read_admin_presence():
#     try:
#         with connexion() as conn:
#             with conn.cursor() as cursor:
#                 sql="""SELECT
#     pr.professeur_code,
#     pr.professeur_nom,
#     arrivee,
#     depart,
#     p.jour_pointage,
#     DATE(p.date_pointage) AS date_pointage,
#     Duree_initial,
#     pp.Status,
#     pr.heure_arrivee,
#     TIMEDIFF(depart,arrivee) AS temps_presence
#     FROM pointage_programe pp
#     JOIN Programme pr ON pr.IDProgramme = pp.IDProgramme
#     JOIN pointages p ON pp.IDPointage = p.id
#     GROUP BY pr.professeur_code, pr.professeur_nom, DATE(p.date_pointage)
#     ORDER BY p.date_pointage DESC, temps_presence;
#                       """
#                 cursor.execute(sql)
#                 return cursor.fetchall()
#     except pymysql.MySQLError as e:
#         print("Erreur MySQL :", e)
#         return []
#     except Exception as e:
#         print("Erreur générale :", e)
#         return []

# def pointage_admin_invalid():
#     try:
#         with connexion() as conn:
#             with conn.cursor() as cursor:
#                 sql = """SELECT 
#     p.professeur_code,
#     p.professeur_nom,
#     DATE(ptg.date_pointage),
#     po.idPointeuse,
#     TIME(ptg.date_pointage) AS heure_pointage,
#     p.heure_arrivee,
#     p.heure_depart,
#     p.duree_cours,
#     ptg.jour_pointage
#     FROM Programme p
#     INNER JOIN pointages ptg ON p.professeur_code = ptg.IDEmploye
#     AND DATE(ptg.date_pointage) =CURDATE() AND ptg.jour_pointage=p.jour
#     INNER JOIN pointeuse po ON po.idPointeuse = ptg.idPointeuse
#     INNER JOIN section s ON s.idPointeuse = po.idPointeuse
#     GROUP BY 
#     p.professeur_code,
#     p.professeur_nom
#     HAVING COUNT(DISTINCT ptg.id)=1
#     ORDER BY p.professeur_code
#                 """
#                 cursor.execute(sql)
#                 return cursor.fetchall()
#     except pymysql.MySQLError as e:
#         print("Erreur MySQL :", e)
#         return []

# def generer_presence_idemployee(date_debut, date_fin,idemployee):
#     try:
#         with connexion() as conn:
#             with conn.cursor() as cursor:
#                 sql = """
#                 SELECT 
#     pr.professeur_nom,jour_pointage,
#     DATE(p.date_pointage) AS date_pointage,
#     s.NomSection as Section,
#     SEC_TO_TIME(SUM(TIME_TO_SEC(pr.duree_cours))) AS total_heures_cours,
#     SEC_TO_TIME(SUM(TIME_TO_SEC(pp.Duree_finale))) AS total_heures_effectuer,
#     SEC_TO_TIME(SUM(TIME_TO_SEC(pp.Duree_finale)) - SUM(TIME_TO_SEC(pr.duree_cours))) AS ecart,
#     CASE
#         WHEN SUM(TIME_TO_SEC(pp.Duree_finale)) = SUM(TIME_TO_SEC(pr.duree_cours)) THEN 'Complet'
#         WHEN SUM(TIME_TO_SEC(pp.Duree_finale)) < SUM(TIME_TO_SEC(pr.duree_cours)) THEN 'Manque du temps'
#         WHEN SUM(TIME_TO_SEC(pp.Duree_finale)) > SUM(TIME_TO_SEC(pr.duree_cours)) THEN 'Excédent'
#         ELSE 'Non défini'
#     END AS observation
#     FROM pointage_programe pp
#     JOIN Programme pr ON pr.IDProgramme = pp.IDProgramme
#     JOIN pointages p ON p.id = pp.IDPointage
#     JOIN pointeuse pt on pt.idPointeuse=p.IDPointeuse
#     JOIN section s on s.idPointeuse=pt.idPointeuse
#     WHERE DATE(p.date_pointage) BETWEEN %s AND %s AND p.IDEmploye=%s
#     GROUP BY pr.professeur_nom, jour_pointage, p.date_pointage
#     ORDER BY p.date_pointage;
#                 """
#                 cursor.execute(sql, (date_debut, date_fin, idemployee))
#                 return cursor.fetchall()
#     except pymysql.MySQLError as e:
#         print("Erreur MySQL :", e)
#         return []
#     except Exception as e:
#         print("Erreur générale :", e)
#         return []

# def generer_presence_idsection(date_debut, date_fin,idsection):
#     try:
#         with connexion() as conn:
#             with conn.cursor() as cursor:
#                 sql = """
#                 SELECT
#     pr.professeur_nom,jour_pointage,
#     DATE(p.date_pointage) AS date_pointage, 
#     s.NomSection as Section,
#     SEC_TO_TIME(SUM(TIME_TO_SEC(pr.duree_cours))) AS total_heures_cours,
#     SEC_TO_TIME(SUM(TIME_TO_SEC(pp.Duree_finale))) AS total_heures_effectuer,
#     SEC_TO_TIME(SUM(TIME_TO_SEC(pp.Duree_finale)) - SUM(TIME_TO_SEC(pr.duree_cours))) AS ecart,
#     CASE
#         WHEN SUM(TIME_TO_SEC(pp.Duree_finale)) = SUM(TIME_TO_SEC(pr.duree_cours)) THEN 'Complet'
#         WHEN SUM(TIME_TO_SEC(pp.Duree_finale)) < SUM(TIME_TO_SEC(pr.duree_cours)) THEN 'Manque du temps'
#         WHEN SUM(TIME_TO_SEC(pp.Duree_finale)) > SUM(TIME_TO_SEC(pr.duree_cours)) THEN 'Excédent'
#         ELSE 'Non défini'
#     END AS observation
#     FROM pointage_programe pp
#     JOIN Programme pr ON pr.IDProgramme = pp.IDProgramme
#     JOIN pointages p ON p.id = pp.IDPointage
#     JOIN pointeuse pt on pt.idPointeuse=p.IDPointeuse
#     JOIN section s on s.idPointeuse=pt.idPointeuse
#     WHERE DATE(p.date_pointage) BETWEEN %s AND %s AND s.idSection=%s
#     GROUP BY pr.professeur_nom, jour_pointage, p.date_pointage
#     ORDER BY p.date_pointage;
#                 """
#                 cursor.execute(sql, (date_debut, date_fin, idsection))
#                 return cursor.fetchall()
#     except pymysql.MySQLError as e:
#         print("Erreur MySQL :", e)
#         return []
#     except Exception as e:
#         print("Erreur générale :", e)
#         return []

# def data_chatjs():
    try:
        data_base = connexion()
        with data_base.cursor() as cursor:
            # --- Présents aujourd’hui ---
            sql2 = """
 WITH jours AS (
    SELECT CURDATE() - INTERVAL n DAY AS jour
    FROM (
        SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 
        UNION SELECT 4 UNION SELECT 5 UNION SELECT 6
    ) AS nums
)
SELECT 
    CASE DAYOFWEEK(j.jour)
        WHEN 1 THEN 'Dimanche'
        WHEN 2 THEN 'Lundi'
        WHEN 3 THEN 'Mardi'
        WHEN 4 THEN 'Mercredi'
        WHEN 5 THEN 'Jeudi'
        WHEN 6 THEN 'Vendredi'
        WHEN 7 THEN 'Samedi'
    END AS jour_francais,
    COUNT(lp.IDEmploye) AS nb_presences
FROM jours j
LEFT JOIN (
    SELECT 
        IDEmploye, 
        DATE(date_pointage) AS jour_pointage
    FROM pointages
    GROUP BY IDEmploye, DATE(date_pointage)
    HAVING COUNT(*) >= 2
) AS lp
ON lp.jour_pointage = j.jour
GROUP BY j.jour
ORDER BY 
    CASE DAYOFWEEK(j.jour)
        WHEN 2 THEN 1
        WHEN 3 THEN 2
        WHEN 4 THEN 3
        WHEN 5 THEN 4
        WHEN 6 THEN 5
        WHEN 7 THEN 6
        WHEN 1 THEN 7
    END;
"""

            # --- Retardataires aujourd’hui ---
            sql3 = """WITH jours AS (
    SELECT CURDATE() - INTERVAL n DAY AS jour
    FROM (
        SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3
        UNION SELECT 4 UNION SELECT 5 UNION SELECT 6
    ) AS nums
),
retardataires AS (
    SELECT 
        p.IDEmploye,
        DATE(p.date_pointage) AS jour_pointage,
        MIN(TIME(p.date_pointage)) AS heure_arrivee_reelle,
        pr.heure_arrivee AS heure_cours
    FROM pointages p
    JOIN Programme pr 
        ON pr.professeur_code = p.IDEmploye
        AND pr.jour = CASE DAYOFWEEK(p.date_pointage)
                        WHEN 1 THEN 'Dimanche'
                        WHEN 2 THEN 'Lundi'
                        WHEN 3 THEN 'Mardi'
                        WHEN 4 THEN 'Mercredi'
                        WHEN 5 THEN 'Jeudi'
                        WHEN 6 THEN 'Vendredi'
                        WHEN 7 THEN 'Samedi'
                      END
    WHERE p.Status = 'Arrivée enregistrée'
      AND p.date_pointage >= CURDATE() - INTERVAL 6 DAY
    GROUP BY p.IDEmploye, DATE(p.date_pointage), pr.heure_arrivee
    HAVING heure_arrivee_reelle > heure_cours
)
SELECT 
    CASE DAYOFWEEK(j.jour)
        WHEN 1 THEN 'Dimanche'
        WHEN 2 THEN 'Lundi'
        WHEN 3 THEN 'Mardi'
        WHEN 4 THEN 'Mercredi'
        WHEN 5 THEN 'Jeudi'
        WHEN 6 THEN 'Vendredi'
        WHEN 7 THEN 'Samedi'
    END AS jour_francais,
    COUNT(r.IDEmploye) AS nb_retard
FROM jours j
LEFT JOIN retardataires r 
       ON r.jour_pointage = j.jour
GROUP BY j.jour
ORDER BY 
    CASE DAYOFWEEK(j.jour)
        WHEN 2 THEN 1  -- Lundi
        WHEN 3 THEN 2  -- Mardi
        WHEN 4 THEN 3  -- Mercredi
        WHEN 5 THEN 4  -- Jeudi
        WHEN 6 THEN 5  -- Vendredi
        WHEN 7 THEN 6  -- Samedi
        WHEN 1 THEN 7  -- Dimanche
    END;

"""

            # --- Absents aujourd’hui ---
            sql4 = """
 SELECT 
    CASE DAYOFWEEK(j.jour)
        WHEN 1 THEN 'Dimanche'
        WHEN 2 THEN 'Lundi'
        WHEN 3 THEN 'Mardi'
        WHEN 4 THEN 'Mercredi'
        WHEN 5 THEN 'Jeudi'
        WHEN 6 THEN 'Vendredi'
        WHEN 7 THEN 'Samedi'
    END AS jour_francais,
    COUNT(prc.IDEmploye) AS nb_absents
 FROM (
    SELECT CURDATE() - INTERVAL n DAY AS jour
    FROM (
        SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION
        SELECT 4 UNION SELECT 5 UNION SELECT 6
    ) AS nums
  ) AS j
JOIN (
    SELECT pr.professeur_code AS IDEmploye, pr.jour AS jour_cours
    FROM Programme pr
) AS prc
  ON prc.jour_cours = CASE DAYOFWEEK(j.jour)
                            WHEN 1 THEN 'Dimanche'
                            WHEN 2 THEN 'Lundi'
                            WHEN 3 THEN 'Mardi'
                            WHEN 4 THEN 'Mercredi'
                            WHEN 5 THEN 'Jeudi'
                            WHEN 6 THEN 'Vendredi'
                            WHEN 7 THEN 'Samedi'
                        END
LEFT JOIN pointages p 
       ON p.IDEmploye = prc.IDEmploye
      AND DATE(p.date_pointage) = j.jour
WHERE p.IDEmploye IS NULL
GROUP BY j.jour
ORDER BY 
    CASE DAYOFWEEK(j.jour)
        WHEN 2 THEN 1
        WHEN 3 THEN 2
        WHEN 4 THEN 3
        WHEN 5 THEN 4
        WHEN 6 THEN 5
        WHEN 7 THEN 6
        WHEN 1 THEN 7
    END;
"""
            
            cursor.execute(sql2)
            chartjs_Presents = cursor.fetchall()

            cursor.execute(sql3)
            chartjs_retard = cursor.fetchall()

            cursor.execute(sql4)
            chartjs_absents = cursor.fetchall()

            return chartjs_Presents, chartjs_retard, chartjs_absents
    except Exception as e:
        print("Erreur lors de la lecture des données pour le graphique :", e)
        return [], [], []

# def read_pointage():
#      try:
#          with connexion() as conn:
#              with conn.cursor() as cusor:
#                  sql= """
#              SELECT DISTINCT e.Nom, p.date_pointage, p.Status,s.NomSection
#              FROM pointages p
#              JOIN empreintes e ON p.IDEmploye = e.IDEmploye
#              JOIN pointeuse pt ON pt.idPointeuse = p.idPointeuse
#              JOIN section s ON s.idPointeuse = pt.idPointeuse
#              ORDER BY p.date_pointage DESC"""
#                  cusor.execute(sql)
#                  return cusor.fetchall()
#      except pymysql.MySQLError as e:
#          print("Erreur Mysql:",e)
#          return []
#      except Exception as e:
#          print("Erreur Generele:",e)
#          return []

# def historique_data():
#     try:
#         with connexion() as conn:
#             with conn.cursor() as cursor:
#                 sql="""
#              SELECT DISTINCT e.Nom, date(p.date_pointage) as date_pointage,time(p.date_pointage) as heure_pointage, p.Status,s.NomSection
#              FROM pointages p
#              JOIN empreintes e ON p.IDEmploye = e.IDEmploye
#              JOIN pointeuse pt ON pt.idPointeuse = p.idPointeuse
#              JOIN section s ON s.idPointeuse = pt.idPointeuse
#              ORDER BY p.date_pointage DESC
#             """
#                 cursor.execute(sql)
#                 return cursor.fetchall()
#     except pymysql.MySQLError as e:
#         print("Erreur MySQL :", e)
#         return []
#     except Exception as e:
#         print("Erreur générale :", e)
#         return []
                
# def read_raports(agence_id):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql = """
                SELECT r.fichier, u.nom
                FROM rapports r
                JOIN utilisateurs u ON r.id_utilisateur = u.id
                WHERE r.agence_id = %s
                ORDER BY r.date_upload DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return []
    except Exception as e:
        print("Erreur générale :", e)
        return []