import pandas as pd
import plotly.graph_objects as go

PRI = 'PARTIDO REVOLUCIONARIO INSTITUCIONAL'
PAN = 'PARTIDO ACCIÓN NACIONAL'
PRD = 'PARTIDO DE LA REVOLUCIÓN DEMOCRÁTICA'
MC = 'MOVIMIENTO CIUDADANO'
PV = 'PARTIDO VERDE ECOLOGISTA DE MÉXICO'
PT = 'PARTIDO DEL TRABAJO'
PES = 'ENCUENTRO SOCIAL '
MORENA = 'MORENA'
PNA = 'NUEVA ALIANZA'

COAL_MORENA_2018 = 'JUNTOS HAREMOS HISTORIA'
COAL_MORENA_2018_PARTIES = 'JUNTOS HAREMOS HISTORIA (MORENA, PT, ENCUENTRO SOCIAL)'
COAL_PAN_2018 = 'POR MÉXICO AL FRENTE'
COAL_PAN_2018_PARTIES = 'POR MÉXICO AL FRENTE (PAN, PRD, MC)'
COAL_PRI_2018 = 'TODOS POR MÉXICO'
COAL_PRI_2018_PARTIES = 'TODOS POR MÉXICO (PRI, VERDE, NUEVA ALIANZA)'
COAL_PAN_PRI_2024 = 'FUERZA Y CORAZON POR MEXICO'
COAL_PAN_PRI_2024_PARTIES = 'FUERZA Y CORAZON POR MEXICO (PAN, PRI, PRD)'
COAL_MORENA_2024 = 'SIGAMOS HACIENDO HISTORIA'
COAL_MORENA_2024_PARTIES = 'SIGAMOS HACIENDO HISTORIA (MORENA, PT, VERDE)'

COL_NAME_PARTY_COALITION = 'PARTIDO_COALICION'
COL_NAME_CANDIDATE = 'NOMBRE_CANDIDATO'
COL_NAME_SORTED_CANDIDATE_NAME = 'NOMBRE_COMPLETO_ORDENADO'
COL_NAME_SOURCE_PARTY_COALITION = 'PARTIDO_COALICION_x'
COL_NAME_TARGET_PARTY_COALITION = 'PARTIDO_COALICION_y'
COL_NAME_SOURCE_CANDIDATE_NAME = 'NOMBRE_CANDIDATO_x'
COL_NAME_TARGET_CANDIDATE_NAME = 'NOMBRE_CANDIDATO_y'


COL_DISPLAY_NAME_SOURCE_PARTY_COALITION = 'Partido o Coalición 2018'
COL_DISPLAY_NAME_TARGET_PARTY_COALITION = 'Partido o Coalición 2024'


def has_common_elements(set1, set2):
    return len(set1.intersection(set2)) > 0


def join_with_spaces(x):
    return ' '.join(sorted(x.split()))


def load_candidates_data():
    df = pd.read_csv('candidaturas2024.csv')

    # join data from different sheets exported as csv
    df2018dmr = pd.read_csv('candidaturas2018DMR.csv')
    df2018drp = pd.read_csv('candidaturas2018DRP.csv')
    df2018smr = pd.read_csv('candidaturas2018SMR.csv')
    df2018srp = pd.read_csv('candidaturas2018SRP.csv')
    df2018p = pd.read_csv('candidaturas2018P.csv')
    df2018 = pd.concat([df2018dmr, df2018drp, df2018smr, df2018srp, df2018p])

    df2018.rename(columns={'NOMBRE_ASOCIACION': COL_NAME_PARTY_COALITION}, inplace=True)

    # join the two types of candidates in the 2018
    propietarios2018 = df2018[
        ['NOMBRE_PROPIETARIO', COL_NAME_PARTY_COALITION, 'TIPO_CANDIDATURA_PROP', 'ESTADO_ELECCION']]
    propietarios2018.rename(columns={
        'NOMBRE_PROPIETARIO': COL_NAME_CANDIDATE
    }, inplace=True)
    suplentes2018 = df2018[df2018['NOMBRE_SUP'].notna()][
        ['NOMBRE_SUP', COL_NAME_PARTY_COALITION, 'TIPO_CANDIDATURA_PROP', 'ESTADO_ELECCION']
    ]
    suplentes2018.rename(columns={
        'NOMBRE_SUP': COL_NAME_CANDIDATE
    }, inplace=True)

    candidates2018 = pd.concat([propietarios2018, suplentes2018])
    candidates2024 = df[[COL_NAME_CANDIDATE, COL_NAME_PARTY_COALITION, 'CARGO', 'ENTIDAD']]

    candidates2018.drop_duplicates(subset=[COL_NAME_CANDIDATE], keep='first', inplace=True)
    candidates2024.drop_duplicates(subset=[COL_NAME_CANDIDATE], keep='first', inplace=True)

    # Add list of political parties to the coalition name
    candidates2018.loc[
        candidates2018[COL_NAME_PARTY_COALITION] == COAL_MORENA_2018, [COL_NAME_PARTY_COALITION]
    ] = COAL_MORENA_2018_PARTIES
    candidates2018.loc[
        candidates2018[COL_NAME_PARTY_COALITION] == COAL_PAN_2018, [COL_NAME_PARTY_COALITION]
    ] = COAL_PAN_2018_PARTIES
    candidates2018.loc[
        candidates2018[COL_NAME_PARTY_COALITION] == COAL_PRI_2018, [COL_NAME_PARTY_COALITION]
    ] = COAL_PRI_2018_PARTIES
    candidates2024.loc[
        candidates2024[COL_NAME_PARTY_COALITION] == COAL_PAN_PRI_2024, [COL_NAME_PARTY_COALITION]
    ] = COAL_PAN_PRI_2024_PARTIES
    candidates2024.loc[
        candidates2024[COL_NAME_PARTY_COALITION] == COAL_MORENA_2024, [COL_NAME_PARTY_COALITION]
    ] = COAL_MORENA_2024_PARTIES

    # create unified name column, since names in data source are in different order (first, last vs last first)
    candidates2018[COL_NAME_SORTED_CANDIDATE_NAME] = (candidates2018[COL_NAME_CANDIDATE].apply(join_with_spaces))
    candidates2024[COL_NAME_SORTED_CANDIDATE_NAME] = (candidates2024[COL_NAME_CANDIDATE].apply(join_with_spaces))

    return candidates2018, candidates2024


