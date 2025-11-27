from data.db_communication import PostgreSQL
import pandas as pd
import streamlit as st

DATABASE = PostgreSQL(
    hostname="ep-curly-dew-ad41zuv8-pooler.c-2.us-east-1.aws.neon.tech",
    db_name="neondb",
    username="guest",
    password="project-rally",
    port=5432,
)

# Question 1 
df_question1 = DATABASE.execute("SELECT last_name, first_name, citizenship FROM contestant JOIN crew ON contestant.id_crew = crew.id JOIN participation ON crew.id_team = participation.id_team JOIN team ON crew.id_team = team.id JOIN rally ON participation.id_rally = rally.id WHERE team.type = 'motorbike' AND rally.year = '2000'")
df_question1 = pd.DataFrame(df_question1, columns = ['Last Name', 'First Name', 'Citizenship'])
df_question1 = df_question1.sort_values(by = ["Last Name", "First Name"]).reset_index(drop = True)

st.title("Requêtes")

# Question 2 

nombre_etape_senegal = DATABASE.execute("SELECT COUNT(*) AS nb_lignes FROM stage JOIN city c1 ON stage.id_starting_city = c1.id JOIN city c2 ON stage.id_ending_city = c2.id WHERE c1.country = 'Sénégal' AND c2.country = 'Sénégal'")

# Question 3

df_question3 = DATABASE.execute("SELECT number, c1.name, c2.name FROM stage JOIN city c1 ON stage.id_starting_city = c1.id JOIN city c2 ON stage.id_ending_city = c2.id WHERE c1.country = 'Sénégal' AND c2.country = 'Sénégal'")
df_question3 = pd.DataFrame(df_question3, columns = ['Number', 'Name of the starting city', 'Name of the ending city'])

# Question 4 

df_question4 = DATABASE.execute("SELECT r.name, r.year FROM rally r WHERE (SELECT COUNT(*) FROM participation p JOIN crew c ON c.id = p.id_team JOIN contestant ct ON ct.id_crew = c.id WHERE p.id_rally = r.id) >= (SELECT COUNT(*) FROM participation p JOIN crew c ON c.id = p.id_team JOIN contestant ct ON ct.id_crew = c.id JOIN rally r2 ON p.id_rally = r2.id WHERE r2.name = 'Paris-Dakar' AND r2.year = '2002');")
df_question4 = pd.DataFrame(df_question4, columns = ['Name of the rally', 'Year of the rally'])

# Question 5

nombre_vehicule_toyota = DATABASE.execute("SELECT COUNT(*) AS nb_vehicles FROM vehicle v JOIN crew c ON v.id_crew = c.id JOIN participation p ON c.id_team = p.id_team JOIN rally r ON p.id_rally = r.id WHERE r.name = 'Paris Dakar' AND r.year >= 2004 AND v.constructor = 'Toyota';")

# Question 6

df_question6 = DATABASE.execute("SELECT id_crew, time, disqualification, number FROM result re JOIN stage s ON re.id_stage = s.id JOIN rally ra ON s.id_rally = ra.id WHERE ra.name = 'Paris Dakar' AND ra.year = 2002;")
df_question6 = pd.DataFrame(df_question6, columns=["Crew number", 'Chrono', 'Disqualification', "Stage number"])
df_question6 = df_question6[df_question6["Disqualification"] != True]
df_question6['Chrono'] = pd.to_timedelta(df_question6['Chrono'], unit='s')

df_question6['Rank'] = df_question6.groupby("Stage number")['Chrono'].rank(method='first').astype(int)
df_question6 = df_question6.pivot(index="Stage number", columns='Rank', values='Chrono')

df_question6 = df_question6.applymap(lambda x: f"{int(x.total_seconds()//3600)}h{int((x.total_seconds()%3600)//60)}" if pd.notnull(x) else "")

# Question 7

df_question7 = DATABASE.execute("SELECT last_name, first_name, citizenship, participation_number FROM contestant")
df_question7 = pd.DataFrame(df_question7, columns = ["Last Name", "First Name", "Citizenship", "Number of participation"])

# Streamlit Question 1

st.divider()
st.header("1) Lister par ordre alphabétique les participants du rallye Paris Dakar de l'année 2000 ayant appartenu à la catégorie moto.")
st.divider()
st.write("")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Requête n°1")
        st.code("""SELECT last_name, first_name, citizenship FROM contestant
                    JOIN crew ON contestant.id_crew = crew.id
                    JOIN participation ON crew.id_team = participation.id_team
                    JOIN team ON crew.id_team = team.id
                    JOIN rally ON participation.id_rally = rally.id
                    WHERE team.type = 'motorbike' AND rally.year = '2000';""")

