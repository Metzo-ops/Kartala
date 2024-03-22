from flask import Flask, render_template
import mysql.connector
import os, json
from builtins import zip


def zip_lists(*args):
    return list(zip(*args))

app = Flask(__name__)
app.jinja_env.filters['zip_lists'] = zip_lists

with open('config.json', 'r') as f:
    config_data = json.load(f)

User = config_data['Database']['user']
Password=config_data['Database']['password']
Host = config_data['Database']['host']
db = config_data['Database']['database']
file_db = config_data['Database']['file_db']



#############################################################
#####---CONNEXION A LA BASE DE DONNEE AVEC mysql.connector--#
#############################################################

os.system(f'mysql -u {User} -p{Password} -e "{file_db} ;"')

def connect_to_DB():
    conn = mysql.connector.connect(
        host=Host,
        user=User,
        password=Password,
        database=db
    )
    if conn.is_connected:
        print("connexion OK")
    conn.commit()    
    return conn

#############################################################
#####---INSERTION DE VALEURS ALEATOIRES DANS LA BASE---#####
#############################################################

poles = ["Education et Développement du capital humain","Eau, Assainissement et Santé publique","Système d’Information, Ingénierie des données et Intelligence Artificielle","Agriculture, Immigration et Entreprenariat des jeunes","Gestion et Evaluation des Politiques publiques","Environnement, Changement climatique et Gestion des Ressources Naturelles","Financement du Développement","Suivi & Evaluation d’Impact"]
projets = ["p1","p2","p3","p4","p5","p6","p7","p8"]
nom_COM = ["Abdou","Modou","Mamadou","Abdoulaye","Nafi","Ami","Astou","Abou"]
dp = range(1,9)
dd = ["2022-12-28","2022-08-28","2022-07-28","2022-06-28","2022-05-28","2022-03-28","2023-02-28","2024-02-28"]
df = ["2024-11-28","2024-10-28","2024-05-28","2024-04-28","2024-01-28","2024-02-28","2024-03-28","2025-02-28"]
id_cor = range(1,8)
bp = range(1000,9000,1000)
id_pole = range(1,9)
Ne = ["Sonko","Diomaye","Diakhar","Faye","Ba","Diallo","Sow","Ly"]
age = range(16,30,2)
sexe = ["M","M","M","M","F","F","F","M"]
SM = ["Mar","Mar","Mar","Celib","Mar","Mar","Celib","Celib"]
Nedu = [f"Bac+{i}" for i in range(1,9)]
libAct = [f"Act{i}" for i in range(1,9)]

def pull_values_in_poles(cur):
    for i in poles:
        cur.execute("INSERT INTO Poles(NomPole) VALUES (%s)",(i,))

def pull_values_in_employes(cur):
    req0 = "INSERT INTO Employes(NomEmploye, PrenomEmploye, DateEmbauche, DateFinContrat, Age, Sexe, StatutMatrimonial, NiveauEducation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    val = list(zip(Ne, nom_COM, dd,df, age,sexe, SM,Nedu))
    cur.executemany(req0, val)
        
def pull_values_in_proj(cur):
    req ="INSERT INTO Projets(NomProjet, NomCommanditaire, DureeProjet, DateDebutProjet, DateFinPrevueProjet,BudgetProjet, IdCoordinateur,IdPole) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    values = list(zip(projets, nom_COM, dp,dd,df, bp,id_cor, id_pole))
    cur.executemany(req, values)

def pull_values_in_activ(cur):
    req1 ="INSERT INTO Activites(LibelleActivite, DureeActivite, DateDebutActivite, DateFinPrevueActivite, BudgetActivite,IdProjet) VALUES (%s,%s,%s,%s,%s,%s)"
    val_1 = list(zip(libAct, dp,dd,df, bp, range(1,8)))
    cur.executemany(req1, val_1)

#############################################################
#####---APPEL DES FONCTIONS---#####
#############################################################

db_conn = connect_to_DB()
cursor = db_conn.cursor()
pull_values_in_poles(cursor)
pull_values_in_employes(cursor)
pull_values_in_proj(cursor)
pull_values_in_activ(cursor)

#############################################################
#####---DEFINITION DES REQUETES SQL---#####
#############################################################

