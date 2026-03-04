import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Central de Performance Comercial 2026", layout="wide")

# =====================================================
# METAS
# =====================================================

METAS = {
    "Janeiro": 2436225.96,
    "Fevereiro": 3193147.61,
    "Março": 3186391.65
}

META_KG = 164430

# =====================================================
# FORMATAÇÃO EXECUTIVA
# =====================================================

def formatar_moeda(valor):
    if valor >= 1_000_000:
        return f"R$ {valor/1_000_000:,.3f} MI"
    elif valor >= 1_000:
        return f"R$ {valor/1_000:,.3f} MIL"
    else:
        return f"R$ {valor:,.2f}"

# =====================================================
# CARREGAR DADOS
# =====================================================

@st.cache_data
def carregar_dados():
    df_sc = pd.read_excel("BASE_SC_SP_NEW.xlsx", sheet_name="SC")
    df_sp = pd.read_excel("BASE_SC_SP_NEW.xlsx", sheet_name="SP")

    df_sc.columns = df_sc.columns.str.strip()
    df_sp.columns = df_sp.columns.str.strip()

    df_sc["Filial"] = "SC"
    df_sp["Filial"] = "SP"

    df = pd.concat([df_sc, df_sp], ignore_index=True)

    df["DT Emissao"] = pd.to_datetime(df["DT Emissao"])

    mapa_meses = {
        "January": "Janeiro",
        "February": "Fevereiro",
        "March": "Março",
        "April": "Abril",
        "May": "Maio",
        "June": "Junho",
        "July": "Julho",
        "August": "Agosto",
        "September": "Setembro",
        "October": "Outubro",
        "November": "Novembro",
        "December": "Dezembro"
    }

    df["Mes"] = df["DT Emissao"].dt.strftime("%B").map(mapa_meses)

    if "Vendedor 1" in df.columns:
        df = df[df["Vendedor 1"] != "KP"]

    return df

df = carregar_dados()

# =====================================================
# CAPA
# =====================================================

st.image("CAPA.png", use_container_width=True)
st.title("Central de Performance Comercial 2026")
st.markdown("### Análise estratégica de faturamento, metas e performance – SC x SP")
# =====================================================
# FILTROS
# =====================================================

# =====================================================
# FILTROS
# =====================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    vendedor = st.multiselect(
        "Vendedor",
        sorted(df["Vendedor 1"].dropna().unique()),
        placeholder="Selecione o vendedor"
    )

with col2:
    grupo = st.multiselect(
        "Grupo de Produto",
        sorted(df["Nome Grupo"].dropna().unique()),
        placeholder="Selecione o grupo"
    )

with col3:
    produto = st.multiselect(
        "Descrição do Produto",
        sorted(df["Descricao"].dropna().unique()),
        placeholder="Selecione o produto"
    )

with col4:
    estado = st.multiselect(
        "Estado",
        sorted(df["Estado"].dropna().unique()),
        placeholder="Selecione o estado"
    )

with col5:
    mes = st.multiselect(
        "Mês Faturamento",
        sorted(df["Mes"].dropna().unique()),
        placeholder="Selecione o mês"
    )

# =====================================================
# FILTRAGEM
# =====================================================

df_filtrado = df.copy()

if vendedor:
    df_filtrado = df_filtrado[df_filtrado["Vendedor 1"].isin(vendedor)]

if grupo:
    df_filtrado = df_filtrado[df_filtrado["Nome Grupo"].isin(grupo)]

if estado:
    df_filtrado = df_filtrado[df_filtrado["Estado"].isin(estado)]

if mes:
    df_filtrado = df_filtrado[df_filtrado["Mes"].isin(mes)]

if produto:
    df_filtrado = df_filtrado[df_filtrado["Descricao"].isin(produto)]

# =====================================================
# META E CÁLCULOS
# =====================================================

meta_valor = sum(METAS.get(m, 0) for m in mes) if mes else sum(METAS.values())

faturamento = df_filtrado["Total"].sum()
quantidade = df_filtrado["Quantidade"].sum()

percentual_meta = (faturamento / meta_valor) * 100 if meta_valor else 0
falta_meta = meta_valor - faturamento
percentual_meta_kg = (quantidade / META_KG) * 100 if META_KG else 0

# =====================================================
# INDICADORES FINANCEIROS
# =====================================================

st.subheader("Indicadores Financeiros")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Faturamento Total", formatar_moeda(faturamento))
c2.metric("Meta do Período", formatar_moeda(meta_valor))
c3.metric("Saldo para Meta", formatar_moeda(falta_meta))
c4.metric("Atingimento (%)", f"{percentual_meta:,.2f}%")

