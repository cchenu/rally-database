"""Streamlit page to have information about a given rally."""

from typing import Any, Literal

import pandas as pd
import streamlit as st
from dataframe_with_button import static_dataframe

from app.utils import APP_SRC, DATABASE, convert_s_to_h, get_leaderboard


def get_city(id_city: int) -> tuple[str, str]:
    """
    Get city and country from an ID.

    Parameters
    ----------
    id_city : int
        ID of the city in the database.

    Returns
    -------
    str
        French name of the city.
    str
        French name of the country.
    """
    city, country = DATABASE.read(
        "city", ["name", "country"], {"id": id_city}, return_type="list"
    )[0]

    return city, country


def get_team_numbers(
    id_rally: int, vehicle: Literal["car", "truck", "motorbike"]
) -> int:
    """
    Find number of participating teams in a rally for a type of vehicle.

    Parameters
    ----------
    id_rally : int
        ID of the rally in the database.
    vehicle : Literal["car", "truck", "motorbike"]
        Type of vehicle.

    Returns
    -------
    int
        Number of participating type in a rally for a category.
    """
    team_numbers: int = DATABASE.execute(
        "SELECT COUNT(*) "
        "FROM team JOIN participation ON team.id = id_team "
        "WHERE id_rally = %s AND team.type = %s;",
        [id_rally, vehicle],
    )[0][0]

    return team_numbers


def create_table_leaderboard(
    leaderboard: list[tuple[str, float, str, str, str, str, int, bool]],
    vehicle: str,
) -> None:
    """
    Create a streamlit table for leaderboard of a rally for a given category.

    Parameters
    ----------
    leaderboard : list[tuple[str, float, str, str, str, str, int, bool]]
        Leaderboard with team name, time, first name of contestant 1, last
        name, first_name of contestant 2, last name, team ID and
        disqualification status.
    vehicle : str
        Type of vehicle.
    """
    st.subheader(f"Classement {vehicle}")

    df_leaderboard = pd.DataFrame(
        columns=[
            "Classement",
            "Équipe",
            "Temps",
            "Pilote 1",
            "Pilote 2",
        ]
    )

    df_leaderboard["Classement"] = [
        str(i + 1) if not line[-1] else "N/A"
        for i, line in enumerate(leaderboard)
    ]
    df_leaderboard["Équipe"] = [line[0] for line in leaderboard]
    df_leaderboard["Temps"] = [
        convert_s_to_h(line[1]) if not line[-1] else "Disqualifié"
        for line in leaderboard
    ]
    df_leaderboard["Pilote 1"] = [
        f"{line[2]} {line[3]}" for line in leaderboard
    ]
    df_leaderboard["Pilote 2"] = [
        f"{line[4]} {line[5]}" for line in leaderboard
    ]

    st_table = static_dataframe(df_leaderboard, clickable_column="Équipe")

    if st_table:
        st.session_state["id_team"] = next(
            line[-2] for line in leaderboard if line[0] == st_table
        )
        st.switch_page(APP_SRC / "team.py")


def create_table_stages(list_stages: list[dict[str, Any]]) -> None:
    """
    Create a streamlit table for stages of a rally.

    Parameters
    ----------
    list_stages : list[dict[str, Any]]
        List of stages of a given rally.
    """
    st.subheader("Étapes")
    df_stages = pd.DataFrame(list_stages).rename(
        {
            "number": "Étape",
            "id_starting_city": "Départ",
            "id_ending_city": "Arrivée",
            "type": "Type",
            "kilometers": "Distance (km)",
        },
        axis=1,
    )
    df_stages["Étape"] = df_stages["Étape"].replace(0, "Prologue")

    df_stages["Départ"] = df_stages["Départ"].apply(get_city)
    df_stages["Départ"] = (
        df_stages["Départ"].str[0] + " (" + df_stages["Départ"].str[1] + ")"
    )

    df_stages["Arrivée"] = df_stages["Arrivée"].apply(get_city)
    df_stages["Arrivée"] = (
        df_stages["Arrivée"].str[0] + " (" + df_stages["Arrivée"].str[1] + ")"
    )

    df_stages["Type"] = (
        df_stages["Type"]
        .replace("special", "Spéciale")
        .replace("linking", "Liaison")
    )

    st_table = static_dataframe(
        df_stages.drop("id", axis="columns"), clickable_column="Étape"
    )

    if st_table:
        st.session_state["id_stage"] = df_stages[
            df_stages["Étape"] == st_table
        ]["id"].iloc[0]
        st.switch_page(APP_SRC / "stage.py")


