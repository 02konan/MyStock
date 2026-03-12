from flask import Flask, render_template, request,send_file, redirect, url_for, jsonify, send_from_directory, Response, session, flash
from programme.read_superadmin import Card_data
from programme.read_data import liste_client,liste_ventes,read_document,liste_lots,read_client,read_idlot,read_idlotis,liste_ilots,read_idrole,liste_utilisateur,liste_localite,read_idlocalite,liste_lotis
from programme.Creat_data import Creat_document,get_fichier_from_db,Creat_document_lot,Creat_Achats,Creat_Client,cret_User,Creat_Lotissement,Creat_ilot,Creat_Vente,Creat_lot
from programme.auth import Authentification
from werkzeug.utils import secure_filename
from flask_cors import CORS
from datetime import datetime,timedelta
import threading
from functools import wraps
import os
import random
import base64
import io
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='template')
app.secret_key =os.getenv("APP_SECRETKEY")
app.permanent_session_lifetime = timedelta(minutes=10)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CORS(app)
def init_session():
    if 'user_type' not in session:
        session['user_type'] = None  
    if 'section_id' not in session:
        session['section_id'] = None
    if 'professeur_code' not in session:
        session['professeur_code'] = None
    if 'connecter' not in session:
        session['connecter'] = False

@app.before_request
def before_request():
    init_session()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'connecter' not in session or not session['connecter']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'].lower() != role.lower():
                flash("Accès refusé : vous n'avez pas les droits nécessaires.", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET','POST'])
def login():
    if 'connecter' in session and session['connecter']:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        utilisateur = Authentification(username, password)
        if utilisateur:
            session.clear()
            session.permanent = True
            session['connecter'] = True
            session['username'] = username
            session['identifiant'] = utilisateur['identifiants']
            session['role'] = utilisateur['nom_roles']
            session['services'] = utilisateur['code_services']

            if utilisateur['nom_roles'].lower() == 'superadmin':
                return redirect(url_for('index'))
            elif utilisateur['nom_roles'].lower() == 'admin':
                return redirect(url_for('index'))
            else:
                return redirect(url_for('index'))
        else:
            flash("Identifiants incorrects. Veuillez réessayer.", "danger")
    return render_template('login.html')

@app.route('/')
def index():
    if 'connecter' not in session or not session['connecter']:
        return redirect(url_for('login'))

    return render_template('index.html', active_page='index')

@app.route('/api/liste_rapports')
def liste_rapports():
    try:
        if 'agences' not in session:
            return jsonify({"error": "Session expirée"}), 401

        base_list = read_document(session['agences'])
        if not base_list:
            return jsonify([])

        fichiers = []
       
        for row in base_list:
            fichier_path = row['fichier_path'] if isinstance(row, dict) else row[3]
            nom_projet   = row['nom_projet']   if isinstance(row, dict) else row[0]
            numero       = row['numero']       if isinstance(row, dict) else row[1]
            type_doc     = row['type_document']if isinstance(row, dict) else row[2]
            date_doc     = row['date_document']if isinstance(row, dict) else row[4]
            
            if not fichier_path:
                continue

            # ✅ Plus de vérification locale — on affiche tout ce qui est en DB
            fichiers.append({
                "nom": fichier_path,
                "projet": nom_projet,
                "numero": numero,
                "type": type_doc,
                "date": date_doc.strftime("%d-%m-%Y %H:%M") if date_doc else None
            })

        fichiers.sort(key=lambda x: x['date'] or '', reverse=True)
        return jsonify(fichiers)

    except Exception as e:
        print("Erreur liste_rapports :", e)
        return jsonify({"error": "Erreur serveur"}), 500

# Generale
@app.route('/api/realestate/dashboard', methods=['GET'])
@login_required
def api_realestate_dashboard():
   
    try:
        data_card=Card_data(session['agences'])
        if data_card:
            total_localité,total_ilots,total_lot,total_clients,total_lotissement,total_ventes,total_Prevision,total_revenue,derniere_activite,propriete,chart_revenue=data_card
            

            return jsonify(
                {
                 "success": True,
                 "localite_count":total_localité,
                 "ilot_count":total_ilots,
                 "properties_count": total_lotissement,
                 "tenants_count": total_clients,  
                 "monthly_income": total_Prevision,
                 "lot_count":total_lot,
                 "sales_count":total_ventes,
                 "vente_count":total_revenue,
                 "recent_transactions": [
                       {
                            "title": f" {r[1]} {r[2]}",
                            "description": f"Lot N°{r[3]} - {r[6]} m²",
                            "date": (r[5]).strftime("%d-%m-%Y"),
                            "amount": r[4]
                        }
                         for r in derniere_activite
                       ],
                 "properties": [
                     {
                         "ilot": p[0],
                         "number": p[1],
                         "surface": p[2],
                         "status": p[3],
                         "price": p[4]
                     }
                     for p in propriete
                 ],
                    "chart_revenue": [
                        {
                            "lotissements": c[0],
                            "revenue": c[1]
                        }
                        for c in chart_revenue
                    ]
                })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/historique")
def Page_Historique():
    return render_template('historique.html', active_page='historique')

# Gestion Foncier
@app.route('/Achats')
@login_required
def Page_Achats():
    data=liste_localite()
    table=[]
    for d in data:
        if not d:
            continue
        information = {
                "id": d[0] if len(d) > 0 else "",
                "code": d[1] if len(d) > 1 else "",
                "Montant": d[2] if len(d) > 2 else "",
                "date": d[3] if len(d) > 3 else "",
                "description": d[4] if len(d) > 4 else "",
            }
        table.append(information)
        
    return render_template('Achats.html', localite=table, active_page='Achats')

@app.route('/Achats',methods=['POST'])
@login_required
def enregistrement_achats():
    if request.method:
        id=request.form['id']
        code=f"Ach-{random.randint(100,999)}"
        Montant=request.form['Montant']
        Desciption=request.form['description']
        date=request.form['date']
        result=Creat_Achats(code,Montant,date,Desciption,id)
        if result is not True:
            flash(str(result),"danger")
        else:
            flash(str(result),"success")
    
    return redirect(url_for('Page_Achats'))

@app.route('/lots')
@login_required
def Page_lots():
    ilots_data = liste_ilots(session['agences'])
    lots_data = liste_lots(session['agences'])
    lots_table = []
    ilots_table = []
    

    for lot in lots_data:
        if not lot:
            continue
        lots_table.append({
            "nom_ilot": lot[0] if len(lot) > 0 else "",
            "numero_lot": lot[1] if len(lot) > 1 else "",
            "superficie": lot[2] if len(lot) > 2 else "",
            "statut": lot[3] if len(lot) > 3 else "",
            "prix": lot[4] if len(lot) > 4 else "",
            "id": lot[5] if len(lot) > 5 else "",
        })

    
    # Get all ilots for dropdown selection
    for ilot in ilots_data:
        if not ilot:
            continue
        ilots_table.append({
            "ilot_id": ilot[0] if len(ilot) > 0 else "",
            "nom_ilot": ilot[3] if len(ilot) > 3 else "",
        })


    return render_template('lots.html', active_page='lots',lots=lots_table, ilots=ilots_table)

@app.route('/lots', methods=['POST'])
@login_required
def enregistrement_lots():
    if request.method == "POST":
        id_lot = request.form.get("id_lot") or None
        ilot_id = request.form.get("id_ilot")
        superficie = request.form.get("superficie")
        statut = request.form.get("statut")
        prix= request.form.get("prix")
        result = Creat_lot(ilot_id, superficie, statut, session['agences'], prix, id_lot)
        if result is not True:
            flash(str(result), "danger")
        else:
            flash("Lot enregistré avec succès.", "success")
    return redirect(url_for('Page_lots'))

@app.route('/upload_document_lot', methods=['POST'])
def upload_document_lot():

    file = request.files.get('fichier_document')
    lot_id = request.form.get('lot_id')
    document_type = request.form.get('nom_document')
    
    if not file:
        flash("Aucun fichier envoyé.", "danger")
        return redirect(url_for('Page_lots'))
    
    if document_type is None:
        flash("Veiller remplir le champs Type document.", "danger")
        return redirect(url_for('Page_lots'))

    code_doc = document_type[:3].upper() + '-' + str(random.randint(1000, 9999))
    nom_fichier = code_doc + '_' + secure_filename(file.filename)

    # ✅ Stockage en Base64 dans la DB
    file_bytes = file.read()
    fichier_data = base64.b64encode(file_bytes).decode('utf-8')
    fichier_mimetype = file.content_type

    Creat_document_lot(lot_id, nom_fichier, document_type, code_doc, fichier_data, fichier_mimetype)

    flash("Document téléchargé avec succès.", "success")
    return redirect(url_for('Page_lots'))
 
@app.route('/ilots')
@login_required
def Page_ilots():
    data = liste_ilots(session['agences'])
    lotis_id = read_idlotis(session['agences'])
    table_idlotis = []
    table = []

    for index in data:
        if not index:
            continue
        # index is (ilot_id, lotissement_id, lotissement_name,
        #           nom_ilot, superficie, statut, description)
        information = {
            "id": index[0] if len(index) > 0 else None,
            "lotissement_id": index[1] if len(index) > 1 else None,
            "lotissement": index[2] if len(index) > 2 else "",
            "code_ilot": index[3] if len(index) > 3 else "",
            "superficie": index[4] if len(index) > 4 else "",
            "statut": index[5] if len(index) > 5 else "",
            "description": index[6] if len(index) > 6 else "",
        }
        table.append(information)
    
    for i in lotis_id:
        if not i:
            continue
        information_lotis = {
            "lotissement_id": i[0] if len(i) > 0 else "",
            "nom_lotissent": i[1] if len(i) > 1 else "",
        }
        table_idlotis.append(information_lotis)
         
    return render_template('ilots.html', active_page='ilots',ilots=table,id_lotis=table_idlotis)

@app.route('/ilots', methods=['POST'])
@login_required
def enregistrement_ilots():
   if request.method == "POST":
        id_ilot = request.form.get("id_ilot") or None
        lotissement = request.form.get("lotissement_id")
        superficie = request.form.get("superficie")
        statut = request.form.get("statut")
        description = request.form.get("description")
        decoupage = request.form.get("decoupage") or None 

        result = Creat_ilot(lotissement, superficie, statut, description, decoupage, id_ilot)

        if result is not True:
         flash(str(result), "danger")
        else:
         flash(str(result), "success")
   return redirect(url_for('Page_ilots')) 

@app.route('/Lotissement')
@login_required
def Page_Lotissement():
    try:
        data = read_idlocalite(session['agences'])
        donne=liste_lotis(session['agences'])
        table = []
        table_lotis=[]
        for index in donne:
            if not index:
                continue
            information_lotis = {
                "id":index[0] if len(index) > 0 else "",
                "ville": index[1] if len(index) > 1 else "",
                "projet": index[2] if len(index) > 2 else "",
                "superficie": index[3] if len(index) > 3 else "",
                "nombre_lots": index[4] if len(index) > 4 else "",
                "nombre_ilots": index[5] if len(index) > 5 else "",
                "status": index[6] if len(index) > 6 else "",
                "date_lotis": index[7].strftime("%d-%m-%Y") if len(index) > 7 else "",
            }
            table_lotis.append(information_lotis)
        
        for d in data:
            if not d:
                continue
            information = {
                "id": d[0] if len(d) > 0 else "",
                "ville": d[1] if len(d) > 1 else ""
            }
            table.append(information)
    except Exception as e:
        flash(f"Erreur lors du chargement des localités: {str(e)}", "danger")
    return render_template('Lotissement.html', idlocale=table,lotis=table_lotis, active_page='Lotissement')

@app.route('/Lotissement',methods=['POST'])
@login_required
def enregistrement_lotissement():
    if request.method=="POST":
        id=request.form['id']
        agences=session['agences']
        Localite=request.form['localite'] or None
        Nom_Projet=request.form['nom_pojet']
        Superficie=request.form['Superficie']
        if Superficie:
            try:
                Superficie =Superficie.replace(',', '.')
            except ValueError:
                flash("Superficie doit être un nombre valide.", "danger")
                return redirect(url_for('Page_Lotissement'))
        Nombre_iLots=request.form['nombre_ilots'] or 0
        Nombre_Lots=request.form['nombre_lots'] or 0
        if Nombre_iLots:
            try:
                Nombre_iLots = int(Nombre_iLots)
            except ValueError:
                flash("Nombre d'ilots doit être un entier valide.", "danger")
                return redirect(url_for('Page_Lotissement'))
        if Nombre_Lots:
            try:
                Nombre_Lots = int(Nombre_Lots)
            except ValueError:
                flash("Nombre de lots doit être un entier valide.", "danger")
                return redirect(url_for('Page_Lotissement'))
        Status=request.form['status']
        Date=request.form['Date']
        Creat_Lotissement(Localite,Nom_Projet,Superficie,Nombre_iLots,Nombre_Lots,Status,Date,id,agences)
    if id:
        flash(f'Lotissement {Nom_Projet} a bien été modifié',"primary")
    else:
        flash(f'Lotissement {Nom_Projet} Ajouter avec success',"success")    
    return redirect(url_for('Page_Lotissement'))

@app.route('/upload_document', methods=['POST'])
def upload_document():
    file = request.files.get('fichier_document')
    lotissement_id = request.form.get('lotissement_id')
    document_type = request.form.get('nom_document')
    code_doc = document_type[:3].upper() + '-' + str(session['agences']) + '-' + str(random.randint(1000, 9999))

    if not file:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    nom_fichier = code_doc + '_' + secure_filename(file.filename)

    # ✅ Lit et encode le fichier en Base64
    file_bytes = file.read()
    fichier_data = base64.b64encode(file_bytes).decode('utf-8')
    fichier_mimetype = file.content_type

    Creat_document(lotissement_id, nom_fichier, document_type, code_doc, fichier_data, fichier_mimetype)

    flash("Document téléchargé avec succès.", "success")
    return redirect(url_for('Page_Lotissement'))

#  Gestion Commerciale
@app.route('/Client')
@login_required
def page_Client():
    try:
        agences = session.get('agences')
        data = liste_client(agences)
        table = []
        for d in data:
            if not d:
                continue
            information = {
                "Nom": d[0] if len(d) > 0 else "",
                "Prenom": d[1] if len(d) > 1 else "",
                "Code": d[2] if len(d) > 2 else "",
                "Email": d[3] if len(d) > 3 else "",
                "telephone": d[4] if len(d) > 4 else "",
                "adresse": d[5] if len(d) > 5 else "",
                "CNI": d[6] if len(d) > 6 else "",
                "COPIE": d[7] if len(d) > 7 else "",
            }
            table.append(information)
    except Exception as e:
        flash(f"Erreur lors du chargement des clients: {str(e)}", "danger")
        table = []

    return render_template('Clients.html', active_page='Client', valeurs=table)

@app.route('/Client', methods=['POST'])
def enregistrement():
    Nom=request.form['Nom']
    Prenom=request.form['Prenom']
    telephone = request.form['telephone']
    email = request.form['email']
    carte_cni = request.form['cni']
    date = request.form['Date']
    adresse = request.form['Adresse']
    agences=session['agences']
    valeurrandom=random.randint(1000, 9999)
    code_client=f"Cli-{agences}-{valeurrandom}"
    
    Creat_Client(code_client, agences, Nom, Prenom, telephone, adresse,email,carte_cni,date)
    flash("Client enregistré avec succès !", "success")
    return redirect(url_for('page_Client'))

@app.route('/Ventes')
@login_required
def page_Ventes():
    idlot=read_idlot(session['agences'])
    idclient=read_client(session['agences'])
    ventes_liste=liste_ventes(session['agences']) 
    table_ventes=[]  
    table_idlot=[]
    table_idclient=[]

    
    for d in idlot:
        information = {
                "id": d[0],
                "numero": d[1],
            }
        table_idlot.append(information)
     
    for d in idclient:
        information = {
                "id": d[0],
                "nom": d[1],
                "Prenom": d[2]
            }
        table_idclient.append(information)  
    
    for v in ventes_liste:
        information_ventes = {
            "id": v[0] if len(v) > 0 else "",
            "client_nom": v[1] if len(v) > 1 else "",
            "client_prenom": v[2] if len(v) > 2 else "",
            "lot_id": v[3] if len(v) > 3 else "",
            "prix_vente": v[4] if len(v) > 4 else "",
            "date_vente": v[5].strftime("%d-%m-%Y") if len(v) > 5 else "",
            "superficie": v[6] if len(v) > 6 else "",
            "prix_total": v[7] if len(v) > 7 else "",
            "nom_ilot": v[8] if len(v) > 8 else "",
            "code_client": v[9] if len(v) > 9 else ""
        }
        table_ventes.append(information_ventes)
        

    return render_template('Ventes.html', active_page='Ventes',ventes=table_ventes, lots=table_idlot, clients=table_idclient)

@app.route('/Ventes',methods=["POST"])
@login_required
def enregistrement_ventes():
    if request.method=="POST":
       vent_id=request.form['vente_id'] or None
       lot_id=request.form['lot_id']
       client_id=request.form['client_id']
       prix_vente = request.form['montant']
       date_vente = request.form['date']
       agence_id=session['agences']
       valeurrandom=random.randint(1000, 9999)
       code_vente=f"VEN-{agence_id}-{valeurrandom}"
    Creat_Vente(lot_id, client_id, prix_vente,date_vente,agence_id,code_vente,vent_id)
    return redirect(url_for("page_Ventes"))

# Administration
@app.route('/rapports')
@login_required
def intf_rapports():
    return render_template('rapport.html', active_page='rapports')

@app.route('/telechargement/<nom>')
def telecharger_rapport(nom):
    doc = get_fichier_from_db(nom)
    if not doc:
        return "Fichier non trouvé", 404

    file_bytes = base64.b64decode(doc['fichier_data'])
    return send_file(
        io.BytesIO(file_bytes),
        mimetype=doc['fichier_mimetype'],
        as_attachment=True,
        download_name=nom
    )


@app.route('/impression/<nom>')
def imprimer_rapport(nom):
    doc = get_fichier_from_db(nom)
    if not doc:
        return "Fichier non trouvé", 404

    file_bytes = base64.b64decode(doc['fichier_data'])
    return send_file(
        io.BytesIO(file_bytes),
        mimetype=doc['fichier_mimetype'],
        as_attachment=False
    )
@app.route('/suppression/<nom>', methods=['DELETE'])
def supprimer_rapport(nom):
    chemin = os.path.join('uploads', nom)
    if os.path.exists(chemin):
        os.remove(chemin)
        return jsonify({"success": True})
    return jsonify({"error": "Fichier introuvable"}), 404

@app.route('/parametres')
@login_required
def intf_Parametres():
    return render_template('parametre.html', active_page='parametres')

@app.route('/utilisateurs')
@login_required
def Page_utilisateur():
    data=read_idrole()
    liste_users=liste_utilisateur(session['agences'])
    table = []
    table_users = []
    for d in liste_users:
        if not d:
            continue
        information = {
            "nom": d[0] if len(d) > 0 else "",
            "email": d[1] if len(d) > 1 else "",
            "mpd": d[2] if len(d) > 2 else "",
            "role": d[3] if len(d) > 3 else ""
        }
        table_users.append(information)
    for d in data:
        if not d:
            continue
        information = {
            "id": d[0] if len(d) > 0 else "",
            "nom": d[1] if len(d) > 1 else ""
        }
        table.append(information)
    return render_template('utilisateurs.html',roles=table, users=table_users,  active_page='utilisateurs')

@app.route('/utilisateurs/ajouter', methods=['GET', 'POST'])
def ajouter_utilisateur():
    if request.method == 'POST':
        NomUtilisateur = request.form['nomuser']
        EmailUtilisateur = request.form['Email']
        RoleUtilisateur = int(request.form['role'])
        AgrenceUtilisateur = int(session['agences'])
        passUtilisateur = request.form['pass']
        cret_User(NomUtilisateur, EmailUtilisateur, RoleUtilisateur, AgrenceUtilisateur,passUtilisateur)
    return redirect(url_for('Page_utilisateur'))


@app.route('/logout')
def logout():
    session.clear()
    flash("Déconnexion réussie", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    port=int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0',port=port)