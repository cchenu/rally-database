"""Home page of the streamlit app."""

from typing import Any, Literal, TypedDict

import streamlit as st
from streamlit_searchbox import st_searchbox

from app.utils import APP_SRC, DATABASE, TRAD_VEHICLE


class SearchDict(TypedDict):
    """Type for `elements` variable."""

    type: Literal["rally", "team", "stage"]
    id: int
    label: str


def create_elements() -> list[SearchDict]:
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


def search_fn(searchterm: str, elements: list[SearchDict]) -> list[str]:

    return [
        x["label"]
        for x in elements
        if searchterm.lower() in x["label"].lower()
    ]


def change_page(select_label: str, elements: list[SearchDict]) -> None:
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


def create_page() -> None:
    st.title("Home Page")

    elements = create_elements()

    selected = st_searchbox(
        search_fn,
        placeholder="Rechercher un rally, une étape ou une équipe",
        elements=elements,
        submit_function=lambda s: change_page(s, elements),
    )


if __name__ == "__main__":
    create_page()
