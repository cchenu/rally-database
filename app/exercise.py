"""Streamlit page with question answers."""

import pandas as pd
import sqlparse
import streamlit as st

from app.utils import DATABASE


def question_1() -> None:
    """Create the first section part."""
    st.header(
        "1) Lister par ordre alphabétique les participants du rallye Paris "
        "Dakar de l'année 2000 ayant appartenu à la catégorie moto."
    )
    query = (
        "SELECT last_name, first_name FROM contestant "
        "JOIN crew ON contestant.id_crew = crew.id "
        "JOIN participation ON crew.id_team = participation.id_team "
        "JOIN team ON crew.id_team = team.id "
        "JOIN rally ON participation.id_rally = rally.id "
        "WHERE team.type = 'motorbike' AND rally.year = 2000 "
        "AND rally.name = 'Paris Dakar' "
        "ORDER BY last_name, first_name;"
    )

    list_question1 = DATABASE.execute(query)

    df_question1 = pd.DataFrame(
        list_question1, columns=["Last Name", "First Name"]
    )

    st.divider()
    st.write("")

    col1, col2 = st.columns(2)

    with col1, st.container(border=True):
        st.subheader("Requête n°1")
        st.code(sqlparse.format(query, reindent=True, keyword_case="upper"))

    with col2:
        st.dataframe(df_question1, width="stretch", hide_index=True)


def question_2() -> None:
    """Create the second section part."""
    st.header("2) Lister le nombre d'étapes se déroulant au Sénégal.")
    query = (
        "SELECT COUNT(*) AS nb_lignes FROM stage "
        "JOIN city c1 ON stage.id_starting_city = c1.id "
        "JOIN city c2 ON stage.id_ending_city = c2.id "
        "WHERE c1.country = 'Sénégal' OR c2.country = 'Sénégal';"
    )
    nombre_etape_senegal = DATABASE.execute(query)

    st.divider()
    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.write("")
        st.subheader(
            "Le nombre d'étapes dont la ville de départ ou la ville "
            "d'arrivée se "
            f"situe au Sénégal est de {nombre_etape_senegal[0][0]}."
        )

    with col2, st.container(border=True):
        st.subheader("Requête 2")
        st.code(sqlparse.format(query, reindent=True, keyword_case="upper"))
    st.divider()


def question_3() -> None:
    """Create the third section part."""
    st.header(
        "3) Lister la liste d'étapes (numéro, ville départ et ville "
        "d'arrivée) se déroulant au Sénégal."
    )
    query = (
        "SELECT stage.number, c1.name, c2.name FROM stage "
        "JOIN city c1 ON stage.id_starting_city = c1.id "
        "JOIN city c2 ON stage.id_ending_city = c2.id "
        "WHERE c1.country = 'Sénégal' AND c2.country = 'Sénégal';"
    )
    list_question3 = DATABASE.execute(query)
    df_question3 = pd.DataFrame(
        list_question3,
        columns=[
            "Number",
            "Name of the starting city",
            "Name of the ending city",
        ],
    )

    st.divider()
    st.write("")

    col1, col2 = st.columns(2)

    with col1, st.container(border=True):
        st.subheader("Requête 3")
        st.code(sqlparse.format(query, reindent=True, keyword_case="upper"))

    with col2:
        st.dataframe(df_question3, width="stretch", hide_index=True)

    st.divider()


def question_4() -> None:
    """Create the fourth section part."""
    st.header(
        "4) Trouver la liste des rallyes ayant un nombre de "
        "participants égal ou supérieur au nombre de participants du rallye "
        "Paris-Dakar de l'année 1999."
    )
    query = (
        "SELECT r.name, r.year FROM rally r "
        "WHERE (SELECT COUNT(*) FROM participation p "
        "WHERE p.id_rally = r.id) "
        ">= (SELECT COUNT(*) FROM participation p "
        "JOIN rally r2 ON p.id_rally = r2.id "
        "WHERE r2.name = 'Paris Dakar' AND r2.year = 1999);"
    )
    list_question4 = DATABASE.execute(query)
    df_question4 = pd.DataFrame(
        list_question4, columns=["Name of the rally", "Year of the rally"]
    )

    st.divider()
    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(df_question4, width="stretch", hide_index=True)

    with col2, st.container(border=True):
        st.subheader("Requête 4")
        st.code(sqlparse.format(query, reindent=True, keyword_case="upper"))

    st.divider()


