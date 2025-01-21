!pip install dash
!pip install mapclassify
!pip install gdown
import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd
import altair as alt
import geopandas as gpd
from datetime import datetime
import gdown

# Definindo o ID do arquivo
file_id = '1abpoLbYvccx9-0g9lJ0BLiK-AMqKdP12'
url = f'https://drive.google.com/uc?export=download&id={file_id}'

# Baixando o arquivo
gdown.download(url, '/content/BD_Atlas_1991_2023_v1.0_2024.04.29.xlsx', quiet=False)

# Lendo o arquivo
desastre = pd.read_excel('/content/BD_Atlas_1991_2023_v1.0_2024.04.29.xlsx')

#limpando ano
desastre['ano evento'] = pd.to_datetime(desastre['Data_Evento']).dt.year

def agrupando_municipio(df, colunas):

    # Agrupar por 'ano evento' e somar as colunas especificadas
    df_agrupado = df.groupby(['ano evento', 'Nome_Municipio', 'Sigla_UF'])[colunas].sum().reset_index()

    return df_agrupado

colunas = ['DH_total_danos_humanos', 'DH_MORTOS', 'DH_ENFERMOS', 'DH_DESALOJADOS', 'DH_DESAPARECIDOS', 'DH_DESABRIGADOS', 'DH_OUTROS AFETADOS']

municipios = agrupando_municipio(desastre, colunas)

desastre_municipio_ano = desastre.groupby(['ano evento', 'Nome_Municipio', 'Sigla_UF'])['Protocolo_S2iD'].count().reset_index()
desastre_municipio_ano_afetados = pd.merge(desastre_municipio_ano, municipios, how = 'inner', on = ['ano evento', 'Nome_Municipio', 'Sigla_UF'])
desastre_municipio_ano_afetados

# Inicializando o app Dash
app = dash.Dash(__name__)

# Definindo configurações para o gráfico
GRAPH_WIDTH = 1000
GRAPH_HEIGHT = 800
PLOT_BG_COLOR = "white"
FONT = dict(family="Arial", size=10, color="rgb(82, 82, 82)")
SOURCE_TEXT = "Fonte: Instituto de Pesquisa Ambiental (IPAM) | Atlas dos Desastres"

# Layout do app
app.layout = html.Div([
    html.H1("Evolução de desastres por município (1991-2023)"),
    dcc.Input(
        id='municipio-search',
        type='text',
        placeholder='Pesquise por município...',
        debounce=True,  # Pesquisa somente após o usuário parar de digitar
        style={'margin-bottom': '20px', 'width': '50%'}
    ),
    dcc.Graph(id='line-plot')  # Gráfico inicial vazio
])

# Callback para atualizar o gráfico com base na pesquisa
@app.callback(
    Output('line-plot', 'figure'),
    [Input('municipio-search', 'value')]
)
def update_graph(search_value):
    # Usar todos os dados se a pesquisa for vazia ou None
    filtered_data = desastre_municipio_ano_afetados
    if search_value:
        filtered_data = filtered_data[filtered_data['Nome_Municipio'].str.contains(search_value, case=False, na=False)]

    # Verificar se os dados filtrados estão vazios
    if filtered_data.empty:
        return go.Figure(layout={"title": f"Nenhum dado encontrado para '{search_value}'"})

    # Criar o gráfico
    fig = px.line(
        filtered_data,
        x="ano evento",
        y="Protocolo_S2iD",
        color='Nome_Municipio',
        labels={'ano evento': 'Ano', 'Protocolo_S2iD': 'Quantidade de desastres'},
        hover_name="Nome_Municipio",
        log_x=False
    )

    # Atualizar layout com configurações globais
    fig.update_layout(
        width=GRAPH_WIDTH,
        height=GRAPH_HEIGHT,
        plot_bgcolor=PLOT_BG_COLOR,
        xaxis=dict(title=None),
        yaxis=dict(title=None, tickangle=0),
        annotations=[
            dict(
                x=0.5,
                y=-0.2,
                xref="paper",
                yref="paper",
                text=SOURCE_TEXT,
                showarrow=False,
                font=FONT,
                align="center"
            )
        ]
    )

    return fig

# Executando o app
if __name__ == '__main__':
    app.run_server(debug=True)