def create_comparison_df(candidates_source, candidates_target):
    comparison_df = pd.merge(candidates_source, candidates_target, on=COL_NAME_SORTED_CANDIDATE_NAME, how='outer')
    comparison_df['matched'] = (
            comparison_df[COL_NAME_SOURCE_PARTY_COALITION] == comparison_df[COL_NAME_TARGET_PARTY_COALITION]
    )
    comparison_df['matched'].fillna(False, inplace=True)
    return comparison_df


def replace_column_values(df, column_name, old_value, new_value):
    df.loc[
        df[column_name] == old_value,
        [column_name]
    ] = new_value


def get_df_grouped_by_coalition(candidates_source, candidates_target):
    source_coalition_parties = [
        [MORENA, PT, PES],
        [PAN, PRD, MC],
        [PRI, PV, PNA]
    ]
    source_coalition_names = [COAL_MORENA_2018_PARTIES, COAL_PAN_2018_PARTIES, COAL_PRI_2018_PARTIES]

    for i, cp in enumerate(source_coalition_parties):
        for p in cp:
            replace_column_values(
                candidates_source,
                COL_NAME_PARTY_COALITION,
                p,
                source_coalition_names[i]
            )

    target_coalition_parties = [
        [PAN, PRI, PRD],
        [MORENA, PT, PV],
    ]
    target_coalition_names = [COAL_PAN_PRI_2024_PARTIES, COAL_MORENA_2024_PARTIES]

    for i, cp in enumerate(target_coalition_parties):
        for p in cp:
            replace_column_values(
                candidates_target,
                COL_NAME_PARTY_COALITION,
                p,
                target_coalition_names[i]
            )

    return candidates_source, candidates_target


def get_df_grouped_by_parties_in_coalition(candidates_source, candidates_target):
    source_coalition_parties = [
        [MORENA, PT, PES, COAL_MORENA_2018_PARTIES],
        [PAN, PRD, MC, COAL_PAN_2018_PARTIES],
        [PRI, PV, PNA, COAL_PRI_2018_PARTIES],
    ]
    source_coalition_names = [
        'MORENA,PT,PES',
        'PAN,PRD,MC',
        'PRI,PV,PNA'
    ]

    for i, cp in enumerate(source_coalition_parties):
        for p in cp:
            replace_column_values(
                candidates_source,
                COL_NAME_PARTY_COALITION,
                p,
                source_coalition_names[i]
            )

    target_coalition_parties = [
        [PAN, PRI, PRD, COAL_PAN_PRI_2024_PARTIES],
        [MORENA, PT, PV, COAL_MORENA_2024_PARTIES],
        [MC]
    ]
    target_coalition_names = [
        'PAN,PRI,PRD',
        'MORENA,PT,PES',
        'MC'
    ]

    for i, cp in enumerate(target_coalition_parties):
        for p in cp:
            replace_column_values(
                candidates_target,
                COL_NAME_PARTY_COALITION,
                p,
                target_coalition_names[i]
            )

    return candidates_source, candidates_target


