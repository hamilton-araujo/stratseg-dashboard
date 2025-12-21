import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px

# --- CARREGAMENTO E TRATAMENTO ---
dados = pd.read_csv('stratseg - clientes.csv')
dados['Avisar Empresa'] = pd.to_datetime(dados['Avisar Empresa'], format='%d/%m/%Y')
dados['Fim Apólice'] = pd.to_datetime(dados['Fim Apólice'], format='%d/%m/%Y')

hoje = pd.Timestamp.now()
data_inicio = hoje.replace(day=1) 
data_fim = hoje + pd.offsets.MonthEnd(0) 

# --- SIDEBAR / FILTROS ---
st.sidebar.title('Filtros')
with st.sidebar.expander('Empresa'):
    empresas_selecionadas = st.multiselect('Selecione as empresas', dados['Empresa'].unique(), dados['Empresa'].unique())
with st.sidebar.expander('Categoria do seguro'):
    categoria = st.multiselect('Selecione as categorias', dados['Seguro'].unique(), dados['Seguro'].unique())
with st.sidebar.expander('Data de contato'):
    avisar_empresa = st.date_input('Selecione a data', value=(data_inicio.date(), data_fim.date()), format="DD/MM/YYYY")
with st.sidebar.expander('Data de vencimento da apólice'):
    fim_apolice = st.date_input('Selecione a data', (dados['Fim Apólice'].min(), dados['Fim Apólice'].max()))

# Aplicação dos Filtros
if len(avisar_empresa) == 2:
    start_date, end_date = avisar_empresa
    dados = dados.query('Empresa == @empresas_selecionadas & Seguro == @categoria & `Avisar Empresa` >= @start_date & `Avisar Empresa` <= @end_date & `Fim Apólice` >= @fim_apolice[0] & `Fim Apólice` <= @fim_apolice[1]')
else:
    st.stop()

# --- SINCRONIZAÇÃO DE CORES ---
# Definimos a paleta fixa para todas as empresas únicas do dataset original 
# para que a cor da empresa não mude se o filtro for alterado
cores_plotly = px.colors.qualitative.T10
empresas_unicas = sorted(empresas_selecionadas) # Ordenado para consistência
mapa_cores = {empresa: cores_plotly[i % len(cores_plotly)] for i, empresa in enumerate(empresas_unicas)}

# --- GRÁFICO ---
dados_agrupado = dados.groupby("Avisar Empresa")[["Empresa", 'Fim Apólice']].value_counts().reset_index()
dados_agrupado['Apólices'] = dados_agrupado['count']
dados_agrupado['Fim_Apolice_Formatada'] = dados_agrupado['Fim Apólice'].dt.strftime('%d/%m/%Y')

fig = px.bar(
    dados_agrupado, 
    x="Avisar Empresa", 
    y="Apólices", 
    color="Empresa", 
    color_discrete_map=mapa_cores, # AQUI ESTÁ A SINCRONIZAÇÃO
    labels={"Avisar Empresa": "Data de Aviso", "Apólices": "Nº de Apólices"}, 
    title="Número de Apólices por Data de Aviso e Empresa"
)

# Customizações de Hover e Layout (Mantidas as suas)
fig.update_traces(
    hovertemplate="<b>🏢 Empresa:</b> %{fullData.name}<br><b>📅 Data:</b> %{x|%d/%m/%Y}<br><b>📊 Qtd:</b> %{y}<extra></extra>",
    customdata=dados_agrupado[['Fim_Apolice_Formatada']]
)
fig.update_xaxes(type='date', tickformat="%d/%m/%Y")

# --- INTERFACE ABA 1 ---
st.set_page_config(layout='wide')
st.title('DASHBOARD DE CLIENTES - STRATSEG')
aba1, aba2, aba3 = st.tabs(["Clientes para Contato", "Em negociação", "Visão Geral"])

with aba1:
    col1, col2 = st.columns(2)
    meio = (len(empresas_unicas) + 1) // 2 
    
    def renderizar_lista_empresas(lista):
        for empresa_atual in lista:
            cor = mapa_cores[empresa_atual] # Usa a mesma cor mapeada para o gráfico
            df_detalhe = dados[dados['Empresa'] == empresa_atual].copy()
            
            st.markdown(f"""
                <div style="border-left: 5px solid {cor}; padding-left: 15px; margin-top: 20px;">
                    <span style="color: {cor}; font-size: 20px; font-weight: bold;">🏢 {empresa_atual}</span>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Ver {len(df_detalhe)} apólice(s)"):
                st.dataframe(df_detalhe[['Apólice', 'Seguro', 'Fim Apólice']], hide_index=True, use_container_width=True)

    with col1:
        st.metric('Total de Clientes', len(empresas_unicas))
        renderizar_lista_empresas(empresas_unicas[:meio])
    with col2:
        st.metric('Total de Apólices', len(dados))
        renderizar_lista_empresas(empresas_unicas[meio:])

    st.plotly_chart(fig, use_container_width=True)

# (Abas 2 e 3 seguem o seu código original...)

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
