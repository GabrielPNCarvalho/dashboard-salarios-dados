import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Data Salary Insights",
    page_icon="💰",
    layout="wide",
)


# --- Funções de Carregamento ---
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    df = pd.read_csv(url)
    return df


df = load_data()

# --- Barra Lateral (Filtros) ---
with st.sidebar:
    st.header("🔍 Filtros de Pesquisa")

    # Filtro de Ano (mantive o padrão)
    anos = st.multiselect("Ano", sorted(df['ano'].unique()), default=sorted(df['ano'].unique()))

    st.divider()

    # --- LÓGICA DO FILTRO DE CARGO (TODOS OU ESPECÍFICO) ---
    st.write("**Cargo**")
    todos_cargos = st.checkbox("Selecionar todos os cargos", value=True)

    cargos_disponiveis = sorted(df['cargo'].unique())

    if todos_cargos:
        # Se "Selecionar todos" estiver marcado, mostramos o multiselect desabilitado ou apenas informativo
        cargos_selecionados = st.multiselect("Cargos específicos", cargos_disponiveis, default=cargos_disponiveis,
                                             disabled=True)
    else:
        # Se desmarcar, o usuário escolhe o que quiser (começa vazio para ele escolher)
        cargos_selecionados = st.multiselect("Escolha os cargos:", cargos_disponiveis)

    st.divider()

    # Outros filtros
    senioridades = st.multiselect("Senioridade", sorted(df['senioridade'].unique()),
                                  default=sorted(df['senioridade'].unique()))
    tamanhos = st.multiselect("Tamanho da Empresa", sorted(df['tamanho_empresa'].unique()),
                              default=sorted(df['tamanho_empresa'].unique()))

# --- Lógica de Filtragem Corrigida ---
# Se "todos_cargos" for True, a gente nem filtra por cargo (pega todos)
if todos_cargos:
    df_filtrado = df[
        (df['ano'].isin(anos)) &
        (df['senioridade'].isin(senioridades)) &
        (df['tamanho_empresa'].isin(tamanhos))
        ]
else:
    # Se for False, a gente filtra pela lista do multiselect
    df_filtrado = df[
        (df['ano'].isin(anos)) &
        (df['cargo'].isin(cargos_selecionados)) &
        (df['senioridade'].isin(senioridades)) &
        (df['tamanho_empresa'].isin(tamanhos))
        ]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Salários: Área de Dados")

if df_filtrado.empty:
    st.warning("⚠️ Ops! Nenhum dado encontrado para essa combinação de filtros. Tente selecionar mais cargos ou anos.")
else:
    # Métricas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Média Salarial", f"USD {df_filtrado['usd'].mean():,.0f}")
    m2.metric("Salário Máximo", f"USD {df_filtrado['usd'].max():,.0f}")

    cargo_freq = df_filtrado["cargo"].mode()[0] if not df_filtrado["cargo"].empty else "N/A"
    m3.metric("Cargo Predominante", cargo_freq)
    m4.metric("Total de Registros", f"{len(df_filtrado):,}")

    st.divider()

    # Gráficos
    c1, c2 = st.columns(2)

    with c1:
        # Mostra a média salarial dos cargos selecionados
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().sort_values(ascending=True).reset_index()
        # Se houver muitos cargos, mostramos os top 15 para não poluir
        if len(top_cargos) > 15:
            top_cargos = top_cargos.tail(15)

        fig_bar = px.bar(
            top_cargos, x='usd', y='cargo', orientation='h',
            title="Média Salarial por Cargo Selecionado",
            labels={'usd': 'Salário (USD)', 'cargo': ''},
            color='usd', color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        fig_hist = px.histogram(
            df_filtrado, x='usd', nbins=25, title="Distribuição de Salários",
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Segunda linha de gráficos
    c3, c4 = st.columns(2)

    with c3:
        fig_pie = px.pie(df_filtrado, names='remoto', title='Modelo de Trabalho (Remoto vs Presencial)', hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c4:
        media_pais = df_filtrado.groupby('residencia_iso3')['usd'].mean().reset_index()
        fig_map = px.choropleth(
            media_pais, locations='residencia_iso3', color='usd',
            title='Salário Médio Mundial (Filtros Ativos)',
            color_continuous_scale='YlGnBu'
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # Tabela detalhada
    with st.expander("📄 Ver base de dados filtrada"):
        st.dataframe(df_filtrado, use_container_width=True)