def get_coalitions_changed(merged_df):
    coalitions_changed = {}

    for index, row in merged_df.iterrows():
        k = (row[COL_NAME_SOURCE_PARTY_COALITION], row[COL_NAME_TARGET_PARTY_COALITION])
        coalitions_changed[k] = coalitions_changed.get(k, 0) + 1

    return coalitions_changed


def get_coalitions_change_values(coalitions_changed):
    source_coalition = []
    target_coalition = []
    coalition_change_values = []
    for k, v in coalitions_changed.items():
        source_coalition.append(k[0] + ' 2018')
        target_coalition.append(k[1] + ' 2024')
        coalition_change_values.append(v)

    return {
        'source_coalition': source_coalition,
        'target_coalition': target_coalition,
        'coalition_change_values': coalition_change_values
    }


def get_coalition_indexes(coalitions_merged):
    coalition_indexes = {}
    i = 0
    for c in coalitions_merged:
        if c not in coalition_indexes:
            coalition_indexes[c] = i
            i += 1
    return coalition_indexes


def get_graph_data(merged_df):
    coalitions_changed = get_coalitions_changed(merged_df)

    coalitions_change_values = get_coalitions_change_values(coalitions_changed)
    source_coalition = coalitions_change_values['source_coalition']
    target_coalition = coalitions_change_values['target_coalition']
    coalitions_merged = source_coalition + target_coalition
    coalition_change_values = coalitions_change_values['coalition_change_values']

    coalition_indexes = get_coalition_indexes(coalitions_merged)

    coalition_source_indexes = [coalition_indexes[c] for c in source_coalition]
    coalition_target_indexes = [coalition_indexes[c] for c in target_coalition]

    return {
        'labels': list(coalition_indexes.keys()),
        'source_indexes': coalition_source_indexes,
        'target_indexes': coalition_target_indexes,
        'values': coalition_change_values
    }


def get_sankey_graph(labels, source_indexes, target_indexes, values, title):
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels,
                ),
                link=dict(
                    source=source_indexes,
                    target=target_indexes,
                    value=values,
                )
            )
        ]
    )

    fig.update_layout(title_text=title, font_size=10)
    return fig


def copy_df_for_display(df):
    dfc = df.copy()
    dfc.drop(['NOMBRE_CANDIDATO_x', COL_NAME_SORTED_CANDIDATE_NAME], axis=1, inplace=True)
    dfc.rename(
        columns={
            COL_NAME_TARGET_CANDIDATE_NAME: 'Candidato',
            COL_NAME_SOURCE_PARTY_COALITION: COL_DISPLAY_NAME_SOURCE_PARTY_COALITION,
            COL_NAME_TARGET_PARTY_COALITION: COL_DISPLAY_NAME_TARGET_PARTY_COALITION,
            'TIPO_CANDIDATURA_PROP': 'Cargo 2018',
            'ESTADO_ELECCION': 'Entidad 2018',
            'CARGO': 'Cargo 2024',
            'ENTIDAD': 'Entidad 2024',
        },
        inplace=True, errors='raise'
    )
    dfc = dfc[
        ['Candidato',
         COL_DISPLAY_NAME_SOURCE_PARTY_COALITION, COL_DISPLAY_NAME_TARGET_PARTY_COALITION,
         'Cargo 2018', 'Cargo 2024',
         'Entidad 2018', 'Entidad 2024']
    ]
    # dfc.reset_index(drop=True, inplace=True)

    return dfc


def get_migrated_to_morena(comparison_df):
    display_df = copy_df_for_display(comparison_df)
    migrated_to_morena = display_df[
        (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
        & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION].notna())
        & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION] != COAL_MORENA_2018_PARTIES)
        & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION] == COAL_MORENA_2024_PARTIES)
        ].reset_index(drop=True, inplace=False)
    migrated_to_morena.index += 1

    return migrated_to_morena


def get_migrated_to_mc(comparison_df):
    display_df = copy_df_for_display(comparison_df)
    migrated_to_mc = display_df[
        (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
        & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION].notna())
        & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION] != COAL_PAN_2018_PARTIES)
        & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION] == MC)
        ].reset_index()
    migrated_to_mc.index += 1

    return migrated_to_mc


def get_migrated_to_pan_pri(comparison_df):
    display_df = copy_df_for_display(comparison_df)
    migrated_to_pan_pri = display_df[
        (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION].notna())
        & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION].notna())
        & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION] != COAL_PRI_2018_PARTIES)
        & (display_df[COL_DISPLAY_NAME_SOURCE_PARTY_COALITION] != COAL_PAN_2018_PARTIES)
        & (display_df[COL_DISPLAY_NAME_TARGET_PARTY_COALITION] == COAL_PAN_PRI_2024_PARTIES)
        ].reset_index()
    migrated_to_pan_pri.index += 1

    return migrated_to_pan_pri
