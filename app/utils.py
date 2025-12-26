"""Module with utilitaries."""

import os
from pathlib import Path
from typing import Literal

import streamlit as st
from dotenv import load_dotenv

from data.db_communication import PostgreSQL


def getenv_str(name: str) -> str:
    """
    Get environment variable which is a string.

    Parameters
    ----------
    name : str
        Name of the environment variable.

    Returns
    -------
    str
        Value of the environment variable.

    Raises
    ------
    RuntimeError
        Missing environment variable.
    """
    value = os.getenv(name)
    if value is None:
        exception_text = f"Missing environment variable: {name}"
        raise RuntimeError(exception_text)
    return value


def getenv_int(name: str) -> int:
    """
    Get environment variable which must be an integer.

    Parameters
    ----------
    name : str
        Name of the environment variable.

    Returns
    -------
    int
        Value of the environment variable as an integer.

    Raises
    ------
    RuntimeError
        Missing environment variable.
    RuntimeError
        Environment variable is not an integer.
    """
    value = os.getenv(name)
    if value is None:
        exception_text = f"Missing environment variable: {name}"
        raise RuntimeError(exception_text)
    try:
        return int(value)
    except ValueError as exc:
        exception_text = (
            f"Environment variable {name} must be an integer, got {value!r}"
        )
        raise RuntimeError(exception_text) from exc


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


load_dotenv(override=True)
DATABASE = PostgreSQL(
    hostname=getenv_str("HOSTNAME"),
    db_name=getenv_str("DB_NAME"),
    username=getenv_str("USERNAME"),
    password=getenv_str("PASSWORD"),
    port=getenv_int("PORT"),
)

APP_SRC = Path(__file__).parent

TRAD_VEHICLE: dict[str, str] = {
    "car": "voiture",
    "motorbike": "moto",
    "truck": "camion",
}