# Le nombre de projets/programmes en cours désagrégé par pôle ou démembrement.
def one_1():
    cursor.execute("SELECT p.NomPole, COUNT(*) AS NombreProjetsEnCours FROM Projets pr JOIN Poles p ON pr.IdPole = p.IdPole WHERE pr.DateFinPrevueProjet > CURRENT_DATE() GROUP BY p.NomPole;")
    resultats = cursor.fetchall()
    if resultats:
        list_poles_1, list_nbre_de_proj_1 = zip(*[(i[0], i[1]) for i in resultats]) 
        return list_poles_1, list_nbre_de_proj_1
    else:
        return [], []
    
# Le nombre de projets/programmes déjà finalisés désagrégé par pôle ou démembrement.
def two_2():
    cursor.execute("SELECT p.NomPole, COUNT(*) AS NombreProjetsFinalises FROM Projets pr JOIN Poles p ON pr.IdPole = p.IdPole WHERE pr.DateFinPrevueProjet < CURRENT_DATE() GROUP BY p.NomPole;")
    resultats = cursor.fetchall()
    if resultats:
        list_poles_2, list_nbre_de_proj_2 = zip(*[(i[0], i[1]) for i in resultats])
        return list_poles_2, list_nbre_de_proj_2
    else:
        return [], []
    
# Le pourcentage d'activité/tâches exécutées avant l'échéance désagrégé par projet/programme.
def three_3():
    cursor.execute("SELECT pr.NomProjet, ROUND(100.0 * SUM(CASE WHEN ea.DateFinRealisation <= a.DateFinPrevueActivite THEN 1 ELSE 0 END) / COUNT(*), 2) AS PourcentageAvantEcheance FROM Projets pr JOIN Activites a ON pr.IdProjet = a.IdProjet LEFT JOIN EmployesAffectes ea ON a.IdActivite = ea.IdActivite GROUP BY pr.NomProjet;")
    resultats = cursor.fetchall()
    if resultats:
        list_nom_proj_3, list_percent3 = zip(*[(i[0], i[1]) for i in resultats])
        return list_nom_proj_3, list_percent3
    else:
        return [], []
    
# Le pourcentage d'activité/tâches exécutées après l'échéance désagrégé par projet/programme
def four_4():
    cursor.execute("SELECT pr.NomProjet, ROUND(100.0 * SUM(CASE WHEN ea.DateFinRealisation > a.DateFinPrevueActivite THEN 1 ELSE 0 END) / COUNT(*), 2) AS PourcentageApresEcheance FROM Projets pr JOIN Activites a ON pr.IdProjet = a.IdProjet LEFT JOIN EmployesAffectes ea ON a.IdActivite = ea.IdActivite GROUP BY pr.NomProjet;")
    resultats = cursor.fetchall()
    if resultats:
        list_nom_proj_4, list_percent4 = zip(*[(i[0], i[1]) for i in resultats])
        return list_nom_proj_4, list_percent4
    else:
        return [], []
    
# Le pourcentage des membres d'un pôle impliqué dans un projet/programme qui ont réalisé les activités liées au projet/programme avant l'échéance parmi tous les membres du pôle impliqués.
def five_5():
    cursor.execute("SELECT p.NomPole, pr.NomProjet, ROUND(100.0 * SUM(CASE WHEN ea.DateFinRealisation <= a.DateFinPrevueActivite THEN 1 ELSE 0 END) / COUNT(DISTINCT e.IdEmploye), 2) AS PourcentageAvantEcheance FROM Poles p JOIN Projets pr ON p.IdPole = pr.IdPole JOIN Activites a ON pr.IdProjet = a.IdProjet JOIN EmployesAffectes ea ON a.IdActivite = ea.IdActivite JOIN Employes e ON ea.IdEmploye = e.IdEmploye GROUP BY p.NomPole, pr.NomProjet;")
    resultats = cursor.fetchall()
    if resultats:
        list_pole_5, list_proj_5, list_percent_5 = zip(*[(i[0], i[1], i[2]) for i in resultats])
        return list_pole_5, list_proj_5, list_percent_5
    else:
        return [], [], []

