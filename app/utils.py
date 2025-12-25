"""Module with utilitaries."""

from pathlib import Path
from typing import Literal

import streamlit as st

from data.db_communication import PostgreSQL

DATABASE = PostgreSQL(
    hostname="ep-curly-dew-ad41zuv8-pooler.c-2.us-east-1.aws.neon.tech",
    db_name="neondb",
    username="guest",
    password="project-rally",
    port=5432,
)

APP_SRC = Path(__file__).parent

TRAD_VEHICLE: dict[str, str] = {
    "car": "voiture",
    "motorbike": "moto",
    "truck": "camion",
}


def get_leaderboard(
    id_rally: int, vehicle: Literal["car", "truck", "motorbike"]
) -> list[tuple[str, float, str, str, str, str, int, bool]]:
    """
    Get the leaderboard of a rally for a given category.

    Parameters
    ----------
    id_rally : int
        ID of the rally in the database.
    vehicle : Literal["car", "truck", "motorbike"]
        Type of vehicle.

    Returns
    -------
    list[tuple[str, float, str, str, str, str, int, bool]]
        Leaderboard with team name, time, first_name of contestant 1, last
        name, first_name of contestant 2, last name, team ID and
        disqualification status.
    """
    if f"leaderboard_{id_rally}_{vehicle}" in st.session_state:
        leaderboard: list[tuple[str, float, str, str, str, str, int, bool]] = (
            st.session_state[f"leaderboard_{id_rally}_{vehicle}"]
        )
        return leaderboard

    leaderboard = DATABASE.execute(
        "SELECT team.name, SUM(result.time) AS total_time, c1.first_name, "
        "c1.last_name, c2.first_name, c2.last_name, team.id, "
        "BOOL_OR(result.disqualification) as disquali "
        "FROM crew "
        "JOIN result ON result.id_crew = crew.id "
        "JOIN stage ON stage.id = result.id_stage "
        "JOIN team ON team.id = crew.id_team "
        "JOIN contestant c1 ON c1.id_crew = crew.id "
        "JOIN contestant c2 ON c2.id_crew = crew.id AND c2.id > c1.id "
        "WHERE stage.id_rally = %s AND team.type = %s "
        "GROUP BY team.name, c1.first_name, c1.last_name, c2.first_name, "
        "c2.last_name, team.id "
        "ORDER BY disquali ASC, total_time ASC;",
        [id_rally, vehicle],
    )
    st.session_state[f"leaderboard_{id_rally}_{vehicle}"] = leaderboard
    return leaderboard


def convert_s_to_h(seconds: float) -> str:
    """
    Convert second into a string which give it in hours.

    Parameters
    ----------
    seconds : float
        Number of seconds.

    Returns
    -------
    str
        String with hour. For example: 1 h 06 min.
    """
    return f"{int(seconds // 3600)} h {int(seconds % 3600 // 60):02} min"
