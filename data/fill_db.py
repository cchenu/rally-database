"""Script to fill our database with fake data."""

import random
import time
from pathlib import Path

import pandas as pd
from db_communication import PostgreSQL
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from geopy.location import Location

DATABASE = PostgreSQL("localhost", "rally", "postgres", "postgres", 5432)


def fill_rally(database: PostgreSQL) -> None:
    """
    Fill rally table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    canceled_year = 2008
    database.write(
        "rally",
        [
            {"year": year, "name": "Paris Dakar"}
            for year in range(1995, 2015)
            if year != canceled_year
        ],
    )


def get_location(geolocator: Nominatim, city_name: str) -> Location:
    """
    Give Location object of the given city. Handle error in geopy.

    Parameters
    ----------
    geolocator: Nominatim
        Object to use geopy.
    city_name : str
        City name in French.

    Returns
    -------
    Location
        Location object of the city.
    """
    if city_name == "Saint-Louis":
        city_name += ", Sénégal"
    elif city_name == "Nara":
        city_name += ", Mali"
    elif city_name in {"Waha", "Zillah"}:
        city_name += ", Libye"
    elif city_name in {
        "Santa Rosa",
        "San Rafael",
        "La Rioja",
        "Còrdoba",
        "San Juan",
        "Argentine",
        "San Luis",
    }:
        city_name += ", Argentine"
    elif city_name == "El Salvador":
        city_name += ", Chili"

    while True:
        try:
            return geolocator.geocode(city_name, language="fr")
        except GeocoderTimedOut:
            time.sleep(1)


def fill_stage(database: PostgreSQL) -> None:
    """
    Fill stage table and city table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    geolocator = Nominatim(user_agent="m")

    df_stages = pd.read_csv(Path(__file__).parent / "stages.csv")

    # Fill city table
    df_cities = pd.DataFrame(
        pd.concat(
            (df_stages["starting_city"], df_stages["ending_city"])
        ).unique(),
        columns=["name"],
    )

    df_cities["location"] = df_cities["name"].apply(
        lambda city: get_location(geolocator, city)
    )

    df_cities["country"] = df_cities["location"].apply(
        lambda loc: loc.address.split(", ")[-1]
    )
    df_cities["lat"] = df_cities["location"].apply(lambda loc: loc.latitude)
    df_cities["long"] = df_cities["location"].apply(lambda loc: loc.longitude)

    df_cities = df_cities.drop("location", axis="columns")

    df_cities["id"] = range(1, len(df_cities) + 1)

    database.write("city", [row[1].to_dict() for row in df_cities.iterrows()])

    # Fill stage table
    rallys = database.read("rally", ["id", "year"])
    rallys_dict = {row["year"]: row["id"] for row in rallys}

    df_stages["id_rally"] = df_stages["year"].apply(lambda y: rallys_dict[y])

    df_stages["id_starting_city"] = df_stages["starting_city"].apply(
        lambda c: int(df_cities.loc[df_cities["name"] == c, "id"].iloc[0])
    )

    df_stages["id_ending_city"] = df_stages["ending_city"].apply(
        lambda c: int(df_cities.loc[df_cities["name"] == c, "id"].iloc[0])
    )

    df_stages["kilometers"] = [
        random.randint(200, 850) for _ in range(len(df_stages))
    ]

    df_stages["type"] = random.choices(
        ["linking", "special"], weights=[0.3, 0.7], k=len(df_stages)
    )

    min_time = 3 * 3600
    max_time = 6 * 3600
    df_stages["max_time"] = df_stages["type"].apply(
        lambda t: random.randint(min_time, max_time) if t == "special" else 0
    )

    df_stages = df_stages.drop(
        ["starting_city", "ending_city", "year"], axis="columns"
    )
    database.write("stage", [row[1].to_dict() for row in df_stages.iterrows()])


if __name__ == "__main__":
    fill_rally(DATABASE)
    fill_stage(DATABASE)
