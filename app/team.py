"""Streamlit page to have information about a given team."""

from typing import Any, TypedDict

import pandas as pd
import streamlit as st
from dataframe_with_button import static_dataframe

from app.utils import APP_SRC, DATABASE, TRAD_VEHICLE, Vehicle, get_leaderboard


class TeamInfo(TypedDict):
    """Type for `team_info` variable."""

    name: str
    budget: float
    type: Vehicle
    id_crew: int
    constructor: str
    engine_size: float
    serie_number: str


def create_section_member(member: dict[str, Any]) -> None:
    """
    Create the section about a team member.

    Parameters
    ----------
    member : dict[str, Any]
        Information about the member. Must have keys 'first_name', 'last_name',
        'citizenship' and 'address'.
    """
    st.markdown(
        f"**{member['first_name']} {member['last_name']}**\n- "
        f"Citoyenneté : {member['citizenship']} \n- "
        f"Adresse : {member['address']}"
    )


def get_rank(id_rally: int, id_team: int, vehicle: Vehicle) -> str:
    """
    Get the rank of a team for a rally.

    Parameters
    ----------
    id_rally : int
        ID of the rally.
    id_team : int
        ID of the team.
    vehicle : Vehicle
        Type of vehicle.

    Returns
    -------
    str
        Formatting rank of the team in the rally. If disqualified, return
        "Disqualifiée".
    """
    leaderboard = get_leaderboard(id_rally, vehicle)
    id_teams = [line[-2] for line in leaderboard if not line[-1]]

    if id_team in id_teams:
        return f"{id_teams.index(id_team) + 1}ᵉ"

    return "Disqualifiée"


def create_section_races(id_team: int, vehicle: Vehicle) -> None:
    """
    Create a section about all races of a team.

    Parameters
    ----------
    id_team : int
        ID of the team.
    vehicle : Vehicle
        Type of vehicle.
    """
    st.subheader("Courses")

    rallys = DATABASE.read(
        "race_by_team",
        ["id", "name", "year"],
        {"id_team": id_team},
        return_type="dict",
    )

    df_rallys = pd.DataFrame(rallys)
    df_rallys["Rallye"] = (
        df_rallys["name"] + " " + df_rallys["year"].astype(str)
    )
    df_rallys["Classement"] = df_rallys["id"].apply(
        lambda id_rally: get_rank(id_rally, id_team, vehicle)
    )

    st_table = static_dataframe(df_rallys[["Rallye", "Classement"]], "Rallye")

    if st_table:
        st.session_state["id_rally"] = df_rallys[
            df_rallys["Rallye"] == st_table
        ]["id"].iloc[0]
        st.switch_page(APP_SRC / "rally.py")


def create_section_vehicle(team_info: TeamInfo) -> None:
    """
    Create a section about a vehicle.

    Parameters
    ----------
    team_info : TeamInfo
        Information about the team.
    """
    st.subheader("Véhicule")

    st.markdown(
        f"- Constructeur : {team_info['constructor']}\n- "
        f"Cylindrée : {int(team_info['engine_size'])} cm³ \n- "
        f"Numéro de série : {team_info['serie_number']}"
    )


def create_section_sponsors(id_team: int) -> None:
    """
    Create a section about team sponsors.

    Parameters
    ----------
    id_team : int
        ID of the team.
    """
    sponsors: list[str] = DATABASE.read(
        "team_sponsor", "name", {"id_team": id_team}, return_type="list"
    )

    if sponsors:
        st.subheader("Sponsors")
        st.markdown("- " + "\n- ".join(sponsors))


def create_page() -> None:
    """Create the Streamlit page about a team."""
    id_team: int = st.session_state["id_team"]

    team_info: TeamInfo = DATABASE.read(
        "team_info",
        [
            "name",
            "budget",
            "type",
            "id_crew",
            "constructor",
            "engine_size",
            "serie_number",
        ],
        {"id_team": id_team},
        return_type="list[dict]",
    )[0]

    members = DATABASE.read(
        "contestant",
        [
            "last_name",
            "first_name",
            "address",
            "citizenship",
            "participation_number",
        ],
        {"id_crew": team_info["id_crew"]},
    )

    st.title(team_info["name"])

    st.write(
        f"{team_info['name']} est une équipe de catégorie "
        f"{TRAD_VEHICLE[team_info['type']]} composée de "
        f"{members[0]['first_name']} {members[0]['last_name']} et "
        f"{members[1]['first_name']} {members[1]['last_name']}. Elle a "
        f"participé à {members[1]['participation_number']} "
        f"rallye{'s' if members[1]['participation_number'] > 1 else ''} "
        f"avec une {team_info["constructor"]}. Elle possède un budget de "
        f"{int(team_info["budget"])} €."
    )

    st.subheader("Membres")
    col1, col2 = st.columns(2, border=True)

    with col1:
        create_section_member(members[0])

    with col2:
        create_section_member(members[1])

    create_section_races(id_team, team_info["type"])

    create_section_vehicle(team_info)
    create_section_sponsors(id_team)


if __name__ == "__main__":
    create_page()
