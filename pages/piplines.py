import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px

# Carregamento dos dados
piplines = pd.read_csv('pages/bids_esquentar.csv')

st.set_page_config(layout= 'wide')
st.title('DASHBOARD DE PIPLINES - STRATSEG')

st.write("### Filtros")
busca_empresa = st.text_input('Pesquisar por Nome da Empresa', '')

# Só executa a lógica se houver algo digitado na busca
if busca_empresa:
    # 1. Filtra as linhas pelo nome da empresa
    df_filtrado = piplines[piplines['Nome da Empresa'].str.contains(busca_empresa, case=False, na=False)]

    # 2. Remove colunas onde TODOS os valores são nulos (NaN) para o resultado atual
    # Se quiser remover colunas que tenham QUALQUER nulo, use how='any'
    df_exibicao = df_filtrado.dropna(axis=1, how='all')

    st.write(f"Resultados para: **{busca_empresa}**")
    
    with st.expander('Personalizar Colunas'):
        colunas_disponiveis = list(df_exibicao.columns)
        colunas_selecionadas = st.multiselect('Selecione as colunas', colunas_disponiveis, colunas_disponiveis)

    # Exibindo o dataframe apenas com dados relevantes
    st.dataframe(df_exibicao[colunas_selecionadas], use_container_width=True)
else:
    # Mensagem amigável enquanto o usuário não pesquisa
    st.info("Digite o nome de uma empresa na barra de pesquisa acima para visualizar os dados.")