st.divider()

# =====================================================
# INDICADORES DE VOLUME
# =====================================================

st.subheader("Indicadores de Volume")

k1, k2, k3 = st.columns(3)

k1.metric("Volume Comercializado", f"{quantidade:,.0f} KG")
k2.metric("Meta de Volume", f"{META_KG:,.0f} KG")
k3.metric("Atingimento Volume (%)", f"{percentual_meta_kg:,.2f}%")

st.divider()

# =====================================================
# EVOLUÇÃO MENSAL DE FATURAMENTO
# =====================================================

st.subheader("Evolução Mensal do Faturamento 2026")

# Ordem correta dos meses
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

faturamento_mensal = (
    df.groupby("Mes")["Total"]
    .sum()
    .reindex(ordem_meses)
    .dropna()
    .reset_index()
)

if not faturamento_mensal.empty:
    fig_linha = px.line(
        faturamento_mensal,
        x="Mes",
        y="Total",
        markers=True
    )

    fig_linha.update_layout(
        xaxis_title="Mês",
        yaxis_title="Faturamento",
        yaxis_tickprefix="R$ "
    )

    st.plotly_chart(fig_linha, use_container_width=True, key="evolucao_mensal")

# =====================================================
# COMPARATIVO SC x SP
# =====================================================

st.subheader("Comparativo de Faturamento – SC x SP")

comparativo = df_filtrado.groupby("Filial")["Total"].sum().reset_index()

if not comparativo.empty:
    fig_comp = px.bar(comparativo, x="Filial", y="Total", text_auto=".3s")
    st.plotly_chart(fig_comp, use_container_width=True, key="comparativo")

st.divider()

# =====================================================
# TOP 5 ESTADOS
# =====================================================

st.subheader("Top 5 Estados")

top_estados = (
    df_filtrado.groupby("Estado")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

if not top_estados.empty:
    fig_estados = px.pie(top_estados, names="Estado", values="Total", hole=0.4)
    st.plotly_chart(fig_estados, use_container_width=True, key="estados")

st.divider()

# =====================================================
# TOP 3 PRODUTOS - MAIOR
# =====================================================

st.subheader("Top 3 Produtos - Maior Performance")

top_produtos = (
    df_filtrado.groupby("Descricao")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(3)
    .reset_index()
)

if not top_produtos.empty:
    fig_top = px.bar(top_produtos, x="Descricao", y="Total", text_auto=".3s")
    st.plotly_chart(fig_top, use_container_width=True, key="top_maior")

# =====================================================
# TOP 3 PRODUTOS - MENOR
# =====================================================

st.subheader("Top 3 Produtos - Menor Performance")

bottom_produtos = (
    df_filtrado.groupby("Descricao")["Total"]
    .sum()
    .sort_values(ascending=True)
    .head(3)
    .reset_index()
)

if not bottom_produtos.empty:
    fig_bottom = px.bar(bottom_produtos, x="Descricao", y="Total", text_auto=".3s")
    st.plotly_chart(fig_bottom, use_container_width=True, key="top_menor")

st.divider()

# =====================================================
# RANKING VENDEDORES
# =====================================================

st.subheader("Ranking de Vendedores")

ranking = (
    df_filtrado.groupby("Vendedor 1")["Total"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

if not ranking.empty:
    fig_rank = px.bar(ranking, x="Vendedor 1", y="Total", text_auto=".3s")
    st.plotly_chart(fig_rank, use_container_width=True, key="ranking")

    st.dataframe(
        ranking.style.format({"Total": "R$ {:,.2f}"}),
        use_container_width=True
    )

st.divider()

# =====================================================
# TOP 3 CLIENTES
# =====================================================

st.subheader("Top 3 Clientes")

top_clientes = (
    df_filtrado.groupby("Nome")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(3)
    .reset_index()
)

if not top_clientes.empty:
    fig_clientes = px.bar(top_clientes, x="Nome", y="Total", text_auto=".3s")
    st.plotly_chart(fig_clientes, use_container_width=True, key="clientes")

    top_clientes["% Participação"] = (
        top_clientes["Total"] / faturamento * 100 if faturamento else 0
    )

    st.dataframe(
        top_clientes.style.format({
            "Total": "R$ {:,.2f}",
            "% Participação": "{:.2f}%"
        }),
        use_container_width=True
    )

st.divider()

# =====================================================
# BASE DETALHADA
# =====================================================

st.subheader("Base de Dados Detalhada")
st.dataframe(df_filtrado, use_container_width=True)