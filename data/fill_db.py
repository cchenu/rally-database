"""Script to fill our database with fake data."""

import operator
import random
import string
import time
from pathlib import Path
from typing import Any

import pandas as pd
from db_communication import PostgreSQL
from faker import Faker
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from geopy.location import Location

<<<<<<< HEAD
from data.db_communication import PostgreSQL

=======
>>>>>>> f1cf7ef1dbc9dceb221e6422657157affe92d3cf
DATABASE = PostgreSQL(
    hostname="ep-curly-dew-ad41zuv8-pooler.c-2.us-east-1.aws.neon.tech",
    db_name="neondb",
    username="guest",
    password="project-rally",
    port=5432,
)
FAKE = Faker("fr_FR")


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
        except GeocoderUnavailable:
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


def fill_team(database: PostgreSQL) -> None:
    """
    Fill team table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    types = ["car", "truck", "motorbike"]

    list_teams = [FAKE.company() for _ in range(50)]
    list_dicts: list[dict[str, Any]] = [
        {"name": team, "type": type_}
        for team in list_teams
        for type_ in random.sample(types, k=random.randint(1, 3))
    ]

    for dict_row in list_dicts:
        dict_row["budget"] = round(random.uniform(100_000, 10_000_000), 2)
        dict_row["official"] = bool(random.randint(0, 1))

    database.write("team", list_dicts)


def fill_team_sponsor(database: PostgreSQL) -> None:
    """
    Fill team_sponsor table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    team_ids = database.read("team", "id", return_type="list")

    list_dicts: list[dict[str, Any]] = []

    for team_id in team_ids:
        list_dicts.extend(
            [
                {"id_team": team_id, "name": FAKE.company()}
                for _ in range(random.randint(0, 6))
            ]
        )

    database.write("team_sponsor", list_dicts)


def fill_crew(database: PostgreSQL) -> None:
    """
    Fill crew table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    team_ids = database.read("team", "id", return_type="list")

    list_dicts: list[dict[str, Any]] = []

    for i, team_id in enumerate(team_ids):
        list_dicts.append({"id_team": team_id, "number": i + 1})

    database.write("crew", list_dicts)


def fill_contestant(database: PostgreSQL) -> None:
    """
    Fill contestant table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    crew_ids = database.read("crew", "id", return_type="list")

    list_dicts: list[dict[str, Any]] = []

    list_citizenships = [
        ("Sud Africain", "en_US"),
        ("Argentin", "es_AR"),
        ("Belge", "fr_BE"),
        ("Brésilien", "pt_BR"),
        ("Esapgnol", "es_ES"),
        ("Estonien", "et_EE"),
        ("Américain", "en_US"),
        ("Français", "fr_FR"),
        ("Italien", "it_IT"),
        ("Lituanien", "lt_LT"),
        ("Néerlandais", "nl_NL"),
        ("Polonais", "pl_PL"),
        ("Suédois", "sv_SE"),
        ("Suisse", "fr_CH"),
        ("Tchèque", "cs_CZ"),
    ]

    for crew_id in crew_ids:
        participation_number = random.randint(1, 10)

        for _ in range(2):
            citizenship, local = random.choice(list_citizenships)

            fake_local = Faker(local)

            list_dicts.append(
                {
                    "last_name": fake_local.last_name(),
                    "first_name": fake_local.first_name(),
                    "address": fake_local.address(),
                    "citizenship": citizenship,
                    "participation_number": participation_number,
                    "id_crew": crew_id,
                }
            )

    database.write("contestant", list_dicts)


def fill_vehicle(database: PostgreSQL) -> None:
    """
    Fill vehicle table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    crew_ids = database.read("crew", "id", return_type="list")

    list_dicts: list[dict[str, Any]] = []

    constructors = [
        "Peugeot",
        "Citroën",
        "Renault",
        "Audi",
        "Volkswagen",
        "MINI",
        "Mitsubishi",
        "Toyota",
        "Nissan",
        "Ford",
        "KTM",
        "Honda",
        "Yamaha",
        "Suzuki",
        "Husqvarna",
        "GasGas",
        "Kamaz",
        "Tatra",
        "Iveco",
        "Mercedes-Benz",
    ]
    engine_sizes = [125, 250, 450, 690, 800, 1000, 3000, 3500]

    for i, crew_id in enumerate(crew_ids):
        list_dicts.append(
            {
                "number": i + 1,
                "constructor": random.choice(constructors),
                "engine_size": random.choice(engine_sizes),
                "serie_number": FAKE.bothify(
                    "??##-####-????", letters=string.ascii_uppercase
                ),
                "id_crew": crew_id,
            }
        )

    database.write("vehicle", list_dicts)


def fill_supplier(database: PostgreSQL) -> None:
    """
    Fill supplier table and rally_sponsor table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    rally_ids = database.read("rally", "id", return_type="list")

    for table in ("supplier", "rally_sponsor"):
        list_dicts: list[dict[str, Any]] = []

        for rally_id in rally_ids:
            list_dicts.extend(
                [
                    {"id_rally": rally_id, "name": FAKE.company()}
                    for _ in range(random.randint(0, 6))
                ]
            )

        database.write(table, list_dicts)


def fill_result(database: PostgreSQL) -> None:
    """
    Fill result table of `database`.

    Parameters
    ----------
    database : PostgreSQL
        Database to be filled.
    """
    stages = database.read(
        "stage", ["id", "id_rally", "type", "max_time", "number", "kilometers"]
    )
    crews = database.read("crew", ["id", "id_team"])
    participations = database.read("participation", ["id_rally", "id_team"])

    list_dicts: list[dict[str, Any]] = []

    for crew in crews:
        rally_of_the_crew = [
            p["id_rally"]
            for p in participations
            if p["id_team"] == crew["id_team"]
        ]

        for rally in rally_of_the_crew:
            stage_of_the_rally_of_the_crew = sorted(
                [s for s in stages if s["id_rally"] == rally],
                key=operator.itemgetter("number"),
            )

            for stage in stage_of_the_rally_of_the_crew:
                time = 0
                disqualification = False

                if stage["type"] == "special":
                    time = random.randint(
                        int(0.8 * stage["max_time"]),
                        int(1.02 * stage["max_time"]),
                    )

                    if time > stage["max_time"]:
                        disqualification = True

                else:
                    vitesse = 0.028  # km/s
                    time = random.randint(
                        int(0.8 * stage["kilometers"] / vitesse),
                        int(1.2 * stage["kilometers"] / vitesse),
                    )

                crash_probability = 0.02
                if random.random() < crash_probability:
                    disqualification = True
                    time = 0

                list_dicts.append(
                    {
                        "id_stage": stage["id"],
                        "id_crew": crew["id"],
                        "time": time,
                        "disqualification": disqualification,
                    }
                )
                if disqualification:
                    break

    database.write("result", list_dicts)


if __name__ == "__main__":
<<<<<<< HEAD
    #fill_result(DATABASE)
    print(DATABASE.read("result"))
    
=======
    DATABASE.read("result")
>>>>>>> f1cf7ef1dbc9dceb221e6422657157affe92d3cf
