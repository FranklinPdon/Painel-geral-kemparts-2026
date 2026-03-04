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

METAS_KG = {
    "Janeiro": 126670,
    "Fevereiro": 164430,
    "Março": 167371,
    "Abril": 191195,
    "Maio": 190840,
    "Junho": 230735,
    "Julho": 202845,
    "Agosto": 216508,
    "Setembro": 226475,
    "Outubro": 194810,
    "Novembro": 201370,
    "Dezembro": 157346
}

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
    df_sc = pd.read_excel("BASE_SC_SP_NEW.xlsx", sheet_name="SP")
    df_sp = pd.read_excel("BASE_SC_SP_NEW.xlsx", sheet_name="SC")

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

col1, col2, col3, col4 = st.columns(4)

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
    estado = st.multiselect(
        "Estado",
        sorted(df["Estado"].dropna().unique()),
        placeholder="Selecione o estado"
    )

with col4:
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

# =====================================================
# META E CÁLCULOS
# =====================================================

meta_valor = sum(METAS.get(m, 0) for m in mes) if mes else sum(METAS.values())

faturamento = df_filtrado["Total"].sum()
quantidade = df_filtrado["Quantidade"].sum()

percentual_meta = (faturamento / meta_valor) * 100 if meta_valor else 0
falta_meta = meta_valor - faturamento
meta_volume = sum(METAS_KG.get(m, 0) for m in mes) if mes else sum(METAS_KG.values())

percentual_meta_kg = (quantidade / meta_volume) * 100 if meta_volume else 0

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
# PROJEÇÃO DE FECHAMENTO DO MÊS
# =====================================================

st.subheader("Projeção de Fechamento do Mês")

from datetime import datetime
import calendar

hoje = datetime.today()

if mes and len(mes) == 1:
    mes_nome = mes[0]
else:
    mes_nome = hoje.strftime("%B")
    mapa_meses_inverso = {
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
    mes_nome = mapa_meses_inverso.get(mes_nome, mes_nome)

mapa_numero_mes = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

numero_mes = mapa_numero_mes.get(mes_nome, hoje.month)

ano_atual = hoje.year
dias_no_mes = calendar.monthrange(ano_atual, numero_mes)[1]
dia_atual = hoje.day

dias_decorridos = min(dia_atual, dias_no_mes)
dias_restantes = dias_no_mes - dias_decorridos

media_diaria = faturamento / dias_decorridos if dias_decorridos > 0 else 0
projecao_final = media_diaria * dias_no_mes

valor_restante = meta_valor - faturamento
necessario_por_dia = valor_restante / dias_restantes if dias_restantes > 0 else 0

p1, p2, p3, p4 = st.columns(4)

p1.metric("Média Diária Atual", formatar_moeda(media_diaria))
p2.metric("Projeção de Fechamento", formatar_moeda(projecao_final))
p3.metric("Dias Restantes", dias_restantes)
p4.metric("Necessário por Dia p/ Meta", formatar_moeda(necessario_por_dia))

if projecao_final >= meta_valor:
    st.success(" Mantendo o ritmo atual, a meta será atingida.")
else:
    st.error("⚠ No ritmo atual, a meta NÃO será atingida.")

# =====================================================
# INDICADORES DE VOLUME
# =====================================================

st.subheader("Indicadores de Volume")

k1, k2, k3 = st.columns(3)

k1.metric("Volume Comercializado", f"{quantidade:,.0f} KG")
k2.metric("Meta de Volume", f"{meta_volume:,.0f} KG")
k3.metric("Atingimento Volume (%)", f"{percentual_meta_kg:,.2f}%")

st.divider()

# =====================================================
# EVOLUÇÃO MENSAL
# =====================================================

st.subheader("Evolução Mensal do Faturamento 2026")

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
    st.plotly_chart(fig_linha, use_container_width=True)

# =====================================================
# TOP 5 PRODUTOS - MAIOR
# =====================================================

st.subheader("Top 5 Produtos - Maior Performance")

top_produtos = (
    df_filtrado.groupby("Descricao")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

if not top_produtos.empty:
    fig_top = px.bar(top_produtos, x="Descricao", y="Total", text_auto=".3s")
    st.plotly_chart(fig_top, use_container_width=True)

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
    st.plotly_chart(fig_rank, use_container_width=True)

st.divider()

# =====================================================
# TOP 5 CLIENTES
# =====================================================

st.subheader("Top 5 Clientes que mais compram")

top_clientes = (
    df_filtrado.groupby("Nome")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

if not top_clientes.empty:
    fig_clientes = px.bar(top_clientes, x="Nome", y="Total", text_auto=".3s")
    st.plotly_chart(fig_clientes, use_container_width=True)

st.divider()

# =====================================================
# BASE DETALHADA
# =====================================================

st.subheader("Base de Dados Detalhada")
st.dataframe(df_filtrado, use_container_width=True)