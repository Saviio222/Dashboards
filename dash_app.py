import pandas as pd
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Leitura dos dados
df = pd.read_csv('https://raw.githubusercontent.com/Saviio222/Dashboards/main/Base_de_Dados.csv')

# Remover o símbolo "R$" e as aspas duplas e converter 'Valor_Total_Venda' para float
df['Valor_Total_Venda'] = df['Valor_Total_Venda'].str.replace('R\\$', '', regex=True).str.replace('"', '').astype(float)

# Converter 'Data_Pedido' para datetime
df['Data_Pedido'] = pd.to_datetime(df['Data_Pedido'], format='%m-%d-%y')

# Inicialização do aplicativo Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
server = app.server

# Layout do aplicativo
app.layout = html.Div([
    html.H1('Dashboard de Vendas', className='text-center text-primary display-2 shadow'),
    
    html.Div([
        dcc.Graph(id='total-vendas-por-mes', figure={})
    ], className='row'),
    html.Div([
        dcc.Graph(id='total-vendas-por-representante', figure={})
    ], className='row'),
    html.Div([
        dcc.Graph(id='total-vendas-por-produto', figure={})
    ], className='row'),
    html.Div([
        dcc.Graph(id='total-vendas-por-regional', figure={})
    ], className='row'),
    html.Div([
        dcc.Graph(id='total-vendas-por-estado', figure={})
    ], className='row'),
    
    html.Div([
        html.Div([
            html.Label("Estado"),
            dcc.Dropdown(
                id='estado-dropdown',
                options=[{'label': estado, 'value': estado} for estado in df['Estado_Cliente'].unique()],
                value=df['Estado_Cliente'].unique()[0],
                multi=False
            ),
        ], className='six columns'),
        html.Div([
            html.Label("Cidade"),
            dcc.Dropdown(
                id='cidade-dropdown',
                multi=True
            ),
        ], className='six columns'),
    ], className='row'),
    
    html.Div([
        html.H1("Total de Vendas por Produto e Mês"),
        html.Label("Selecione o produto:"),
        dcc.Dropdown(
            id='dropdown-produto',
            options=[{'label': produto, 'value': produto} for produto in df['Nome_Produto'].unique()],
            value=df['Nome_Produto'].unique()[0]  # Valor padrão selecionado
        ),
        dcc.Graph(id='graph-vendas')
    ], className='row'),
    
    html.Div([
        html.Div([
            html.Label("Estado"),
            dcc.Dropdown(
                id='estado-dropdown2',
                options=[{'label': i, 'value': i} for i in df['Estado_Cliente'].unique()],
                value='SP'
            ),
        ], className='six columns'),
        html.Div([
            html.Label("Cidade"),
            dcc.Dropdown(
                id='cidade-dropdown2'
            ),
        ], className='six columns'),
    ], className='row'),
    
    html.Div([
        dcc.Graph(id='vendas-estado-cidade')
    ], className='row'),
], className='container-fluid')

# Callback para atualizar as opções do dropdown de cidades de acordo com o estado selecionado
@app.callback(
    Output('cidade-dropdown', 'options'),
    [Input('estado-dropdown', 'value')]
)
def update_cidades_dropdown(estado_selecionado):
    cidades = df[df['Estado_Cliente'] == estado_selecionado]['Cidade_Cliente'].unique()
    return [{'label': cidade, 'value': cidade} for cidade in cidades]

