import streamlit as st
from helpers import *
from display_messages import *

# Page Config
st.set_page_config(page_title=PAGE_TITLE)

# Data Load
candidates2018, candidates2024 = load_candidates_data()
comparison_df_parties_coalitions = create_comparison_df(candidates2018.copy(), candidates2024.copy())

# Header
st.title(PAGE_HEADER)

st.markdown(INTRO_MESSAGE)

# Only Coalitions Graph
st.header(GROUPED_GRAPH_HEADER)
st.write(GROUPED_GRAPH_DESCRIPTION)

candidates2018_by_coalition, candidates2024_by_coalition = get_df_grouped_by_coalition(candidates2018.copy(),
                                                                                       candidates2024.copy())
comparison_df_only_coalitions = create_comparison_df(candidates2018_by_coalition, candidates2024_by_coalition)
graph_data = get_graph_data(
    comparison_df_only_coalitions.dropna(subset=[COL_NAME_SOURCE_CANDIDATE_NAME, COL_NAME_TARGET_CANDIDATE_NAME])
)
graph2 = get_sankey_graph(
    graph_data['labels'],
    graph_data['source_indexes'],
    graph_data['target_indexes'],
    graph_data['values'],
    ""
)
st.plotly_chart(graph2)

# Migrated Candidates Table Data Preparation
migrated_to_morena = get_migrated_to_morena(comparison_df_only_coalitions)
migrated_to_mc = get_migrated_to_mc(comparison_df_only_coalitions)
migrated_to_pan_pri = get_migrated_to_pan_pri(comparison_df_only_coalitions)

# DF preparation for non migrated
candidates2018_by_parties_in_coalition, candidates2024_by_parties_in_coalition = (
    get_df_grouped_by_parties_in_coalition(
        candidates2018.copy(), candidates2024.copy()
    ))

candidates2018_by_parties_in_coalition[COL_NAME_PARTY_COALITION] = (
    candidates2018_by_parties_in_coalition[COL_NAME_PARTY_COALITION]
    .apply(lambda x: set(x.split(','))))

candidates2024_by_parties_in_coalition[COL_NAME_PARTY_COALITION] = (
    candidates2024_by_parties_in_coalition[COL_NAME_PARTY_COALITION]
    .apply(lambda x: set(x.split(','))))

comparison_by_parties_in_coalition = create_comparison_df(
    candidates2018_by_parties_in_coalition, candidates2024_by_parties_in_coalition
)
comparison_by_parties_in_coalition.dropna(
    subset=[COL_NAME_SOURCE_PARTY_COALITION, COL_NAME_TARGET_PARTY_COALITION],
    inplace=True
)

comparison_by_parties_in_coalition['matched'] = (
    comparison_by_parties_in_coalition.apply(
        lambda row: has_common_elements(
            row[COL_NAME_SOURCE_PARTY_COALITION],
            row[COL_NAME_TARGET_PARTY_COALITION]
        ),
        axis=1
    )
)

comparison_by_parties_in_coalition = comparison_by_parties_in_coalition[
    comparison_by_parties_in_coalition['matched']
]

# Migrated to MORENA
st.subheader(f'{len(migrated_to_morena)} candidatos cambiaron a coalición MORENA, PT, VERDE')
st.dataframe(migrated_to_morena)

# Migrated to MC
st.subheader(f'{len(migrated_to_mc)} candidatos cambiaron a MC')
st.dataframe(migrated_to_mc)

# Migrated to PRI PAN
st.subheader(f'{len(migrated_to_pan_pri)} candidatos cambiaron a coalición PAN, PRI, PRD')
st.dataframe(migrated_to_pan_pri)

# Non migrated
st.subheader(f'{len(comparison_by_parties_in_coalition)} candidatos no cambiaron a un partido de otra coalición')
st.dataframe(
    copy_df_for_display(comparison_by_parties_in_coalition).reset_index(drop=True)
)

# Candidate count
candidates_count_2018 = len(candidates2018_by_coalition)
candidates_count_2024 = len(candidates2024_by_coalition)
repeated_candidates_count = len(
    comparison_df_only_coalitions.dropna(
        subset=[COL_NAME_SOURCE_PARTY_COALITION, COL_NAME_TARGET_PARTY_COALITION]
    )
)
non_migrated_count = len(comparison_by_parties_in_coalition)
non_migrated_percent = (non_migrated_count / repeated_candidates_count) * 100
migrated_count = repeated_candidates_count - non_migrated_count
migrated_percent = (migrated_count / repeated_candidates_count) * 100

st.subheader(CANDIDATES_COUNT_SUBHEADER)
st.write(f'{candidates_count_2018:,} candidaturas en 2018')
st.write(f'{candidates_count_2024:,} candidaturas 2024')
st.write(f'{repeated_candidates_count} candidatos de 2018 vuelven a postularse por un cargo federal en 2024')
st.write(
    f'{non_migrated_count} candidatos ({non_migrated_percent:.2f}%) que vuelven a postularse se mantuvieron en partidos de su coalición'
)
st.info(
    f'{migrated_count} candidatos ({migrated_percent:.2f}%) que vuelven a postularse cambiaron a un partido de otra coalición'
)

# Party & Coalition Graph
st.header(MAIN_GRAPH_HEADER)
st.markdown(MAIN_GRAPH_MESSAGE)

graph_data = get_graph_data(
    comparison_df_parties_coalitions.dropna(
        subset=[COL_NAME_SOURCE_PARTY_COALITION, COL_NAME_TARGET_PARTY_COALITION]
    )
)
graph = get_sankey_graph(
    graph_data['labels'],
    graph_data['source_indexes'],
    graph_data['target_indexes'],
    graph_data['values'],
    ""
)
st.plotly_chart(graph)

# Footer

st.markdown(AUTHOR_MESSAGE)
st.markdown(DATA_SOURCE)
