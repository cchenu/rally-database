"""Streamlit page to have information about a given stage."""

import streamlit as st
import pandas as pd
from data.db_communication import PostgreSQL

DATABASE = PostgreSQL(
    hostname="ep-curly-dew-ad41zuv8-pooler.c-2.us-east-1.aws.neon.tech",
    db_name="neondb",
    username="guest",
    password="project-rally",
    port=5432,
)


def exposant_etape(number: int, rally_name: int, rally_year: int):
    determinant = "La"
    if number == 0:
        determinant = "Le"
        return (f"Prologue de {rally_name} {rally_year}", determinant)
    elif number == 1:
        return (f"{number}ʳᵉ étape du {rally_name} {rally_year}", determinant)
    else:
        return (f"{number}ᵉ étape du {rally_name} {rally_year}", determinant)


def create_page():
    # id_contestant: int = st.session_state["id_contestant"]
    id_rally: int = st.session_state["id_rally"]
    id_stage: int = st.session_state["id_stage"]

    stage = DATABASE.read("stage", condition_data={"id": id_stage})
    df_stage = pd.DataFrame(stage)
    id_starting_city = df_stage["id_starting_city"][0]
    id_ending_city = df_stage["id_ending_city"][0]
    rally = DATABASE.read("rally", condition_data={"id": id_rally})
    df_rally = pd.DataFrame(rally)
    city_depart = DATABASE.read("city", "name", condition_data = {"id": id_starting_city})
    df_city_depart = pd.DataFrame(city_depart)
    city_arrivee = DATABASE.read("city", "name", condition_data = {"id": id_ending_city})
    df_city_arrivee = pd.DataFrame(city_arrivee)

    rally_name = df_rally["name"][0]
    rally_year = df_rally["year"][0]
    number = df_stage["number"][0]
    city_depart = df_city_depart["name"][0]
    city_arrivee = df_city_arrivee["name"][0]
    st.title(exposant_etape(number, rally_name, rally_year)[0])

    st.text(f"{exposant_etape(number, rally_name, rally_year)[1]} {exposant_etape(number, rally_name, rally_year)[0]} se déroule de {city_depart} à {city_arrivee}")


if __name__ == "__main__":
    create_page()
