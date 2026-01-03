"""Streamlit page to have information about a given stage."""

from typing import Literal

import numpy as np
import pandas as pd
import streamlit as st
from dataframe_with_button import static_dataframe

from app.utils import APP_SRC, DATABASE, Vehicle, convert_s_to_h


def stage_name(
    number: int, rally_name: int, rally_year: int
) -> tuple[str, Literal["Le", "La"]]:
    """
    Write the stage name with the determiner.

    Parameters
    ----------
    number : int
        Number of the stage. For prologue, number is 0.
    rally_name : int
        Name of the rally.
    rally_year : int
        Year of the rally.

    Returns
    -------
    str
        Stage name in French.
    Literal["Le", "La"]
        Determiner according to the stage.
    """
    determiner: Literal["Le", "La"] = "La"
    if number == 0:
        determiner = "Le"
        return (f"Prologue de {rally_name} {rally_year}", determiner)
    if number == 1:
        return (f"{number}ʳᵉ étape du {rally_name} {rally_year}", determiner)
    return (f"{number}ᵉ étape du {rally_name} {rally_year}", determiner)


def get_crew_by_vehicle(vehicle: Vehicle) -> list[tuple[int]]:
    """
    Get all crew IDs for one type of vehicle.

    Parameters
    ----------
    vehicle : Vehicle
        Type of vehicle.

    Returns
    -------
    list[tuple[int]]
        Crew IDs of one category.
    """
    return DATABASE.execute(
        "SELECT c.id FROM crew AS c JOIN team AS t ON c.id_team = t.id "
        "WHERE t.type = %s",
        [vehicle],
    )


def get_result_stage(id_stage: int, vehicle: Vehicle) -> None:
    """
    Create the result table for a vehicle category and the given stage.

    Parameters
    ----------
    id_stage : int
        ID of the stage in the database.
    vehicle : Vehicle
        Type of vehicle.
    """
    list_number_crew = get_crew_by_vehicle(vehicle)
    crew_ids = [row[0] for row in list_number_crew]

    traductions = {"car": "voiture", "truck": "camion"}
    vehicle_fr = traductions.get(vehicle, "moto")

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

    st.subheader(f"Classement {vehicle_fr}")

    st_table = static_dataframe(
        df_display[["Classement", "Équipe", "Temps", "Pilote 1", "Pilote 2"]],
        clickable_column="Équipe",
    )

    if st_table:
        st.session_state["id_team"] = df_display[
            df_display["Équipe"] == st_table
        ]["id_team"].iloc[0]
        st.switch_page(APP_SRC / "team.py")


def get_table_team_number_name_member() -> pd.DataFrame:
    """
    Get table with crew ID, team ID, team name and driver names.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns `id_crew`, `id_team`, `team_name`, `Pilote 1`
        and `Pilote 2`.
    """
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

    df_pivot = df.pivot_table(
        index=["id_crew", "id_team", "team_name"],
        columns="member_idx",
        values="full_name",
        aggfunc="first",
    ).reset_index()

    df_pivot.columns = [
        "id_crew",
        "id_team",
        "team_name",
        "Pilote 1",
        "Pilote 2",
    ]

    return df_pivot.fillna("")


def create_button(stage_number: int, id_rally: int) -> None:
    """
    Create buttons to navigate to the previous and next stages.

    Parameters
    ----------
    stage_number : int
        Number of the stage
    id_rally : int
        ID of the rally in the database.
    """
    col1, _, _, _, col5 = st.columns(5)
    if stage_number != 0:
        previous_stage: list[int] = DATABASE.read(
            "stage",
            "id",
            condition_data={"number": stage_number - 1, "id_rally": id_rally},
            return_type="list",
        )
        if previous_stage:
            with col1:
                if st.button("Étape précédente"):
                    st.session_state["id_stage"] = previous_stage[0]
                    st.rerun()

    next_stage: list[int] = DATABASE.read(
        "stage",
        "id",
        condition_data={"number": stage_number + 1, "id_rally": id_rally},
        return_type="list",
    )
    if next_stage:
        with col5:
            if st.button("Étape suivante"):
                st.session_state["id_stage"] = next_stage[0]
                st.rerun()


def create_page() -> None:
    """Create a page about a stage."""
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
    st.title(stage_name(number, rally_name, rally_year)[0])

    st.text(
        f"{stage_name(number, rally_name, rally_year)[1]} "
        f"{stage_name(number, rally_name, rally_year)[0]} "
        f"se déroule de {city_depart} à {city_arrivee} sur une distance de "
        f"{distance_stage} km."
    )

    get_result_stage(id_stage, "car")
    get_result_stage(id_stage, "truck")
    get_result_stage(id_stage, "motorbike")

    create_button(df_stage["number"].item(), id_rally)


if __name__ == "__main__":
    create_page()
