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
st.markdown(AUTHOR_MESSAGE)
st.markdown(DATA_SOURCE)
with st.expander('Ver instrucciones'):
    st.markdown(USAGE_NOTES)
st.divider()

# Party & Coalition Graph
st.header(MAIN_GRAPH_HEADER)
st.markdown(MAIN_GRAPH_MESSAGE)

graph_data = get_graph_data(
    comparison_df_parties_coalitions.dropna(subset=['NOMBRE_CANDIDATO_x', 'NOMBRE_CANDIDATO_y'])
)
graph = get_sankey_graph(
    graph_data['labels'],
    graph_data['source_indexes'],
    graph_data['target_indexes'],
    graph_data['values'],
    ""
)
st.plotly_chart(graph)

# Only Coalitions Graph
st.header(GROUPED_GRAPH_HEADER)
st.write(GROUPED_GRAPH_DESCRIPTION)

candidates2018_by_coalition, candidates2024_by_coalition = get_df_grouped_by_coalition(candidates2018.copy(),
                                                                                       candidates2024.copy())
comparison_df_only_coalitions = create_comparison_df(candidates2018_by_coalition, candidates2024_by_coalition)
graph_data = get_graph_data(
    comparison_df_only_coalitions.dropna(subset=['NOMBRE_CANDIDATO_x', 'NOMBRE_CANDIDATO_y'])
)
graph2 = get_sankey_graph(
    graph_data['labels'],
    graph_data['source_indexes'],
    graph_data['target_indexes'],
    graph_data['values'],
    ""
)
st.plotly_chart(graph2)
st.divider()

# Migrated Candidates Table Data Preparation
display_df = copy_df_for_display(comparison_df_only_coalitions)

# Migrated to MORENA

morena_migrated = display_df[
    (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
    & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
    & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION] != COAL_MORENA_2018_PARTIES)
    & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION] == COAL_MORENA_2024_PARTIES)
    ].reset_index(drop=True, inplace=False)
morena_migrated.index += 1

st.subheader(f'{len(morena_migrated)} candidatos cambiaron a coalición MORENA, PT, VERDE')
st.dataframe(morena_migrated)

# MIGRATED TO MC

mc_migrated = display_df[
    (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
    & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
    & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION] != COAL_PAN_2018_PARTIES)
    & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION] == MC)
    ].reset_index()
mc_migrated.index += 1

st.subheader(f'{len(mc_migrated)} candidatos cambiaron a MC')
st.dataframe(mc_migrated)

# MIGRATED TO PRI PAN

pri_pan_migrated = display_df[
    (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
    & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
    # & (display_df['Tipo Candidatura'] != 'No Postulado')
    & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION] != COAL_PRI_2018_PARTIES)
    & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION] != COAL_PAN_2018_PARTIES)
    & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION] == COAL_PAN_PRI_2024_PARTIES)
    ].reset_index()
pri_pan_migrated.index += 1

st.subheader(f'{len(pri_pan_migrated)} candidatos cambiaron a coalición PAN, PRI, PRD')
st.dataframe(pri_pan_migrated)

# DF preparation for non migrated
candidates2018_by_parties_in_coalition, candidates2024_by_parties_in_coalition = (
    get_df_grouped_by_parties_in_coalition(
        candidates2018.copy(), candidates2024.copy()
    ))


candidates2018_by_parties_in_coalition['PARTIDO_COALICION'] = (
    candidates2018_by_parties_in_coalition['PARTIDO_COALICION']
    .apply(lambda x: set(x.split(','))))

candidates2024_by_parties_in_coalition['PARTIDO_COALICION'] = (
    candidates2024_by_parties_in_coalition['PARTIDO_COALICION']
    .apply(lambda x: set(x.split(','))))

comparison_by_parties_in_coalition = create_comparison_df(
    candidates2018_by_parties_in_coalition, candidates2024_by_parties_in_coalition
)
comparison_by_parties_in_coalition.dropna(subset=['PARTIDO_COALICION_x', 'PARTIDO_COALICION_y'], inplace=True)

comparison_by_parties_in_coalition['matched'] = (
    comparison_by_parties_in_coalition.apply(
        lambda row: has_common_elements(
            row['PARTIDO_COALICION_x'], row['PARTIDO_COALICION_y']
        ), axis=1
    )
)

comparison_by_parties_in_coalition = comparison_by_parties_in_coalition[
    comparison_by_parties_in_coalition['matched']
]

st.subheader(f'{len(comparison_by_parties_in_coalition)} candidatos no cambiaron de coalición')
st.dataframe(
    copy_df_for_display(comparison_by_parties_in_coalition).reset_index(drop=True)
)
