from programme.base_donnee import connexion
import pymysql
from decimal import Decimal,InvalidOperation


def get_fichier_from_db(nom):
    try:
        with connexion() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT fichier_data, fichier_mimetype, fichier_path 
                    FROM documents_lotissement WHERE fichier_path = %s
                    UNION ALL
                    SELECT fichier_data, fichier_mimetype, fichier_path 
                    FROM documents_lot WHERE fichier_path = %s
                """
                cursor.execute(sql, (nom, nom))
                return cursor.fetchone()
    except Exception as e:
        print("Erreur get_fichier_from_db :", e)
        return None

def Convertiseur(valeur):
    metre_carre=0
    metre_carre=Decimal(valeur)*10000
    return  metre_carre

def Decoupage(superficie_totale, taille_lot):
    try:
        superficie = Decimal(str(superficie_totale))
        taille = Decimal(str(taille_lot))
    except InvalidOperation:
        return None, None  

    if superficie <= 0 or taille <= 0:
        return None, None  

    nombre_lot = int(superficie // taille)
    reste = superficie % taille

    return nombre_lot, reste  

def Creat_Lotissement(Localite, Nom_Projet, Superficie, Nombre_iLots, Nombre_Lots, Status, Date, id, agences):
    try:
        Superficie = Decimal(str(Superficie))
        Nombre_Lots = int(Nombre_Lots) or 0
        Nombre_iLots = int(Nombre_iLots) or 0
        valeur = Convertiseur(Superficie)

        with connexion() as conn:
            with conn.cursor() as cursor:

                # Vérifier si le lotissement existe
                cursor.execute("""
                    SELECT superficie_totale, nombre_ilots, nombre_lots
                    FROM lotissements
                    WHERE id=%s AND agence_id=%s
                """, (id, agences))

                existe = cursor.fetchone()

                if not existe:
                    # ── Création du lotissement ──────────────────────────────
                    cursor.execute("""
                        INSERT INTO lotissements
                        (agence_id, localite_id, nom_projet,
                         superficie_totale, nombre_ilots, nombre_lots, statut, date)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING id
                    """, (agences, Localite, Nom_Projet,
                          valeur, Nombre_iLots, Nombre_Lots, Status, Date))

                    lotissement_id = cursor.fetchone()[0]

                    # ── Création automatique des îlots ───────────────────────
                    _creer_ilots(cursor, lotissement_id, Nom_Projet, Nombre_iLots, agences)

                    # ── Mise à jour superficie localité ──────────────────────
                    cursor.execute("""
                        UPDATE localites
                        SET superficie_totale = COALESCE(superficie_totale, 0) + %s
                        WHERE id=%s
                    """, (valeur, Localite))

                else:
                    ancienne_superficie  = existe[0]
                    ancien_nombre_ilots  = existe[1]

                    # ── Mise à jour du lotissement ───────────────────────────
                    cursor.execute("""
                        UPDATE lotissements
                        SET localite_id=%s, nom_projet=%s, superficie_totale=%s,
                            nombre_ilots=%s, nombre_lots=%s, statut=%s, date=%s
                        WHERE id=%s AND agence_id=%s
                    """, (Localite, Nom_Projet, valeur,
                          Nombre_iLots, Nombre_Lots, Status, Date,
                          id, agences))

                    # ── Synchronisation des îlots si le nombre a changé ──────
                    _synchroniser_ilots(cursor, id, Nom_Projet, agences, ancien_nombre_ilots, Nombre_iLots)

                    # ── Ajustement superficie localité ───────────────────────
                    difference = Superficie - ancienne_superficie
                    cursor.execute("""
                        UPDATE localites
                        SET superficie_totale = COALESCE(superficie_totale, 0) + %s
                        WHERE id=%s
                    """, (difference, Localite))

            conn.commit()
            return True

    except Exception as e:
        print(f"Erreur Creat_Lotissement : {e}")
        return False

def _creer_ilots(cursor, lotissement_id: int, nom_projet: str, nombre: int, agence_id: int) -> None:
    """Insère `nombre` îlots numérotés pour un lotissement donné."""
    if nombre <= 0:
        return

    ilots = [
        (
            agence_id,
            lotissement_id,
            f"{nom_projet}-I{str(i).zfill(2)}",
            "Disponible",
            f"Ilot créé automatiquement lors de la création du lotissement {nom_projet}"
        )
        for i in range(1, nombre + 1)
    ]

    # DEBUG — à retirer une fois le problème résolu
    print(f"[DEBUG] Données à insérer : {ilots}")

    try:
        cursor.executemany("""
            INSERT INTO ilots (agence_id, lotissement_id, nom_ilot, statut, description)
            VALUES (%s, %s, %s, %s, %s)
        """, ilots)

        # Vérification immédiate après insertion
        cursor.execute("""
            SELECT id, nom_ilot, statut, description
            FROM ilots
            WHERE lotissement_id = %s
        """, (lotissement_id,))

        inseres = cursor.fetchall()
        print(f"[DEBUG] Îlots insérés en base : {inseres}")

    except Exception as e:
        print(f"[ERREUR] Insertion îlots échouée : {e}")
        raise

def _synchroniser_ilots(cursor, lotissement_id: int, nom_projet: str,
                         agence_id: int, ancien: int, nouveau: int) -> None:
    """
    Met les îlots en cohérence après une modification du nombre :
      • nouveau > ancien  → crée les îlots manquants
      • nouveau < ancien  → supprime les îlots en excès (sans lots associés)
      • nouveau == ancien → rien à faire
    """
    if nouveau == ancien:
        return

    if nouveau > ancien:
        ilots_a_ajouter = [
            (agence_id, 
             lotissement_id, 
             f"{nom_projet}-I{str(i).zfill(2)}",
             "Disponible",
            f"Ilot créé automatiquement lors de la création du lotissement {nom_projet}"
             )
            for i in range(ancien + 1, nouveau + 1)
        ]
        cursor.executemany("""
            INSERT INTO ilots (agence_id, lotissement_id, nom_ilot, statut, description)
            VALUES (%s, %s, %s, %s, %s)
        """, ilots_a_ajouter)

    else:
        # Supprimer les îlots en excès sans lots associés
        # On identifie les îlots à supprimer par leur nom_ilot (ex: PROJET-I05, I06...)
        ilots_a_supprimer = [
            f"{nom_projet}-I{str(i).zfill(2)}"
            for i in range(nouveau + 1, ancien + 1)
        ]
        cursor.executemany("""
            DELETE FROM ilots
            WHERE lotissement_id = %s
              AND nom_ilot = %s
              AND id NOT IN (
                  SELECT DISTINCT ilot_id FROM lots WHERE ilot_id IS NOT NULL
              )
        """, [(lotissement_id, nom) for nom in ilots_a_supprimer])

def Creat_ilot(lotissement, superficie, statut, description, decoupage=None, id=None):
    try:
        superficie = Decimal(str(superficie))
    except Exception:
        return "Erreur : superficie invalide"

    if superficie <= 0:
        return "Erreur : la superficie doit être positive"

    # Validation du découpage uniquement s'il est fourni
    decoupage_nombre, decoupage_rest = None, None
    if decoupage:
        try:
            decoupage = Decimal(str(decoupage))
        except Exception:
            return "Erreur : valeur de découpage invalide"

        decoupage_nombre, decoupage_rest = Decoupage(superficie, decoupage)
        if decoupage_nombre is None:
            decoupage_nombre, decoupage_rest = None, None

    try:
        with connexion() as conn:
            with conn.cursor() as cursor:

                # --- Récupération du lotissement ---
                cursor.execute(
                    "SELECT superficie_totale, nom_projet, agence_id FROM lotissements WHERE id=%s",
                    (lotissement,)
                )
                lot_row = cursor.fetchone()
                if not lot_row:
                    return "Lotissement introuvable"

                lot_sup, nom_projet, agence_id = lot_row

                # --- Vérification de la superficie totale ---
                if id:
                    cursor.execute(
                        "SELECT COALESCE(SUM(superficie), 0) FROM ilots WHERE lotissement_id=%s AND id!=%s",
                        (lotissement, id)
                    )
                else:
                    cursor.execute(
                        "SELECT COALESCE(SUM(superficie), 0) FROM ilots WHERE lotissement_id=%s",
                        (lotissement,)
                    )

                sum_existing = Decimal(str(cursor.fetchone()[0] or 0))

                if lot_sup and (sum_existing + superficie) > Decimal(str(lot_sup)):
                    return "Erreur : la superficie dépasse celle du lotissement"

                # --- INSERT ou UPDATE de l'îlot ---
                if not id:
                    cursor.execute(
                        "SELECT COUNT(*) FROM ilots WHERE lotissement_id=%s",
                        (lotissement,)
                    )
                    count = cursor.fetchone()[0]
                    nom_ilot = f"{nom_projet}-I{str(count + 1).zfill(2)}"

                    cursor.execute("""
                        INSERT INTO ilots (agence_id, lotissement_id, nom_ilot, nombre_lot,superficie, statut, description)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (agence_id, lotissement, nom_ilot, int(decoupage_nombre) if decoupage_nombre else 0,superficie, statut, description))

                    ilot_id = cursor.lastrowid

                else:
                    cursor.execute("""
                        UPDATE ilots SET nombre_lot=%s, superficie=%s, statut=%s, description=%s WHERE id=%s
                    """, (int(decoupage_nombre) if decoupage_nombre else 0, superficie, statut, description, id))

                    ilot_id = id

                    cursor.execute("SELECT nom_ilot FROM ilots WHERE id=%s", (id,))
                    row = cursor.fetchone()
                    if not row:
                        return "Erreur : îlot introuvable après mise à jour"
                    nom_ilot = row[0]
                    
                    # Supprimer les anciens lots avant de recréer le découpage
                    cursor.execute("DELETE FROM lots WHERE ilot_id=%s", (ilot_id,))
                    # return f"redution{decoupage_nombre}"    
    

                # --- Découpage en lots (optionnel) ---
                if decoupage_nombre:
                    cursor.execute("SELECT COUNT(*) FROM lots WHERE ilot_id=%s", (ilot_id,))
                    count = cursor.fetchone()[0]

                    lots_to_insert = []

                    for i in range(int(decoupage_nombre)):
                        nom_lot = f"{nom_ilot}-L{str(count + i + 1).zfill(2)}"
                        lots_to_insert.append((agence_id, ilot_id, nom_lot,decoupage, statut))

                    if decoupage_rest > 0:
                        nom_lot = f"{nom_ilot}-L{str(count + decoupage_nombre + 1).zfill(2)}"
                        lots_to_insert.append((agence_id, ilot_id, nom_lot, decoupage_rest, statut))
                       

                    if lots_to_insert:
                        cursor.executemany("""
                            INSERT INTO lots (agence_id, ilot_id, numero_lot, superficie, statut)
                            VALUES (%s, %s, %s, %s, %s)
                        """, lots_to_insert)
                            

            conn.commit()
            return True

    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")
        return False

    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")
        return False

