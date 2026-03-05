import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Kemparts", layout="wide")

st.title("📊 Painel Geral Kemparts 2026")

# Carregar base
@st.cache_data
def carregar_dados():
    df = pd.read_excel("BASE_KEMPARTS.xlsx")
    return df

df = carregar_dados()

st.success("Base carregada com sucesso!")

# Mostrar dados
st.subheader("📋 Base de Dados")
st.dataframe(df)

# Filtro simples
st.sidebar.header("Filtros")

colunas = df.columns.tolist()
coluna_filtro = st.sidebar.selectbox("Escolha uma coluna", colunas)

valores = df[coluna_filtro].unique()
valor = st.sidebar.selectbox("Escolha um valor", valores)

df_filtrado = df[df[coluna_filtro] == valor]

st.subheader("📊 Dados Filtrados")
st.dataframe(df_filtrado)
