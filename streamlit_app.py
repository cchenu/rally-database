"""Entry point of the streamlit app."""

import streamlit as st

from app.utils import APP_SRC


def create_app() -> None:
    """Create the streamlit app."""
    home_page = st.Page(
        APP_SRC / "home.py",
        title="Page d'accueil",
        icon=":material/home:",
    )
    exercise_page = st.Page(
        APP_SRC / "exercise.py",
        title="Exercices",
        icon=":material/assignment:",
    )
    rally_page = st.Page(
        APP_SRC / "rally.py",
        title="Page rally",
        icon=":material/directions_car:",
    )
    stage_page = st.Page(
        APP_SRC / "stage.py", title="Page étape", icon=":material/map:"
    )
    team_page = st.Page(
        APP_SRC / "team.py", title="Page équipe", icon=":material/person:"
    )

    st.set_page_config(layout="wide")

    pg = st.navigation(
        {
            "Home": [home_page],
            "Tâches": [exercise_page],
            "Détails": [rally_page, stage_page, team_page],
        }
    )

    if "id_rally" not in st.session_state:
        st.session_state["id_rally"] = 580

    if "id_team" not in st.session_state:
        st.session_state["id_team"] = 42

    if "id_stage" not in st.session_state:
        st.session_state["id_stage"] = 326

    pg.run()


if __name__ == "__main__":
    create_app()