def Creat_lot(ilot_id, superficie, statut, agence_id, prix, id=None):
    
    try:
        superficie = Decimal(str(superficie))

        with connexion() as conn:
            with conn.cursor() as cursor:

                # Vérifier si le lot existe
                existe = 0
                if id is not None:
                    cursor.execute("SELECT COUNT(*) FROM lots WHERE id = %s", (id,))
                    existe = cursor.fetchone()[0]


                # Récupérer le real_ilot_id
                if existe:
                    # Modification : récupérer l'ilot_id depuis le lot
                    cursor.execute("SELECT ilot_id FROM lots WHERE id = %s", (id,))
                    real_ilot_id = cursor.fetchone()[0]
                else:
                    # Création : ilot_id peut être un id numérique OU un nom_ilot
                    cursor.execute(
                        "SELECT id FROM ilots WHERE (id = %s OR nom_ilot = %s) AND agence_id = %s",
                        (ilot_id, ilot_id, agence_id)
                    )
                    ilot_row = cursor.fetchone()
                    if not ilot_row:
                        return f"Erreur: îlot '{ilot_id}' introuvable pour cette agence."
                    real_ilot_id = ilot_row[0]


                # Récupérer la superficie de l'îlot
                cursor.execute("SELECT superficie, nom_ilot FROM ilots WHERE id = %s", (real_ilot_id,))
                ilot_row = cursor.fetchone()
                ilot_sup = Decimal(str(ilot_row[0])) if ilot_row and ilot_row[0] is not None else None
                nom_ilot = ilot_row[1] if ilot_row else "LOT"


                # Calculer la somme des superficies des autres lots
                if existe:
                    cursor.execute(
                        "SELECT COALESCE(SUM(superficie), 0) FROM lots WHERE ilot_id = %s AND id != %s",
                        (real_ilot_id, id),
                    )
                else:
                    cursor.execute(
                        "SELECT COALESCE(SUM(superficie), 0) FROM lots WHERE ilot_id = %s",
                        (real_ilot_id,),
                    )

                sum_existing = Decimal(str(cursor.fetchone()[0] or 0))
                new_total = sum_existing + superficie

                # Validation superficie
                if ilot_sup is not None and new_total > ilot_sup:
                    return (
                        f"Erreur: la somme des superficies des lots ({new_total}) "
                        f"dépasse celle de l'îlot ({ilot_sup})"
                    )

                # Mise à jour ou création
                if existe:
                    cursor.execute(
                        "UPDATE lots SET superficie=%s, statut=%s, prix_total=%s WHERE id=%s",
                        (superficie, statut, prix, id),
                    )
                else:
                    cursor.execute(
                        "SELECT COUNT(*) FROM lots WHERE ilot_id = %s", (real_ilot_id,)
                    )
                    count = cursor.fetchone()[0] or 0
                    nom_lot = f"{nom_ilot}-L{str(count + 1).zfill(2)}"

                    cursor.execute(
                        """
                        INSERT INTO lots (agence_id, ilot_id, numero_lot, superficie, statut, prix_total)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (agence_id, real_ilot_id, nom_lot, superficie, statut, prix),
                    )

            conn.commit()
            return True

    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")
        return False

def Creat_Achats(code, Montant,date,Desciption,id):
    try:
        with connexion() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Achats WHERE id_Achats = %s", (id,))
                result = cursor.fetchone()
                existe = result[0] if result and result[0] else 0
                if existe:
                    sql_mj = """UPDATE Achats
                    SET Montant=%s,  date=%s, description=%s
                    WHERE id_Achats=%s
                    """
                    cursor.execute(sql_mj, (Montant, date, Desciption, id))
                    return f"Modification reussie avec success"
                else:
                    sql = "INSERT INTO Achats(code_achats, Montant,date,description) VALUES(%s, %s, %s, %s)"
                    cursor.execute(sql, (code, Montant, date, Desciption))

                conn.commit()
                return f"Insertion reussie avec success"
    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")
        return False
 
def creat_historique(fichier, utilisateur,id_utilisateur,type):
    try:
        with connexion() as conn:
            with conn.cursor() as curseur:
                sql = "INSERT INTO rapports (fichier, utilisateur,id_utilisateur,type) VALUES (%s, %s, %s, %s)"
                curseur.execute(sql, (fichier, utilisateur,id_utilisateur,type))
            conn.commit()
            return True
    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")
        return False

def Creat_Client(code_client,agences,Nom,Prenom,telephone,adresse, email,carte_cni,date):
    try:
        with connexion() as conn:
            with conn.cursor() as curseur:
                curseur.execute("SELECT COUNT(*) FROM clients WHERE email = %s", (email,))
                existe = curseur.fetchone()[0]

                if existe:
                    sql = """
                    UPDATE clients
                    SET agence_id=%s,Nom=%s, code_client=%s, Prenom=%s, telephone=%s, adresse=%s, email=%s, CNI=%s,  date=%s
                    WHERE  email=%s
                    """
                    curseur.execute(sql,(agences ,Nom, code_client, Prenom,telephone,adresse, email, carte_cni, date, email))
                else:
                    sql = """
                    INSERT INTO clients (agence_id, Nom, code_client, Prenom, telephone, adresse, email, CNI, date)
                    VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    curseur.execute(sql, (agences,Nom, code_client, Prenom,telephone,adresse, email, carte_cni,  date))

            conn.commit()
    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")

def Creat_Vente(lot_id, client_id, prix_vente, date_vente, agence_id, code_vente, vente_id=None):
    try:
        with connexion() as conn:
            with conn.cursor() as curseur:
                curseur.execute("SELECT COUNT(*) FROM ventes WHERE id = %s", (vente_id,))
                existe = curseur.fetchone()[0]

                if existe:
                    # Récupérer l'ancien lot_id avant modification
                    curseur.execute("SELECT lot_id FROM ventes WHERE id = %s", (vente_id,))
                    ancien_lot = curseur.fetchone()
                    ancien_lot_id = ancien_lot[0] if ancien_lot else None

                    # Mettre à jour la vente
                    sql = """
                        UPDATE ventes
                        SET lot_id=%s, client_id=%s, prix_vente=%s, date_vente=%s, agence_id=%s
                        WHERE id=%s
                    """
                    curseur.execute(sql, (lot_id, client_id, prix_vente, date_vente, agence_id, vente_id))

                    # Si le lot a changé, remettre l'ancien en Disponible
                    if ancien_lot_id and ancien_lot_id != lot_id:
                        curseur.execute(
                            "UPDATE lots SET statut='Disponible', vendu=0 WHERE id=%s",
                            (ancien_lot_id,)
                        )

                    # Marquer le nouveau lot comme Vendu
                    curseur.execute(
                        "UPDATE lots SET statut='Vendu', vendu=1 WHERE id=%s",
                        (lot_id,)
                    )

                else:
                    # Insertion nouvelle vente
                    sql = """
                        INSERT INTO ventes (lot_id, client_id, prix_vente, date_vente, agence_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    curseur.execute(sql, (lot_id, client_id, prix_vente, date_vente, agence_id))

                    # Marquer le lot comme Vendu
                    curseur.execute(
                        "UPDATE lots SET statut='Vendu', vendu=1 WHERE id=%s",
                        (lot_id,)
                    )

            conn.commit()
    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")

def cret_User(nom, email, role, agence, password, id=None):
    try:
        with connexion() as conn:
            with conn.cursor() as curseur:
                # determine whether we're updating an existing user
                existe = 0
                if id is not None:
                    curseur.execute("SELECT COUNT(*) FROM utilisateurs WHERE id = %s", (id,))
                    existe = curseur.fetchone()[0]

                if existe:
                    sql = """
                    UPDATE utilisateurs
                    SET nom=%s, email=%s, role=%s, agence_id=%s
                    WHERE id=%s
                    """
                    curseur.execute(sql, (nom, email, role, agence, id))
                else:
                    sql = """
                    INSERT INTO `utilisateurs` (`nom`, `email`, `role`, `agence_id`, `mpd`)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    curseur.execute(sql, (nom, email, role, agence, password))
                    print("Nouvel utilisateur inséré avec succès.")
            conn.commit()
    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")

def Creat_document_lot(lot_id, nom_fichier, type_doc, code_doc, fichier_data, fichier_mimetype):
    try:
        with connexion() as conn:
            with conn.cursor() as curseur:
                sql = """
                INSERT INTO documents_lot 
                (lot_id, type_document, numero, fichier_path, fichier_data, fichier_mimetype)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                curseur.execute(sql, (lot_id, type_doc, code_doc, nom_fichier, fichier_data, fichier_mimetype))
            conn.commit()
    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")

def Creat_document(lotissement_id, nom_fichier, type_doc, code_doc, fichier_data, fichier_mimetype):
    try:
        with connexion() as conn:
            with conn.cursor() as curseur:
                sql = """
                INSERT INTO documents_lotissement 
                (lotissement_id, fichier_path, type_document, numero, fichier_data, fichier_mimetype)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                curseur.execute(sql, (lotissement_id, nom_fichier, type_doc, code_doc, fichier_data, fichier_mimetype))
            conn.commit()
    except pymysql.MySQLError as e:
        print(f"Erreur MySQL : {e}")