def question_5() -> None:
    """Create the fifth section part."""
    st.header(
        "5) Lister le nombre de véhicules appartenant à la marque Toyota "
        "ayant participé au rallye Paris-Dakar pour les dix dernières années "
        "(depuis 2004)."
    )
    query = (
        "SELECT COUNT(*) AS nb_vehicles FROM vehicle v "
        "JOIN crew c ON v.id_crew = c.id "
        "JOIN participation p ON c.id_team = p.id_team "
        "JOIN rally r ON p.id_rally = r.id "
        "WHERE r.name = 'Paris Dakar' "
        "AND r.year >= 2004 "
        "AND v.constructor = 'Toyota';"
    )
    nombre_vehicule_toyota = DATABASE.execute(query)

    st.divider()
    st.write("")

    col1, col2 = st.columns(2)

    with col1, st.container(border=True):
        st.subheader("Requête 5")
        st.code(sqlparse.format(query, reindent=True, keyword_case="upper"))

    with col2:
        st.write("")
        st.subheader(
            "Le nombre de véhicule appartenant à la marque Toyoa ayant "
            "participé au rally Paris-Dakar pour les 10 dernières années "
            f"(depuis 2004) est de {nombre_vehicule_toyota[0][0]}."
        )

    st.divider()


def question_6() -> None:
    """Create the sixth section part."""
    st.header(
        "6) Lister le classement des équipages par étape pour le Paris-Dakar "
        "de l'an 2002."
    )
    query = (
        "SELECT id_crew, time, disqualification, number FROM result re "
        "JOIN stage s ON re.id_stage = s.id "
        "JOIN rally ra ON s.id_rally = ra.id "
        "WHERE ra.name = 'Paris Dakar' AND ra.year = 2002;"
    )
    list_question6 = DATABASE.execute(query)
    df_question6 = pd.DataFrame(
        list_question6,
        columns=["Crew number", "Chrono", "Disqualification", "Stage number"],
    )
    df_question6 = df_question6[~df_question6["Disqualification"]]
    df_question6["Chrono"] = pd.to_timedelta(df_question6["Chrono"], unit="s")

    df_question6["Rank"] = (
        df_question6.groupby("Stage number")["Chrono"]
        .rank(method="first")
        .astype(int)
    )
    df_question6 = df_question6.pivot_table(
        index="Stage number", columns="Rank", values="Chrono"
    )

    df_question6 = df_question6.map(
        lambda x: (
            f"{int(x.total_seconds() // 3600)}h"
            f"{int((x.total_seconds() % 3600) // 60)}"
            if pd.notna(x)
            else ""
        )
    )

    st.divider()
    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(df_question6, width="stretch")

    with col2, st.container(border=True):
        st.subheader("Requête 6")
        st.code(sqlparse.format(query, reindent=True, keyword_case="upper"))

    st.divider()


def question_7() -> None:
    """Create the seventh section part."""
    st.header(
        "7) Donner le nombre de participation au rallye Paris-Dakar par "
        "concurrent."
    )
    query = (
        "SELECT last_name, first_name, citizenship, participation_number "
        "FROM contestant;"
    )
    list_question7 = DATABASE.execute(query)
    df_question7 = pd.DataFrame(
        list_question7,
        columns=[
            "Last Name",
            "First Name",
            "Citizenship",
            "Number of participation",
        ],
    )

    st.divider()
    st.write("")

    col1, col2 = st.columns(2)

    with col1, st.container(border=True):
        st.subheader("Requête 7")
        st.code(sqlparse.format(query, reindent=True, keyword_case="upper"))

    with col2:
        st.dataframe(df_question7, width="stretch", hide_index=True)

    st.divider()


def create_page() -> None:
    """Create the exercise page with all questions."""
    st.title("Exercices")
    st.divider()
    question_1()
    question_2()
    question_3()
    question_4()
    question_5()
    question_6()
    question_7()


if __name__ == "__main__":
    create_page()
