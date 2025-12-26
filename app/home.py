"""Home page of the streamlit app."""

from typing import Literal, TypedDict

import pandas as pd
import streamlit as st
from psycopg.errors import Error as SQLException
from psycopg.errors import InsufficientPrivilege
from streamlit_searchbox import st_searchbox

from app.utils import APP_SRC, DATABASE, TRAD_VEHICLE


class SearchDict(TypedDict):
    """Type for `elements` variable."""

    type: Literal["rally", "team", "stage"]
    id: int
    label: str


def create_elements() -> list[SearchDict]:
    """
    Create a list with search options.

    Returns
    -------
    list[SearchDict]
        List with search options: rallys, stages and teams.
    """
    elements: list[SearchDict] = []

    rallys = DATABASE.read("rally", ["id", "name", "year"])

    elements.extend(
        [
            {
                "type": "rally",
                "id": rally["id"],
                "label": f"{rally['name']} {rally['year']}",
            }
            for rally in rallys
        ]
    )

    stages = DATABASE.execute(
        "SELECT stage.id, stage.number, rally.name, rally.year FROM stage "
        "JOIN rally ON stage.id_rally = rally.id;"
    )

    elements.extend(
        [
            {
                "type": "stage",
                "id": stage[0],
                "label": (
                    f"{f'{stage[1]}e étape' if stage[1] else 'Prologue'} du "
                    f"{stage[2]} {stage[-1]}"
                ),
            }
            for stage in stages
        ]
    )

    teams = DATABASE.read("team")

    elements.extend(
        [
            {
                "type": "team",
                "id": team["id"],
                "label": f"{team['name']} ({TRAD_VEHICLE[team['type']]})",
            }
            for team in teams
        ]
    )

    return elements


def search_fn(search_term: str, elements: list[SearchDict]) -> list[str]:
    """
    Search function. For a search tearm, find corresponding labels.

    Parameters
    ----------
    search_term : str
        User search term.
    elements : list[SearchDict]
        List with search options: rallys, stages and teams.

    Returns
    -------
    list[str]
        List of labels matching the search term.
    """
    return [
        x["label"]
        for x in elements
        if search_term.lower() in x["label"].lower()
    ]


def change_page(select_label: str, elements: list[SearchDict]) -> None:
    """
    Change page after a search.

    Parameters
    ----------
    select_label : str
        Label selected by the user.
    elements : list[SearchDict]
        List with search options: rallys, stages and teams.
    """
    element = next(
        element for element in elements if element["label"] == select_label
    )

    if element["type"] == "rally":
        st.session_state["id_rally"] = element["id"]

        st.switch_page(APP_SRC / "rally.py")

    elif element["type"] == "stage":
        st.session_state["id_stage"] = element["id"]

        st.switch_page(APP_SRC / "stage.py")

    elif element["type"] == "team":
        st.session_state["id_team"] = element["id"]

        st.switch_page(APP_SRC / "team.py")


def create_section_exercises() -> None:
    """Create a section for exercices."""
    st.subheader("Exercices")

    st.write("Pour accéder aux exercices donnés par le sujet, cliquez ici :")
    button = st.button(
        "Accès à la page Exercices",
        key="exercises_button",
        use_container_width=True,
    )

    if button:
        st.switch_page(APP_SRC / "exercise.py")


def create_section_request() -> None:
    """Create a section for SQL requests."""
    st.subheader("Requêtes libres")

    query = st.text_area(
        "Entrez votre requête SQL", value="SELECT * FROM rally;", height=150
    )

    if st.button("Exécuter la requête"):
        try:
            results = DATABASE.execute(query)
            columns = [desc[0] for desc in DATABASE.cursor.description]
            st.dataframe(
                pd.DataFrame(data=results, columns=columns), hide_index=True
            )
        except InsufficientPrivilege:
            st.error("Vous n'avez pas les droits suffisants !")
        except SQLException as exc:
            st.error(f"Erreur SQL : {exc}")


def create_page() -> None:
    """Create the home page."""
    st.title("Page d'accueil")

    elements = create_elements()

    st_searchbox(
        search_fn,
        placeholder="Rechercher un rally, une étape ou une équipe",
        elements=elements,
        submit_function=lambda s: change_page(s, elements),
    )

    create_section_exercises()

    create_section_request()


if __name__ == "__main__":
    create_page()