# Le pourcentage de membres d'un pôle impliqué dans un projet/programme qui ont réalisé les activités relatives au projet/programme après l'échéance parmi tous les membres du pôle impliqués.
def six_6():
    cursor.execute("SELECT p.NomPole, pr.NomProjet, ROUND(100.0 * SUM(CASE WHEN ea.DateFinRealisation > a.DateFinPrevueActivite THEN 1 ELSE 0 END) / COUNT(DISTINCT e.IdEmploye), 2) AS PourcentageApresEcheance FROM Poles p JOIN Projets pr ON p.IdPole = pr.IdPole JOIN Activites a ON pr.IdProjet = a.IdProjet JOIN EmployesAffectes ea ON a.IdActivite = ea.IdActivite JOIN Employes e ON ea.IdEmploye = e.IdEmploye GROUP BY p.NomPole, pr.NomProjet;")
    resultats = cursor.fetchall()
    if resultats:
        list_pole_6, list_proj_6, list_percent_6 = zip(*[(i[0], i[1], i[2]) for i in resultats])
        return list_pole_6, list_proj_6, list_percent_6
    else:
        return [], [], []
    
# Pourcentage des activités/tâches à la charge d'un employé exécutée avant l'échéance.
def seven_7():
    cursor.execute("SELECT e.NomEmploye, e.PrenomEmploye, ROUND(100.0 * SUM(CASE WHEN ea.DateFinRealisation <= a.DateFinPrevueActivite THEN 1 ELSE 0 END) / COUNT(*), 2) AS PourcentageAvantEcheance FROM Employes e JOIN EmployesAffectes ea ON e.IdEmploye = ea.IdEmploye JOIN Activites a ON ea.IdActivite = a.IdActivite GROUP BY e.IdEmploye;")
    resultats = cursor.fetchall()
    if resultats:
        list_nom_Emp_7, list_pren_Emp_7, list_percent_7 = zip(*[(i[0], i[1], i[2]) for i in resultats])
        return list_nom_Emp_7, list_pren_Emp_7,list_percent_7
    else:
        return [], [], []
    
# Pourcentage des activités/tâches à la charge d'un employé exécutée après l'échéance.
def eight_8():
    cursor.execute("SELECT e.NomEmploye, e.PrenomEmploye, ROUND(100.0 * SUM(CASE WHEN ea.DateFinRealisation > a.DateFinPrevueActivite THEN 1 ELSE 0 END) / COUNT(*), 2) AS PourcentageApresEcheance FROM Employes e JOIN EmployesAffectes ea ON e.IdEmploye = ea.IdEmploye JOIN Activites a ON ea.IdActivite = a.IdActivite GROUP BY e.IdEmploye;")
    resultats = cursor.fetchall()
    if resultats:
        list_nom_Emp_8, list_pren_Emp_8, list_percent_8 = zip(*[(i[0], i[1], i[2]) for i in resultats])
        return list_nom_Emp_8, list_pren_Emp_8,list_percent_8  
    else:
        return [], [], []
    
#############################################################
#####---DEFINITION DES URLs---#####
#############################################################

@app.route("/")
def deb():
    return render_template("base.html")
@app.route("/1")
def first():
    return render_template("one.html", np = one_1()[0], npec = one_1()[1])
@app.route("/2")
def second():
    return render_template("two.html", np = two_2()[0], npf = two_2()[1])
@app.route("/3")
def third():
    return render_template("three.html", np = three_3()[0], perc3 = three_3()[1])
@app.route("/4")
def fourth():
    return render_template("four.html", np = four_4()[0], perc4 = four_4()[1])
@app.route("/5")
def fifth():
    return render_template("five.html", np = five_5()[0], npr = five_5()[1], perc5 = five_5()[2])
@app.route("/6")
def sixth():
    return render_template("six.html",np = six_6()[0], npr = six_6()[1], perc6 = six_6()[2])
@app.route("/7")
def seventh():
    return render_template("seven.html", nEm = seven_7()[0], prenEm = seven_7()[1], perc7 = seven_7()[2])
@app.route("/8")
def eighth():
    return render_template("eight.html", nEm = eight_8()[0], prenEm = eight_8()[1], perc8 = eight_8()[2])

db_conn.commit()   
# db_conn.close()

if __name__ == "__main__":
    app.run(debug=True,port=5001)