import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Data Salary Insights",
    page_icon="💰",
    layout="wide",
)

# --- Estilo CSS Customizado (Opcional para dar um toque extra) ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E88E5; }
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)


# --- Funções de Carregamento ---
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    df = pd.read_csv(url)
    return df


df = load_data()

# --- Barra Lateral (Filtros Organizados) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=80)  # Ícone meramente ilustrativo
    st.title("Painel de Controle")
    st.info("Ajuste os filtros abaixo para atualizar os gráficos em tempo real.")

    # Filtro de Ano Principal
    st.subheader("📅 Período")
    anos = st.multiselect("Selecione os Anos", sorted(df['ano'].unique()), default=sorted(df['ano'].unique()))

    st.divider()

    # Agrupando filtros secundários em Expansers para economizar espaço
    with st.expander("💼 Filtros de Cargo", expanded=True):
        todos_cargos = st.toggle("Selecionar todos os cargos", value=True)
        cargos_disponiveis = sorted(df['cargo'].unique())

        if todos_cargos:
            cargos_selecionados = cargos_disponiveis
            st.caption("✅ Todos os cargos incluídos")
        else:
            cargos_selecionados = st.multiselect("Escolha os cargos:", cargos_disponiveis)

    with st.expander("🏢 Perfil da Empresa & Experiência"):
        senioridades = st.multiselect("Nível de Senioridade", sorted(df['senioridade'].unique()),
                                      default=sorted(df['senioridade'].unique()))

        tamanhos = st.multiselect("Tamanho da Empresa", sorted(df['tamanho_empresa'].unique()),
                                  default=sorted(df['tamanho_empresa'].unique()))

    st.sidebar.markdown("---")
    st.sidebar.caption("Dados atualizados para 2026 • Versão 2.0")

# --- Lógica de Filtragem ---
df_filtrado = df[
    (df['ano'].isin(anos)) &
    (df['cargo'].isin(cargos_selecionados)) &
    (df['senioridade'].isin(senioridades)) &
    (df['tamanho_empresa'].isin(tamanhos))
    ]

# --- Conteúdo Principal ---
st.title("💰 Salary Data Insights")
st.markdown("Analise a evolução salarial e tendências globais do mercado de dados.")

if df_filtrado.empty:
    st.error("❌ **Nenhum dado encontrado.** Ajuste os filtros na barra lateral.")
else:
    # --- Métricas em Destaque ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Média Salarial", f"USD {df_filtrado['usd'].mean():,.0f}")
    with m2:
        st.metric("Teto Salarial", f"USD {df_filtrado['usd'].max():,.0f}")
    with m3:
        cargo_freq = df_filtrado["cargo"].mode()[0] if not df_filtrado["cargo"].empty else "N/A"
        st.metric("Cargo mais Comum", cargo_freq)
    with m4:
        st.metric("Amostras", f"{len(df_filtrado):,}")

    st.markdown("---")

    # --- Gráficos ---
    c1, c2 = st.columns([6, 4])  # Proporção de largura diferente

    with c1:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().sort_values(ascending=True).reset_index().tail(15)
        fig_bar = px.bar(
            top_cargos, x='usd', y='cargo', orientation='h',
            title="Top 15 Médias Salariais por Cargo",
            color='usd', color_continuous_scale='Viridis',
            template="plotly_white"
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        fig_pie = px.pie(
            df_filtrado, names='remoto',
            title='Modelo de Trabalho',
            hole=0.6,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Segunda linha
    c3, c4 = st.columns([4, 6])

    with c3:
        fig_hist = px.histogram(
            df_filtrado, x='usd', nbins=20,
            title="Frequência Salarial",
            color_discrete_sequence=['#636EFA'],
            template="plotly_white"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c4:
        media_pais = df_filtrado.groupby('residencia_iso3')['usd'].mean().reset_index()
        fig_map = px.choropleth(
            media_pais, locations='residencia_iso3', color='usd',
            title='Distribuição Geográfica (Média USD)',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # Tabela detalhada com busca
    st.markdown("### 🔍 Detalhamento dos Dados")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)