# Callbacks para atualizar os gráficos
@app.callback(
    Output('total-vendas-por-mes', 'figure'),
    Output('total-vendas-por-representante', 'figure'),
    Output('total-vendas-por-produto', 'figure'),
    Output('total-vendas-por-regional', 'figure'),
    Output('total-vendas-por-estado', 'figure'),
    Input('estado-dropdown', 'value'),
    Input('cidade-dropdown', 'value')
)
def update_graphs(estado_selecionado, cidade_selecionada):
    df_filtrado = df.copy()
    if cidade_selecionada:
        df_filtrado = df_filtrado[df_filtrado['Cidade_Cliente'].isin(cidade_selecionada)]

    fig_vendas_por_mes = px.line(df_filtrado.groupby(df_filtrado['Data_Pedido'].dt.month)['Valor_Total_Venda'].sum().reset_index(), x='Data_Pedido', y='Valor_Total_Venda', labels={'x':'Mês', 'y':'Total de Vendas'})
    fig_vendas_por_mes.update_layout(title='Total de Vendas por Mês')

    fig_vendas_por_representante = px.bar(df_filtrado, x='Nome_Representante', y='Valor_Total_Venda', labels={'x':'Representante', 'y':'Total de Vendas'})
    fig_vendas_por_representante.update_layout(title='Total de Vendas por Representante')

    fig_vendas_por_produto = go.Figure(data=[
        go.Table(
            header=dict(values=['Produto', 'Total de Vendas']),
            cells=dict(values=[df_filtrado['Nome_Produto'], df_filtrado['Valor_Total_Venda']])
        )
    ])
    fig_vendas_por_produto.update_layout(title='Total de Vendas por Produto')

    fig_vendas_por_regional = px.pie(df_filtrado, names='Regional', values='Valor_Total_Venda', labels={'names':'Regional', 'values':'Total de Vendas'})
    fig_vendas_por_regional.update_layout(title='Total de Vendas por Regional')

    fig_vendas_por_estado = px.bar(df_filtrado, x='Estado_Cliente', y='Valor_Total_Venda', labels={'x':'Estado', 'y':'Total de Vendas'})
    fig_vendas_por_estado.update_layout(title='Total de Vendas por Estado')

    return fig_vendas_por_mes, fig_vendas_por_representante, fig_vendas_por_produto, fig_vendas_por_regional, fig_vendas_por_estado

# Callback para atualizar as opções do dropdown de cidades de acordo com o estado selecionado
@app.callback(
    Output('cidade-dropdown2', 'options'),
    [Input('estado-dropdown2', 'value')]
)
def update_cidades_dropdown2(estado_selecionado):
    cidades = df[df['Estado_Cliente'] == estado_selecionado]['Cidade_Cliente'].unique()
    return [{'label': cidade, 'value': cidade} for cidade in cidades]

# Callback para atualizar o gráfico com base no estado e na cidade selecionados
@app.callback(
    Output('vendas-estado-cidade', 'figure'),
    [Input('estado-dropdown2', 'value'),
     Input('cidade-dropdown2', 'value')]
)
def update_graph(estado_selecionado, cidade_selecionada):
    print(f"Estado selecionado: {estado_selecionado}")
    print(f"Cidade selecionada: {cidade_selecionada}")
    
    # Filtrar o DataFrame com base no estado e na cidade selecionados
    df_filtrado = df[(df['Estado_Cliente'] == estado_selecionado) & (df['Cidade_Cliente'] == cidade_selecionada)]
    print(f"Número de linhas após a filtragem: {len(df_filtrado)}")
    
    # Cria o gráfico de barras com os dados filtrados
    fig = px.bar(df_filtrado, x='Data_Pedido', y='Valor_Total_Venda', labels={'x':'Data', 'y':'Total de Vendas'})
    
    return fig


# Callback para atualizar o gráfico de vendas por produto e mês
@app.callback(
    Output('graph-vendas', 'figure'),
    [Input('dropdown-produto', 'value')]
)
def update_graph(produto):
    # Filtrar o DataFrame para o produto selecionado
    df_produto = df[df['Nome_Produto'] == produto]
    
    # Criar uma tabela dinâmica para calcular o total de vendas por mês
    pivot_table = df_produto.pivot_table(index=df_produto['Data_Pedido'].dt.strftime('%B'), values='Valor_Total_Venda', aggfunc='sum').reset_index()
    
    # Plotar o gráfico de barras usando Plotly Express
    fig = px.bar(pivot_table, x='Data_Pedido', y='Valor_Total_Venda', title=f'Total de Vendas de {produto} por Mês', labels={'Valor_Total_Venda': 'Total de Vendas', 'Data_Pedido': 'Mês'})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8080, use_reloader=False)
