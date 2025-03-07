from dash import Dash, dcc, html, Input, Output
from pathlib import Path
import os
import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px


def convert_int(value):
    try:
        return int(value)
    except ValueError:
        return 0

def prepare_db(codigo_cidade):
    if os.path.exists('dados/dw.db'):
        return

    print("Criando o DB...")

    script = Path('scripts/create_db.sql').read_text()

    connection = sqlite3.connect('dados/dw.db')
    cursor = connection.cursor()
    cursor.executescript(script)

    print("Importando os dados das Rendas...")

    dados_renda_ibge = 'dados/PessoaRenda_BA.xlsx'
    df_renda = pd.read_excel(dados_renda_ibge)[['Cod_setor', 'V001', 'V002', 'V010', 'V020']]
    df_renda = df_renda[df_renda['Cod_setor'].astype(str).str.startswith(codigo_cidade)]
    df_renda.reset_index()

    for index, row in df_renda.iterrows():
        script = ("INSERT INTO censo_ibge_renda_pessoa (cod_setor, v001, v002, v010, v020)"
                  " VALUES('" + str(row['Cod_setor'])
                  + "','" + str(row['V001'])
                  + "','" + str(row['V002'])
                  + "','" + str(row['V010'])
                  + "','" + str(row['V020']) + "')")
        cursor.execute(script)
        connection.commit()

    print("Importando os dados dos Setores...")

    dados_setor_ibge = 'dados/Agregados_por_setores_basico_BR.xlsx'
    df_setor = pd.read_excel(dados_setor_ibge)[['CD_SETOR', 'SITUACAO', 'CD_SIT', 'CD_MUN', 'NM_MUN', 'CD_BAIRRO',
                                                'NM_BAIRRO']]
    df_setor = df_setor[df_setor['CD_SETOR'].astype(str).str.startswith(codigo_cidade)]
    df_setor.reset_index()

    for index, row in df_setor.iterrows():
        script = ("INSERT INTO censo_ibge_setores (cd_setor, situacao, cd_sit, cd_mun, nm_mun, cd_bairro, nm_bairro)"
                  " VALUES('" + str(row['CD_SETOR'])
                  + "','" + str(row['SITUACAO'])
                  + "','" + str(row['CD_SIT'])
                  + "','" + str(row['CD_MUN'])
                  + "','" + str(row['NM_MUN']).replace("'", " ")
                  + "','" + str(row['CD_BAIRRO'])
                  + "','" + str(row['NM_BAIRRO']).replace("'", " ") + "')")
        cursor.execute(script)
        connection.commit()

    print("Contruindo o DW...")

    script = Path('scripts/etl.sql').read_text()
    cursor.executescript(script)

    connection.commit()
    connection.close()

    print("DB Criado.")


def prepare_dataset(codigo_cidade):
    prepare_db(codigo_cidade)

    print("Preparando o DataSet...")

    sql = ("SELECT sf.id 'Setor',"
           "       zo.nome 'Zona',"
           "       mu.nome 'Municipio',"
           "       ba.nome 'Bairro',"
           "       sf.ate_meio_salario 'Ate Meio Salario',"
           "       sf.ate_um_salario 'Ate Um Salario',"
           "       sf.sem_salario 'Sem Renda',"
           "       sf.populacao 'Populacao'"
           "  FROM setor_fact sf"
           " INNER JOIN zona_dim zo"
           "    ON zo.id = sf.zona_id"
           " INNER JOIN municipio_dim mu"
           "    ON mu.id = sf.municipio_id"
           " INNER JOIN bairro_dim ba"
           "    ON ba.id = sf.bairro_id")

    connection = sqlite3.connect('dados/dw.db')
    df_resultado = pd.read_sql_query(sql, connection)

    print("DataSet pronto.")

    return df_resultado


def plot_graficos(dataset):
    app = Dash(__name__)

    app.layout = html.Div([
        html.H1('Ranking do Índice de Pobreza em Salvador/BA'),
        html.H4('Associação Núcleo de Educação Comunitária do Coroadinho – NEDUC'),
        html.P("Orientação do gráfico:"),
        dcc.Dropdown(
            id="dropdown",
            options=['Horizontal', 'Vertical'],
            value='Horizontal',
            clearable=False,
        ),
        dcc.Graph(id="graph"),
    ])

    @app.callback(Output("graph", "figure"),
                  Input("dropdown", "value"))
    def display(value):
        if value == "Vertical":
            orientation = 'v'
            x = 'Bairro'
            y = 'Indice de Pobreza'
        else:
            orientation = 'h'
            y = 'Bairro'
            x = 'Indice de Pobreza'
        fig = px.bar(dataset, x=x, y=y, color='Zona', orientation=orientation)
        fig.update_layout(xaxis_tickformat=".2%", yaxis_tickformat=".2%")
        return fig

    app.run_server(debug=True)


if __name__ == '__main__':
    # Configura o pandas
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.options.display.float_format = '{:.2f}'.format

    codigo_cidade = '2927408'  # Salvador

    # Prepara o dataset a partir dos dados do IBGE para a cidade de Salvador/BA
    df = prepare_dataset(codigo_cidade)

    # Calcula o índice de pobreza
    df['Indice de Pobreza'] = (df['Sem Renda'].astype(int) + df['Ate Meio Salario'].astype(int)) / df[
        'Populacao'].astype(int)

    # Cria ranking do índice de pobreza agrupado por bairro e zona
    df_ranking = (df.groupby(['Bairro', 'Zona']).agg({'Indice de Pobreza': np.mean})
                  .sort_values('Indice de Pobreza', ascending=True)).tail(20).reset_index()

    plot_graficos(df_ranking)

