"""Entry point of the streamlit app."""

import streamlit as st

from app.utils import APP_SRC


def create_app() -> None:
    """Create the streamlit app."""
    home_page = st.Page(
        APP_SRC / "home.py",
        title="Rally application",
        icon=":material/home:",
    )
    exercise_page = st.Page(
        APP_SRC / "exercise.py",
        title="Exercise",
        icon=":material/assignment:",
    )
    rally_page = st.Page(
        APP_SRC / "rally.py",
        title="Rally",
        icon=":material/directions_car:",
    )
    stage_page = st.Page(
        APP_SRC / "stage.py", title="Stage", icon=":material/map:"
    )
    team_page = st.Page(
        APP_SRC / "team.py", title="Team", icon=":material/person:"
    )

    st.set_page_config(layout="wide")

    pg = st.navigation(
        {
            "Hub": [home_page],
            "Assignment": [exercise_page],
            "Reports": [rally_page, stage_page, team_page],
        }
    )

    if "id_rally" not in st.session_state:
        st.session_state["id_rally"] = 580

    if "id_team" not in st.session_state:
        st.session_state["id_team"] = 419

    if "id_stage" not in st.session_state:
        st.session_state["id_stage"] = 326

    pg.run()


if __name__ == "__main__":
    create_app()
