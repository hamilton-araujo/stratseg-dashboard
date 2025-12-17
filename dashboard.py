import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px

dados = pd.read_csv('stratseg - clientes.csv')

st.set_page_config(layout= 'wide')
st.title('DASHBOARD DE CLIENTES - STRATSEG')

# Tratamento de datas
dados['Avisar Empresa'] = pd.to_datetime(dados['Avisar Empresa'], format = '%d/%m/%Y')
dados['Fim Apólice'] = pd.to_datetime(dados['Fim Apólice'], format = '%d/%m/%Y')

hoje = pd.Timestamp.now()
data_inicio = hoje.replace(day=1) 
data_fim = hoje + pd.offsets.MonthEnd(0) 

st.sidebar.title('Filtros')
with st.sidebar.expander('Empresa'):
    empresas = st.multiselect('Selecione as empresas', dados['Empresa'].unique(), dados['Empresa'].unique())
with st.sidebar.expander('Categoria do seguro'):
    categoria = st.multiselect('Selecione as categorias', dados['Seguro'].unique(), dados['Seguro'].unique())

with st.sidebar.expander('Data de contato'):
    avisar_empresa = st.date_input(
        'Selecione a data', 
        value=(data_inicio.date(), data_fim.date()), 
        format="DD/MM/YYYY"
    )

with st.sidebar.expander('Data de vencimento da apólice'):
    fim_apolice = st.date_input('Selecione a data', (dados['Fim Apólice'].min(), dados['Fim Apólice'].max()))

if len(avisar_empresa) == 2:
    start_date, end_date = avisar_empresa
    dados = dados.query('Empresa == @empresas & Seguro == @categoria & `Avisar Empresa` >= @start_date & `Avisar Empresa` <= @end_date & `Fim Apólice` >= @fim_apolice[0] & `Fim Apólice` <= @fim_apolice[1]')
else:
    st.warning("Por favor, selecione uma data final para o filtro de contato.")
    st.stop()

# Agrupamento
dados_agrupado = dados.groupby("Avisar Empresa")[["Empresa", 'Fim Apólice']].value_counts().reset_index()
dados_agrupado['Apólices'] = dados_agrupado['count']
# Formatamos a data de fim apenas para exibição no hover
dados_agrupado['Fim_Apolice_Formatada'] = dados_agrupado['Fim Apólice'].dt.strftime('%d/%m/%Y')
# A data de aviso deve ser formatada no template do Plotly para não quebrar o eixo X temporal

# --- CONFIGURAÇÃO DO GRÁFICO ---
fig = px.bar(
    dados_agrupado, 
    x="Avisar Empresa", 
    y="Apólices", 
    color="Empresa", 
    color_discrete_sequence=px.colors.qualitative.T10, 
    labels={"Avisar Empresa": "Data de Aviso", "Apólices": "Nº de Apólices"}, 
    title="Número de Apólices por Data de Aviso e Empresa"
)

# Customização do HOVER (Template HTML para ficar maior e mais bonito)
fig.update_traces(
    hovertemplate="<br>".join([
        "<b>🏢 Empresa:</b> %{fullData.name}",
        "<b>📅 Data de Aviso:</b> %{x|%d/%m/%Y}",
        "<b>📊 Quantidade:</b> %{y}",
        "<b>⌛ Vencimento:</b> %{customdata[0]}",
        "<extra></extra>" # Remove a label secundária chata do plotly
    ]),
    customdata=dados_agrupado[['Fim_Apolice_Formatada']]
)

fig.update_xaxes(
    type='date',
    tickformat="%d/%m/%Y",
    tickfont=dict(size=14, color="#000000"),
    tickangle=-20,
    showgrid=True
)

fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16, # Tamanho da fonte maior
        font_family="Arial",
        font_color="black",
        bordercolor="black",
        namelength=-1 # Garante que o nome da empresa não seja cortado
    ),
    # Adiciona um padding (margem interna) para o hover parecer maior e mais "respirável"
    margin=dict(l=20, r=20, t=50, b=20) 
)

# --- INTERFACE STREAMLIT ---
aba1, aba2, aba3 = st.tabs(["Clientes para Contato", "Clientes que estão em negociação", "Visão Geral"])

with aba1:
    empresas_unicas = dados_agrupado['Empresa'].unique()
    qtd_empresas = len(empresas_unicas)
    meio = (qtd_empresas + 1) // 2 
    lista_empresas_col1 = empresas_unicas[:meio]
    lista_empresas_col2 = empresas_unicas[meio:]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label='Total de Clientes', value=len(lista_empresas_col1) + len(lista_empresas_col2))
        st.write("---")
        for empresa_atual in lista_empresas_col1:
            total_apolices = dados_agrupado[dados_agrupado['Empresa'] == empresa_atual]['count'].sum()
            st.write(f'🏢 **{empresa_atual}**') 
            st.write(f'Apólices: {total_apolices}')
            st.write("") 

    with col2:
        st.metric(label='Total de Apólices', value=dados_agrupado['count'].sum())
        st.write("---")
        for empresa_atual in lista_empresas_col2:
            total_apolices = dados_agrupado[dados_agrupado['Empresa'] == empresa_atual]['count'].sum()
            st.write(f'🏢 **{empresa_atual}**')
            st.write(f'Apólices: {total_apolices}')
            st.write("")

    st.markdown("---")
    st.plotly_chart(fig, use_container_width=True)


with aba2:
    st.write("Clientes que estão em negociação")
    col1, col2, col3 = st.columns([1.5, 1, 1]) # Larguras relativas: 1, 2, 1

    with col2:
        st.metric(label='Cliente', value = 'CIMED')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label='Apólice', value='9600131570 (Endosso nº 123990)')
        st.metric(label='Matriz de Riscos', value='Link')
        st.metric(label='Contato', value='João Silva - (41) 99999-9999')
    with col2:
        st.metric(label='Tipo de Seguro', value='Seguro Empresarial')
        st.metric(label='Etapa do processo de apresentação', value='Montando PowerPoint')
        st.metric(label='Etapa do processo de negociação', value='Aguardando retorno do cliente')
    with col3:
        st.metric(label='Data de Aviso', value='15/09/2024')
        st.metric(label='Apresentação', value='Link')
        st.metric(label='Corretora Atual', value='WILLIS CORRETORES DE SEGUROS LTDA')

with aba3:
    st.write("Visão Geral dos Clientes")
    with st.expander('Colunas'):
        colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

    st.dataframe(dados[colunas], use_container_width=True)
