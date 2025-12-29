"""Streamlit page to have information about a given stage."""

import streamlit as st
import pandas as pd
import numpy as np
from dataframe_with_button import static_dataframe

from data.db_communication import PostgreSQL
from app.utils import convert_s_to_h, APP_SRC, DATABASE


def exposant_etape(number: int, rally_name: int, rally_year: int):
    determinant = "La"
    if number == 0:
        determinant = "Le"
        return (f"Prologue de {rally_name} {rally_year}", determinant)
    elif number == 1:
        return (f"{number}ʳᵉ étape du {rally_name} {rally_year}", determinant)
    else:
        return (f"{number}ᵉ étape du {rally_name} {rally_year}", determinant)


def get_crew_by_vehicule(vehicule: str):
    list_number_crew = DATABASE.execute(
        "SELECT c.id FROM crew AS c JOIN team AS t ON c.id_team = t.id WHERE t.type = %s",
        [vehicule],
    )
    return list_number_crew


def get_result_stage(id_stage: int, vehicule: str):
    list_number_crew = get_crew_by_vehicule(vehicule)
    crew_ids = [row[0] for row in list_number_crew]

    traductions = {"car": "voiture", "truck": "camion"}
    vehicule_fr = traductions.get(vehicule, "moto")

    result = DATABASE.read("result", condition_data={"id_stage": id_stage})
    df_result = pd.DataFrame(result)

    df_result = df_result[df_result["id_crew"].isin(crew_ids)]

    stage_result = df_result[["time", "id_crew"]].sort_values(
        by=["time"], ascending=True, key=lambda x: x.replace(0, np.inf)
    )

    df_teams_info = get_table_team_number_name_member()

    df_merged = stage_result.merge(df_teams_info, on="id_crew", how="left")

    df_display = pd.DataFrame()
    df_display["Classement"] = [
        str(i + 1) if val != 0 else "N/A"
        for i, val in enumerate(df_merged["time"])
    ]

    df_display["Équipe"] = df_merged["team_name"].astype(str)
    df_display["id_team"] = df_merged["id_team"]

    df_display["Temps"] = [
        convert_s_to_h(line) if line else "Disqualifié"
        for line in df_merged["time"]
    ]

    df_display["Pilote 1"] = df_merged["Pilote 1"]
    df_display["Pilote 2"] = df_merged["Pilote 2"]

    st.subheader(f"Classement {vehicule_fr}")

    st_table = static_dataframe(
        df_display[["Classement", "Équipe", "Temps", "Pilote 1", "Pilote 2"]],
        clickable_column="Équipe",
    )

    if st_table:
        st.session_state["id_team"] = df_display[
            df_display["Équipe"] == st_table
        ]["id_team"].iloc[0]
        st.switch_page(APP_SRC / "team.py")


def get_table_team_number_name_member():
    table_team_number_name_member = DATABASE.execute(
        "SELECT c.id, t.id, t.name, co.first_name, co.last_name "
        "FROM crew AS c "
        "JOIN contestant AS co ON co.id_crew = c.id "
        "JOIN team AS t ON t.id = c.id_team"
    )
    df = pd.DataFrame(
        table_team_number_name_member,
        columns=["id_crew", "id_team", "team_name", "first_name", "last_name"],
    )

    df["full_name"] = df["first_name"] + " " + df["last_name"]
    df["member_idx"] = df.groupby("id_crew").cumcount() + 1

    df_pivot = df.pivot(
        index=["id_crew", "id_team", "team_name"],
        columns="member_idx",
        values="full_name",
    ).reset_index()

    df_pivot.columns = [
        "id_crew",
        "id_team",
        "team_name",
        "Pilote 1",
        "Pilote 2",
    ]

    return df_pivot.fillna("")


def create_page():
    # id_contestant: int = st.session_state["id_contestant"]
    # id_rally: int = st.session_state["id_rally"]
    id_stage: int = st.session_state["id_stage"]

    stage = DATABASE.read("stage", condition_data={"id": id_stage})
    df_stage = pd.DataFrame(stage)
    id_rally = df_stage["id_rally"].item()

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

    get_result_stage(id_stage, "car")
    get_result_stage(id_stage, "truck")
    get_result_stage(id_stage, "motorbike")


if __name__ == "__main__":
    create_page()
