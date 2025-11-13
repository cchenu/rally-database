"""Script to fill our database with fake data."""

from db_communication import PostgreSQL

DATABASE = PostgreSQL("localhost", "rally", "postgres", "postgres", 5432)


def fill_rally(database: PostgreSQL) -> None:
    """
    Fill rally table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    database.write(
        "rally",
        [{"year": year, "name": "Paris Dakar"} for year in range(1979, 2026)],
    )


if __name__ == "__main__":
    fill_rally(DATABASE)
