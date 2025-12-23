"""Module with utilitaries."""

from pathlib import Path

from data.db_communication import PostgreSQL

DATABASE = PostgreSQL(
    hostname="ep-curly-dew-ad41zuv8-pooler.c-2.us-east-1.aws.neon.tech",
    db_name="neondb",
    username="guest",
    password="project-rally",
    port=5432,
)

APP_SRC = Path(__file__).parent


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
