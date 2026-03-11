import pymysql
from programme.base_donnee import connexion

def Authentification(utiliteur,mot_pass):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                sql = """
                SELECT utilisateurs.id_utilisateur as identifiants, utilisateurs.nom as nom_utilisateur, 
                role.nom as nom_roles, utilisateurs.mpd as motdepass,
                role.id_role as role_id, services.id_service as code_services
                FROM utilisateurs
                JOIN role ON utilisateurs.role = role.id_role
                JOIN services ON utilisateurs.id_service=services.id_service
                where utilisateurs.nom=%s and utilisateurs.mpd=%s
                """
                cursor.execute(sql, (utiliteur,mot_pass))
                result = cursor.fetchone()
                if result:
                    return {
                        'identifiants': result[0],
                        'nom_utilisateur': result[1],
                        'nom_roles': result[2],
                        'mot_de_passe': result[3],
                        'role_id': result[4],
                        'code_services': result[5]
                    }
                return None
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return None
    except Exception as e:
        print("Erreur générale :", e)
        return None