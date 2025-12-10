"""Entry point of the streamlit app."""

# L'objectif de ça est de faire en sorte de pouvoir importer les fonctions SQL
# de db_communication dans les fichiers sous app
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
# -------------


def create_app() -> None:
    home_page = st.Page(
        "home.py", title="Rally application", icon=":material/home:"
    )
    exercise_page = st.Page(
        "exercise.py", title="Exercise", icon=":material/assignment:"
    )
    rally_page = st.Page(
        "rally.py", title="Rally", icon=":material/directions_car:"
    )
    stage_page = st.Page("stage.py", title="Stage", icon=":material/map:")
    contestant_page = st.Page(
        "contestant.py", title="Contestant", icon=":material/person:"
    )

    st.set_page_config(layout="wide")

    pg = st.navigation(
        {
            "Hub": [home_page],
            "Assignment": [exercise_page],
            "Reports": [rally_page, stage_page, contestant_page],
        }
    )

    if "id_rally" not in st.session_state:
        st.session_state["id_rally"] = 576

    if "id_contestant" not in st.session_state:
        st.session_state["id_contestant"] = 419

    if "id_stage" not in st.session_state:
        st.session_state["id_stage"] = 326

    pg.run()


if __name__ == "__main__":
    create_app()