def create_section_partners(id_rally: int) -> None:
    """
    Create the section with the partner of a given rally.

    Parameters
    ----------
    id_rally : int
        ID of the rally in the database.
    """
    sponsors = DATABASE.read(
        "rally_sponsor", "name", {"id_rally": id_rally}, return_type="list"
    )
    suppliers = DATABASE.read(
        "supplier", "name", {"id_rally": id_rally}, return_type="list"
    )

    if sponsors or suppliers:
        st.subheader("Partenaires")

        if sponsors:
            st.markdown("**Sponsors :**\n- " + "\n- ".join(sponsors))

        if suppliers:
            st.markdown("**Fournisseurs :**\n- " + "\n- ".join(suppliers))


def create_page() -> None:
    """Create a page about a rally."""
    id_rally: int = st.session_state["id_rally"]

    rally, year = DATABASE.read(
        "rally",
        ["name", "year"],
        {"id": id_rally},
        return_type="list",
    )[0]

    st.title(f"{rally} {year}")

    list_stages: list[dict[str, Any]] = DATABASE.read(
        "stage",
        [
            "id",
            "number",
            "id_starting_city",
            "id_ending_city",
            "type",
            "kilometers",
        ],
        {"id_rally": id_rally},
    )

    starting_city, starting_country = get_city(
        list_stages[0]["id_starting_city"]
    )
    ending_city, ending_country = get_city(list_stages[-1]["id_ending_city"])

    num_cars = get_team_numbers(id_rally, "car")
    num_trucks = get_team_numbers(id_rally, "truck")
    num_motorbikes = get_team_numbers(id_rally, "motorbike")

    leaderboard_car = get_leaderboard(id_rally, "car")
    leaderboard_truck = get_leaderboard(id_rally, "truck")
    leaderboard_motorbike = get_leaderboard(id_rally, "motorbike")

    winners_car = (
        f"{leaderboard_car[0][2]} {leaderboard_car[0][3]} "
        f"et {leaderboard_car[0][4]} {leaderboard_car[0][5]}"
    )
    winners_truck = (
        f"{leaderboard_truck[0][2]} {leaderboard_truck[0][3]} "
        f"et {leaderboard_truck[0][4]} {leaderboard_truck[0][5]}"
    )
    winners_motorbike = (
        f"{leaderboard_motorbike[0][2]} {leaderboard_motorbike[0][3]} "
        f"et {leaderboard_motorbike[0][4]} {leaderboard_motorbike[0][5]}"
    )

    st.write(
        f"{rally} {year} se déroule entre les villes de {starting_city} "
        f"({starting_country}) et {ending_city} ({ending_country}). Cette "
        f"édition voit s'affronter {num_cars + num_trucks + num_motorbikes}"
        f" équipes dont {num_cars} en voiture, {num_trucks} en camion et "
        f"{num_motorbikes} à moto. La catégorie voiture voit s'imposer "
        f"{winners_car}, la catégorie camion {winners_truck} et la catégorie "
        f"moto {winners_motorbike}."
    )

    create_table_leaderboard(leaderboard_car, "voiture")
    create_table_leaderboard(leaderboard_truck, "camion")
    create_table_leaderboard(leaderboard_motorbike, "moto")

    create_table_stages(list_stages)

    create_section_partners(id_rally)


if __name__ == "__main__":
    create_page()
