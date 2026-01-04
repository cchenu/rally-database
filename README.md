# rally-database
> Projet de Système de bases de données à Centrale Lyon : création d'une database sur des rallyes.

## Table des matières
* [Informations générales](#informations-générales)
* [Technologies utilisées](#technologies-utilisées)
* [Fonctionnalités](#fonctionnalités)
* [Utilisation](#utilisation)
* [État du projet](#état-du-projet)
* [Contact](#contact)

## Informations générales
Ce projet contient le développement d'une base de données relative aux rallyes automobiles. Elle est hébergée sur le cloud [Neon](https://neon.com/). Le projet contient aussi une application web Streamlit permettant d'interagir avec la base de données et de voir des informations issues de la base de données concernant les courses, les étapes et les équipes. Cette base de données a été créée à des fins d'exercice, les données sont majoritairement fausses et générées aléatoirement.

## Technologies utilisées
- **Python** - version 3.13.5
  - Bibliothèques Python : psycopg, faker, pandas, geopy, streamlit, dataframe-with-buttons, streamlit_searchbox, sqlparse, python-dotenv, et plus (voir `requirements.txt` pour la liste complète).
- **PostgreSQL** - version 17.7
  - Utilisé via la plateforme cloud [Neon](https://neon.com/).
- **DB-Main** - version 11.0.2
  - Outil de modélisation de base de données utilisé pour concevoir et créer la base de données.

## Fonctionnalités
### Présentation des fichiers
- `.streamlit/config.toml` : Configuration de l'apparence de l'application Streamlit.
- `app/` : Dossier contenant les scripts de l'application Streamlit.
  - `__init__.py` : Fichier d'initialisation de package Python.
  - `exercise.py` : Page Streamlit contenant les réponses aux exercices.
  - `home.py` : Page d'accueil de l'application Streamlit.
  - `rally.py` : Page Streamlit donnant les informations sur un rally.
  - `stage.py` : Page Streamlit donnant les informations sur une étape.
  - `team.py` : Page Streamlit donnant les informations sur une équipe.
  - `utils.py` : Script contenant des fonctions utilitaires pour l'application Streamlit.
- `data/` : Dossier contenant les fichiers et scripts pour la création, le remplissage et la lecture de la base de données.
  - `__init__.py` : Fichier d'initialisation de package Python.
  - `db_communication.py` : Conteneur de la classe PostgreSQL gérant la communication avec la base de données.
  - `dump.sql` : Fichier dump SQL de la base de données, pour information, non nécessaire au fonctionnement de l'application.
  - `fill_db.py` : Script pour remplir la base de données majoritairement avec des données générées aléatoirement.
  - `stages.csv` : Fichier CSV contenant les étapes des rallyes, avec l'année, le numéro, la ville d'arrivée et celle de départ. Ces données sont réelles.
  - `database_creation.ddl` : Fichier DDL contenant les commandes SQL pour créer les tables de la base de données, issu de DB-Main.
- `.env` : Fichier contenant les variables d'environnement pour la connexion à la base de données.
- `.gitignore` : Fichier listant les fichiers et dossiers à ignorer par Git.
- `Makefile` : Fichier Makefile pour automatiser certaines tâches. Non nécessaire, nécessite l'installation de Make.
- `pyproject.toml` : Fichier de configuration du projet Python.
- `rapport.pdf` : Rapport du projet détaillant la conception de la base de données.
- `README.md` : Ce fichier, contenant la documentation du projet.
- `requirements.txt` : Fichier listant les dépendances Python nécessaires au projet.
- `streamlit_app.py` : Fichier d'entrée de l'application Streamlit.

### Application Streamlit
L'application Streamlit contient cinq types de pages différents. La page d'accueil sert de point d'entrée. Elle contient une barre de recherche permettant de trouver les rallyes, les étapes ou les équipes. Elle permet aussi l'accès à la page des exercices et de réaliser des requêtes SQL personnalisées. La page des exercices contient les réponses aux questions posées dans le sujet. Les pages rallye, étape et équipe permettent d'afficher les informations relatives à un rallye, une étape ou une équipe en particulier.

<div align="center">

|  |  |
|:--:|:--:|
| <img src="https://i.postimg.cc/rwq1FHNC/page-home.png" height="250" width="250"> | <img src="https://i.postimg.cc/sg3YDL44/page-exercise.png" height="250" width="250"> |
| <img src="https://i.postimg.cc/4xX6N0Q1/page-rally.png" height="250" width="250"> | <img src="https://i.postimg.cc/wj9XTrQJ/page-team.png" height="250" width="250"> |

</div>

## Utilisation
### Installation
**Vérifiez que vous avez Python 3.x installé.**

**Clonez le dépôt :**
   ```bash
   git clone https://github.com/cchenu/rally-database
   ```

**Placez-vous dans le répertoire du projet :**
   ```bash
   cd rally-database
   ```

**(Facultatif) Créez un environnement virtuel :**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Sur Windows
   source .venv/bin/activate  # Sur Linux ou macOS
   ```

**Installez les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

Il n'est pas nécessaire d'initialiser une copie locale de la base de données, l'application se connecte directement à la base de données hébergée sur Neon grâce aux identifiants enregistrés dans le fichier `.env`.

### Lancer l'application
**Vérifiez que vous êtes dans la racine du projet :**
   ```bash
   cd rally-database
   ```

**(Le cas échéant) Activez votre environnement virtuel :**
   ```bash
   .venv\Scripts\activate  # Sur Windows
   source .venv/bin/activate  # Sur Linux ou macOS
   ```

**Lancez l'application Streamlit :**
   ```bash
   streamlit run
   ```

Lors de la première utilisation, il est possible que Streamlit vous demande une adresse e-mail, il n'est pas nécessaire d'en fournir une, vous pouvez appuyer sur entrée pour passer cette étape.

Une fenêtre de navigateur devrait s'ouvrir automatiquement à l'adresse [http://localhost:8501](http://localhost:8501). Si ce n'est pas le cas, ouvrez votre navigateur et rendez-vous à cette adresse.

## État du projet
Le projet est : _terminé_ - version 0.0.1.


## Contact
Projet réalisé par Clément CHENU et Hugo EBERSCHWEILER sous la supervision de Mohsen ARDABILIAN à Centrale Lyon dans le cadre du MOD 11.1 Systèmes de bases de données.
