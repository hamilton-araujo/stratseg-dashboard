import pandas as pd
import streamlit as st

# Carregamento dos dados
# Usamos o dicionário para facilitar a iteração depois
dfs = pd.read_excel('pages/Bases BIDS a esquentar - Copia.xlsx', sheet_name=None)

# Mapeamento amigável dos nomes das abas
mapeamento_nomes = {
    'Bids WTW 19 e 20': 'Bids WTW 19 e 20',
    'BD Geral WTW': 'BD Geral WTW',
    'Contatos WTW': 'Contatos WTW',
    'Mailling Geral WTW': 'Mailling Geral WTW',
    'CRM RJ 20': 'CRM RJ 20',
    'CRM SP 20': 'CRM SP 20',
    'Conta Loc 24': 'Conta Loc 24',
    'Contact Loc 24': 'Contact Loc 24',
    'IT SEG': 'IT SEG',
    'ITSEG especifico': 'ITSEG especifico',
    'Oportunidad LOC 24': 'Oportunidad LOC 24'
}

st.set_page_config(layout='wide')
st.title('DASHBOARD DE PIPELINES - STRATSEG')

st.write("### Filtros")
busca_empresa = st.text_input('Pesquisar por Nome da Empresa', '')

# Só executa se houver texto na busca
if busca_empresa:
    st.write(f"Resultados para: **{busca_empresa}**")
    houve_resultado = False

    # Iterar sobre cada aba do Excel
    for nome_aba, df in dfs.items():
        # Verificamos se a coluna 'Nome da Empresa' existe nesta aba específica
        if 'Nome da Empresa' in df.columns:
            # Filtra as linhas
            df_filtrado = df[df['Nome da Empresa'].astype(str).str.contains(busca_empresa, case=False, na=False)]
            
            # Só exibe se o DataFrame resultante NÃO estiver vazio
            if not df_filtrado.empty:
                houve_resultado = True
                
                # Remove colunas que estão totalmente vazias para este resultado
                df_exibicao = df_filtrado.dropna(axis=1, how='all')
                
                st.subheader(f"Tabela: {nome_aba}")
                
                # Expander opcional para cada tabela para não poluir a tela
                with st.expander(f"Ver detalhes de {nome_aba} ({len(df_exibicao)} resultados)"):
                    colunas_disponiveis = list(df_exibicao.columns)
                    colunas_selecionadas = st.multiselect(
                        f'Colunas em {nome_aba}', 
                        colunas_disponiveis, 
                        colunas_disponiveis,
                        key=f"sel_{nome_aba}" # Chave única para o multiselect não conflitar
                    )
                    
                    st.dataframe(df_exibicao[colunas_selecionadas], use_container_width=True)
                st.divider()

    if not houve_resultado:
        st.warning(f"Nenhum registro encontrado para '{busca_empresa}' em nenhuma das bases.")

else:
    st.info("Digite o nome de uma empresa na barra de pesquisa acima para visualizar os dados consolidados.")