with col2:
    st.dataframe(df_question1, use_container_width=True)

st.divider()

# Streamlit Question 2

st.header("2) Lister le nombre d'étapes se déroulant au Sénégal.")
st.divider()
st.write("")

col1, col2 = st.columns(2)

with col1:
    st.write("")
    st.subheader(f"Le nombre d'étapes dont la ville de départ et la ville d'arrivée se situe au Sénégal est de {nombre_etape_senegal[0][0]}.")

with col2:
    with st.container(border=True):
        st.subheader("Requête 2")
        st.code("""SELECT COUNT(*) AS nb_lignes
                    FROM stage
                    JOIN city c1 ON stage.id_starting_city = c1.id
                    JOIN city c2 ON stage.id_ending_city = c2.id
                    WHERE c1.country = 'Sénégal' AND c2.country = 'Sénégal';
                    """)

st.divider()

# Streamlit Question 3

st.header("3) Lister la liste d’étapes (numéro, ville départ et ville d'arrivée) se déroulant au Sénégal.")
st.divider()
st.write("")

col1, col2 = st.columns(2)

with col1:
    with st.container(border = True):
        st.subheader("Requête 3")
        st.code("""SELECT (number, c1.name, c2.name) FROM stage
                    JOIN city c1 ON stage.id_starting_city = c1.id
                    JOIN city c2 ON stage.id_ending_city = c2.id
                    WHERE c1.country = 'Sénégal' AND c2.country = 'Sénégal';""")

with col2:
    st.dataframe(df_question3, use_container_width=True)

st.divider()

# Streamlit Question 4

st.header(" Faux : 4) Trouver la liste des rallyes ayant un nombre de participants égal ou supérieur au nombre de participants du rallye Paris-Dakar de l’année 2002.")
st.divider()
st.write("")

col1, col2 = st.columns(2)

with col1:
    st.dataframe(df_question4, use_container_width=True)
with col2:
    with st.container(border=True):
        st.subheader("Requête 4")
        st.code("""SELECT r.name, r.year
                    FROM rally r
                    WHERE (
                        SELECT COUNT(*)
                        FROM participation p
                        JOIN crew c ON c.id = p.id_team
                        JOIN contestant ct ON ct.id_crew = c.id
                        WHERE p.id_rally = r.id
                    ) >= (
                        SELECT COUNT(*)
                        FROM participation p
                        JOIN crew c ON c.id = p.id_team
                        JOIN contestant ct ON ct.id_crew = c.id
                        JOIN rally r2 ON p.id_rally = r2.id
                        WHERE r2.name = 'Paris Dakar' AND r2.year = '2002'
                    );""")

st.divider()

# Streamlit Question 5

st.header("5) Lister le nombre de véhicules appartenant à la marque Toyota ayant participé au rallye Paris-Dakar pour les dix dernières années (depuis 2004).")
st.divider()
st.write("")

col1, col2 = st.columns(2)

with col1:
    with st.container(border = True):
        st.subheader("Requête 5")
        st.code("""SELECT COUNT(*) AS nb_vehicles
                    FROM vehicle v
                    JOIN crew c ON v.id_crew = c.id
                    JOIN participation p ON c.id_team = p.id_team
                    JOIN rally r ON p.id_rally = r.id
                    WHERE r.name = 'Paris Dakar'
                        AND r.year >= 2004
                        AND v.constructor = 'Toyota';""")

with col2:
    st.write("")
    st.subheader(f"Le nombre de véhicule appartenant à la marque Toyoa ayant participé au rally Paris-Dakar pour les 10 dernières années (depuis 2004) est de {nombre_vehicule_toyota[0][0]}.")

st.divider()


# Streamlit Question 6

st.header("6) Lister le classement des équipages par étape pour le Paris-Dakar de l’an 2002.")
st.divider()
st.write("")

col1, col2 = st.columns(2)

with col1:
    st.dataframe(df_question6, use_container_width=True)
    
with col2:
    with st.container(border=True):
        st.subheader("Requête 6")
        st.code("""SELECT id_crew, time, disqualification, number FROM result re
                    JOIN stage s ON re.id_stage = s.id
                    JOIN rally ra ON s.id_rally = ra.id
                    WHERE ra.name = 'Paris Dakar' AND ra.year = 2002;""")

st.divider()

# Streamlit Question 7

st.header("7) Donner le nombre de participation au rallye Paris-Dakar par concurrent.")
st.divider()
st.write("")

col1, col2 = st.columns(2)

with col1:
    with st.container(border = True):
        st.subheader("Requête 7")
        st.code("""SELECT last_name, first_name, citizenship, participation_number FROM contestant;""")

with col2:
    st.dataframe(df_question7, use_container_width=True)

st.divider()