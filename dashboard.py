import pandas as pd
import requests
import streamlit as st
from datetime import datetime # Importação necessária para garantir compatibilidade

dados = pd.read_csv('stratseg - clientes.csv')

st.set_page_config(layout= 'wide')
st.title('DASHBOARD DE CLIENTES - STRATSEG')

# Tratamento de datas
dados['Avisar Empresa'] = pd.to_datetime(dados['Avisar Empresa'], format = '%d/%m/%Y')
dados['Fim Apólice'] = pd.to_datetime(dados['Fim Apólice'], format = '%d/%m/%Y')

# --- NOVO BLOCO: Lógica para pegar o Mês Atual ---
hoje = pd.Timestamp.now()
data_inicio = hoje.replace(day=1) 
# O MonthEnd(0) joga para o último dia do mês atual
data_fim = hoje + pd.offsets.MonthEnd(0) 
# -----------------------------------------------

st.sidebar.title('Filtros')
with st.sidebar.expander('Empresa'):
    empresas = st.multiselect('Selecione as empresas', dados['Empresa'].unique(), dados['Empresa'].unique())
with st.sidebar.expander('Categoria do seguro'):
    categoria = st.multiselect('Selecione as categorias', dados['Seguro'].unique(), dados['Seguro'].unique())

with st.sidebar.expander('Data de contato'):
    # AQUI ESTÁ A MUDANÇA
    # O parâmetro 'value' define o valor inicial. Passamos uma tupla (inicio, fim)
    avisar_empresa = st.date_input(
        'Selecione a data', 
        value=(data_inicio.date(), data_fim.date()), 
        format="DD/MM/YYYY" # Formato brasileiro visual
    )

with st.sidebar.expander('Data de vencimento da apólice'):
    fim_apolice = st.date_input('Selecione a data', (dados['Fim Apólice'].min(), dados['Fim Apólice'].max()))

# Verificação de segurança antes do query
if len(avisar_empresa) == 2:
    start_date, end_date = avisar_empresa
    dados = dados.query('Empresa == @empresas & Seguro == @categoria & `Avisar Empresa` >= @start_date & `Avisar Empresa` <= @end_date & `Fim Apólice` >= @fim_apolice[0] & `Fim Apólice` <= @fim_apolice[1]')
else:
    st.warning("Por favor, selecione uma data final para o filtro de contato.")
    st.stop() # Para a execução até o usuário selecionar a data

dados = dados.query('Empresa == @empresas & Seguro == @categoria & `Avisar Empresa` >= @avisar_empresa[0] & `Avisar Empresa` <= @avisar_empresa[1] & `Fim Apólice` >= @fim_apolice[0] & `Fim Apólice` <= @fim_apolice[1]')

dados_agrupado = dados.groupby("Avisar Empresa")[["Empresa", 'Fim Apólice']].value_counts()
dados_agrupado = dados_agrupado.reset_index()

import plotly.express as px

dados_agrupado["Avisar Empresa"] = dados_agrupado['Avisar Empresa']
dados_agrupado['Apólices'] = dados_agrupado['count']
dados_agrupado['Fim Apólice'] = dados_agrupado['Fim Apólice'].dt.strftime('%d/%m/%Y')

fig = px.bar(
    dados_agrupado, 
    x="Avisar Empresa", 
    y="Apólices", 
    hover_data={'Avisar Empresa': '|%d/%m/%Y', 'Fim Apólice': True}, # Formata a data no hover
    color="Empresa", 
    color_discrete_sequence=px.colors.qualitative.T10, 
    labels={"Avisar Empresa": "Data de Aviso", "Apólices": "Número de Apólices"}, 
    title="Número de Apólices por Data de Aviso e Empresa"
)

# Forçar o eixo X a mostrar todos os dias (linear/date)
fig.update_xaxes(
    type='date',
    tickformat="%d/%m/%Y", # Formato visual no eixo
    tickfont=dict(size=14, color="#000000"),
    tickangle=-20,
    showgrid=True # Ajuda a visualizar os espaços vazios
)
fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",    # Cor de fundo
        font_size=16,       # Tamanho da letra
        font_family="Rockwell", # Tipo da fonte
        bordercolor="black" # Cor da borda
    )
)




aba1, aba2, aba3 = st.tabs(["Clientes para Contato", "Clientes que estão em negociação", "Visão Geral"])
with aba1:
    # 1. Identificando as empresas únicas e calculando a divisão
    empresas_unicas = dados_agrupado['Empresa'].unique()
    qtd_empresas = len(empresas_unicas)
    
    # O cálculo (qtd + 1) // 2 garante que se for ímpar (ex: 5), a col1 fica com 3 e col2 com 2.
    meio = (qtd_empresas + 1) // 2 
    
    lista_empresas_col1 = empresas_unicas[:meio]
    lista_empresas_col2 = empresas_unicas[meio:]

    col1, col2 = st.columns(2)

    # --- COLUNA 1 ---
    with col1:
        # Mantive sua métrica original, mas talvez você queira ajustar o texto
        st.metric(label='Total de Clientes', value=len(lista_empresas_col1) + len(lista_empresas_col2))
        
        st.write("---") # Uma linha separadora visual
        
        for empresa_atual in lista_empresas_col1:
            # Filtra apenas para pegar o total daquela empresa específica
            total_apolices = dados_agrupado[dados_agrupado['Empresa'] == empresa_atual]['count'].sum()
            
            # Usei markdown (**) para destacar o nome da empresa
            st.write(f'🏢 **{empresa_atual}**') 
            st.write(f'Apólices: {total_apolices}')
            st.write("") # Espaço vazio entre empresas

    # --- COLUNA 2 ---
    with col2:
        st.metric(label='Total de Apólices', value=dados_agrupado['count'].sum())
        
        st.write("---")
        
        for empresa_atual in lista_empresas_col2:
            total_apolices = dados_agrupado[dados_agrupado['Empresa'] == empresa_atual]['count'].sum()
            
            st.write(f'🏢 **{empresa_atual}**')
            st.write(f'Apólices: {total_apolices}')
            st.write("")

    # O gráfico continua aparecendo abaixo das colunas
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
