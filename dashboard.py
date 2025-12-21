import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px

# 1. Configuração de Página (Deve ser o primeiro comando)
st.set_page_config(layout='wide', page_title="Dashboard Stratseg")

# 2. Carregamento e Tratamento
dados = pd.read_csv('stratseg - clientes.csv')
dados['Avisar Empresa'] = pd.to_datetime(dados['Avisar Empresa'], format='%d/%m/%Y')
dados['Fim Apólice'] = pd.to_datetime(dados['Fim Apólice'], format='%d/%m/%Y')

# Lógica para filtro inicial de Dezembro (Mês Atual)
hoje = pd.Timestamp.now()
data_inicio_mes = hoje.replace(day=1).date()
data_fim_mes = (hoje + pd.offsets.MonthEnd(0)).date()

st.title('DASHBOARD DE CLIENTES - STRATSEG')

# 3. Sidebar com Filtros
st.sidebar.title('Filtros')
with st.sidebar.expander('Empresa'):
    empresas_opcoes = sorted(dados['Empresa'].unique())
    empresas_selecionadas = st.multiselect('Selecione as empresas', empresas_opcoes, empresas_opcoes)

with st.sidebar.expander('Categoria do seguro'):
    categorias_opcoes = sorted(dados['Seguro'].unique())
    categoria = st.multiselect('Selecione as categorias', categorias_opcoes, categorias_opcoes)

with st.sidebar.expander('Data de contato'):
    avisar_empresa = st.date_input(
        'Selecione a data', 
        value=(data_inicio_mes, data_fim_mes), 
        format="DD/MM/YYYY"
    )

with st.sidebar.expander('Data de vencimento da apólice'):
    fim_apolice = st.date_input('Selecione a data', (dados['Fim Apólice'].min(), dados['Fim Apólice'].max()))

# 4. Aplicação do Filtro
if len(avisar_empresa) == 2:
    start_date, end_date = avisar_empresa
    df_filtrado = dados.query(
        'Empresa == @empresas_selecionadas & '
        'Seguro == @categoria & '
        '`Avisar Empresa` >= @start_date & `Avisar Empresa` <= @end_date & '
        '`Fim Apólice` >= @fim_apolice[0] & `Fim Apólice` <= @fim_apolice[1]'
    ).copy()
else:
    st.warning("Por favor, selecione o intervalo completo (Data Inicial e Final).")
    st.stop()

# 5. Sincronização de Cores Individuais
# Criamos um mapa de cores fixo para TODAS as empresas do arquivo original
cores_paleta = px.colors.qualitative.Alphabet + px.colors.qualitative.Dark24
todas_empresas = sorted(dados['Empresa'].unique())
mapa_cores = {empresa: cores_paleta[i % len(cores_paleta)] for i, empresa in enumerate(todas_empresas)}

# 6. Preparação do Gráfico
dados_agrupado = df_filtrado.groupby(["Avisar Empresa", "Empresa", "Fim Apólice"]).size().reset_index(name='Apólices')
dados_agrupado['Fim_Apolice_Formatada'] = dados_agrupado['Fim Apólice'].dt.strftime('%d/%m/%Y')

fig = px.bar(
    dados_agrupado, 
    x="Avisar Empresa", 
    y="Apólices", 
    color="Empresa", 
    color_discrete_map=mapa_cores, # Sincronização aqui
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


# 7. Interface de Abas
aba1, aba2, aba3 = st.tabs(["Clientes para Contato", "Clientes que estão em negociação", "Visão Geral"])

with aba1:
    col1, col2 = st.columns(2)
    empresas_no_filtro = sorted(df_filtrado['Empresa'].unique())
    meio = (len(empresas_no_filtro) + 1) // 2 

    def renderizar_lista(lista_empresas):
        for emp in lista_empresas:
            cor = mapa_cores[emp]
            df_detalhe = df_filtrado[df_filtrado['Empresa'] == emp]
            
            st.markdown(f"""
                <div style="border-left: 5px solid {cor}; padding-left: 15px; margin-top: 20px; margin-bottom: 5px;">
                    <span style="color: {cor}; font-size: 20px; font-weight: bold;">🏢 {emp}</span>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Ver {len(df_detalhe)} apólice(s)"):
                df_exibir = df_detalhe[['Apólice', 'Seguro', 'Fim Apólice']].copy()
                df_exibir['Fim Apólice'] = df_exibir['Fim Apólice'].dt.strftime('%d/%m/%Y')
                st.dataframe(df_exibir, hide_index=True, use_container_width=True)

    with col1:
        st.metric('Total de Clientes', len(empresas_no_filtro))
        st.write("---")
        renderizar_lista(empresas_no_filtro[:meio])

    with col2:
        st.metric('Total de Apólices', len(df_filtrado))
        st.write("---")
        renderizar_lista(empresas_no_filtro[meio:])

    st.markdown("---")
    st.plotly_chart(fig, use_container_width=True)

with aba2:
    # Restaurado conforme seu código original
    st.write("### Clientes que estão em negociação")
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c2: st.metric('Cliente', 'CIMED')
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric('Apólice', '9600131570')
        st.metric('Matriz de Riscos', 'Link')
        st.metric('Contato', 'João Silva')
    with col_b:
        st.metric('Tipo de Seguro', 'Empresarial')
        st.metric('Etapa Apresentação', 'PPT')
        st.metric('Etapa Negociação', 'Aguardando')
    with col_c:
        st.metric('Data Aviso', '15/09/2024')
        st.metric('Apresentação', 'Link')

with aba3:
    st.write("### Visão Geral dos Dados Filtrados")
    colunas_visiveis = st.multiselect('Colunas', list(df_filtrado.columns), list(df_filtrado.columns))
    st.dataframe(df_filtrado[colunas_visiveis], use_container_width=True)