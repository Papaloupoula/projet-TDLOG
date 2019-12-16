import os
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash
import pandas as pd
import random
import collections
import copy
from wikidata import dictionnaire_des_pays

URL_DE_TEST = 'http://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20Sri%20Lanka.svg'
file_csv = "./liste_logins.csv"

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.no_of_chance = 4

##Génération des questions avec les réponses
longueur_questionnaire = 10
nombre_pays = len(dictionnaire_des_pays)


liste_tous_indices = [i for i in range(nombre_pays)] # liste de tous les indices de tous les pays
liste_indices_questions = [] # liste des indices des pays sur lesquels on pose des questions

for i in range(longueur_questionnaire):
    n = random.randint(0, len(liste_tous_indices)-1)
    liste_indices_questions.append(liste_tous_indices[n])
    del liste_tous_indices[n]

questions = {}
nombre_options_par_question = 4
type_questions = "Capitale"
for i in range(longueur_questionnaire):
    indice_pays = liste_indices_questions[i]
    pays = dictionnaire_des_pays[indice_pays]['Pays']
    reponse = dictionnaire_des_pays[indice_pays][type_questions]
    print("Indice pays : ", indice_pays)
    
    indices_options = [indice_pays] 
    #indices des réponses proposées à l'utilisateur, qui contiennent initialement la bonne réponse
    while len(indices_options) < nombre_options_par_question:
        n = random.randint(0, nombre_pays-1)
        if n not in indices_options:
            indices_options.append(n)
    random.shuffle(indices_options)
    options = [dictionnaire_des_pays[indices_options[j]][type_questions] for j in range(nombre_options_par_question)]
    print("Options : ", indices_options)
    
    if type_questions == "Capitale":
        questions[str(i)] = {"question": "Quelle est la capitale de " + pays, "options": options, "answer": reponse}
    if type_questions == "President":
        questions[str(i)] = {"question": "Qui est le président de " + pays, "options": options, "answer": reponse}
    



# Ici on vérifie si le fichier qui conserve les réponses existe ou pas


#### La page d'accueil #####
@app.route('/')
def home():
    return render_template('index.html')


#### s'inscrire #####

liste = [None] * (longueur_questionnaire + 2)


@app.route('/signup', methods=['POST'])
def signup():
    session['username'] = request.form['username']
    liste[0] = request.form['username']
    # df.iloc[-1]["user"] = request.form['username']
    return redirect(url_for('bienvenue'))


#### page de bienvenue une fois l'inscription faite #####

@app.route('/bienvenue')
def bienvenue():
    if not 'username' in session:
        return abort(403)
    return render_template('message.html', username=session['username'], url_test=URL_DE_TEST)


#### le questionnaire #####

@app.route('/questionnaire/', methods=['GET', 'POST'])
def questionnaire():
    print(request.method)
    print(session.get("question", "a"))

    if request.method == "POST":
        if "question" in session:
            entered_answer = request.form.get('answer', '')
            liste[int(session["question"])] = entered_answer
            print(questions.get(session["question"], False))
            if questions.get(session["question"], False):
                if entered_answer != questions[session["question"]]["answer"]:
                    mark = 0
                else:
                    mark = 4
                session["mark"] += mark
                session["question"] = str(int(session["question"]) + 1)
        else:
            print("question missing")

    if "question" not in session:
        session["question"] = "1"
        session["mark"] = 0
    elif session["question"] not in questions:  # cas où il n'y a plus de question
        df = pd.read_csv(file_csv)
        df.reset_index(drop=True, inplace=True)
        liste[longueur_questionnaire + 1] = session["mark"]
        df.loc[-1] = liste
        df.to_csv(file_csv, index=False)
        return render_template("score.html", score=session["mark"])
    return render_template("quiz.html", question=questions[session["question"]]["question"],
                           question_number=session["question"],
                           nb_questions=len(questions), options=questions[session["question"]]["options"],
                           score=session["mark"], score_total=len(questions) * 4)


@app.route('/logout')
def logout():
    # réinitialiser la session
    session.pop('username', None)
    session.clear()
    return redirect(url_for('home'))


@app.route('/metrics')
def metrics():
    df = pd.read_csv(file_csv)
    cols = copy.copy(liste_choice)
    cols.insert(0, 'user')
    ### la colonne score
    cols.insert(df.shape[1], 'score')
    df.columns = cols
    max_bonne_reponse = 0

    df.sort(['score'], ascending=[0], inplace=True)

    return render_template('metrics.html', tables=[df.head(3).to_html(index=False)],
                           titles=cols, nom_cap=capitale_mieux_trouvee,
                           nb_answers=df.shape[0])


if __name__ == '__main__':
    app.run(debug=True)
