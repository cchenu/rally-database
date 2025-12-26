"""Streamlit page to have information about a given stage."""

import streamlit as st
import pandas as pd
import numpy as np
from dataframe_with_button import static_dataframe

from data.db_communication import PostgreSQL
from app.utils import convert_s_to_h

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


def get_result_stage(id_stage: int):
    result = DATABASE.read("result", condition_data={"id_stage": id_stage})
    df_result = pd.DataFrame(result)

    df_stage_result = pd.DataFrame(columns=["Classement", "Équipe", "Temps"])

    stage_result = df_result[["time", "id_crew"]].sort_values(
        by=["time"], ascending=True, key=lambda x: x.replace(0, np.inf)
    )

    df_stage_result["Temps"] = [
        convert_s_to_h(line) if line else "Disqualifié"
        for line in stage_result["time"]
    ]

    df_stage_result["Équipe"] = stage_result["id_crew"].values

    df_stage_result["Classement"] = [
        str(i + 1) if val != "Disqualifié" else "N/A"
        for i, val in enumerate(stage_result["time"])
    ]
    df_stage_result = df_stage_result[["Classement", "Équipe", "Temps"]]
    
    st_table = static_dataframe(
        df_stage_result, clickable_column="Équipe"
    )


def create_page():
    # id_contestant: int = st.session_state["id_contestant"]
    id_rally: int = st.session_state["id_rally"]
    id_stage: int = st.session_state["id_stage"]

    stage = DATABASE.read("stage", condition_data={"id": id_stage})
    df_stage = pd.DataFrame(stage)
    id_starting_city = df_stage["id_starting_city"][0]
    id_ending_city = df_stage["id_ending_city"][0]
    distance_stage = df_stage["kilometers"][0]
    rally = DATABASE.read("rally", condition_data={"id": id_rally})
    df_rally = pd.DataFrame(rally)
    city_depart = DATABASE.read(
        "city", "name", condition_data={"id": id_starting_city}
    )
    df_city_depart = pd.DataFrame(city_depart)
    city_arrivee = DATABASE.read(
        "city", "name", condition_data={"id": id_ending_city}
    )
    df_city_arrivee = pd.DataFrame(city_arrivee)

    rally_name = df_rally["name"][0]
    rally_year = df_rally["year"][0]
    number = df_stage["number"][0]
    city_depart = df_city_depart["name"][0]
    city_arrivee = df_city_arrivee["name"][0]
    st.title(exposant_etape(number, rally_name, rally_year)[0])

    st.text(
        f"{exposant_etape(number, rally_name, rally_year)[1]} {exposant_etape(number, rally_name, rally_year)[0]} se déroule de {city_depart} à {city_arrivee} sur une distance de {distance_stage} km."
    )

    get_result_stage(id_stage)


if __name__ == "__main__":
    create_page()
