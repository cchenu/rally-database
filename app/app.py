import streamlit as st

home_page = st.Page("home.py", title = "Rally application", icon=":material/home:")
exercice_page = st.Page("exercice/exercice.py", title = "Exercice", icon = ":material/assignment:")
rally_page = st.Page("report/rally.py", title = "Rally", icon = ":material/directions_car:")
stage_page = st.Page("report/stage.py", title = "Stage", icon = ":material/map:")
contestant_page = st.Page("report/contestant.py", title = "Contestant", icon = ":material/person:")

st.set_page_config(layout = "wide")



pg = st.navigation(
    {
        "Hub": [home_page],
        "Assignment": [exercice_page],
        "Reports": [rally_page, stage_page, contestant_page]
    }
)

pg.run()