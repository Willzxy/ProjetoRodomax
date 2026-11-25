import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from src.ia.preditor import prever_atendimento

CAMINHO_CSV = BASE_DIR / "dados" / "saida" / "rodomax_demandas.csv"

st.set_page_config(page_title="HUB Rodomax - IA", layout="wide")
st.title("HUB Integrador Rodomax - Dashboard e Classificacao")

if CAMINHO_CSV.exists():
    df = pd.read_csv(CAMINHO_CSV)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Demandas", len(df))
    if "peso_kg" in df.columns:
        col2.metric("Saldo Total (ton)", f"{df['peso_kg'].sum() / 1000:,.0f}")
    if "valor_frete" in df.columns:
        fretes_validos = df.loc[df["valor_frete"] > 0, "valor_frete"]
        col3.metric("Frete Medio (R$/ton)", f"R$ {fretes_validos.mean():,.2f}")

    graf1, graf2 = st.columns(2)
    if "canal_origem" in df.columns:
        fig_canal = px.pie(df, names="canal_origem", title="Demandas por Canal")
        graf1.plotly_chart(fig_canal, width="stretch")
    if "produto" in df.columns:
        fig_prod = px.bar(
            df["produto"].value_counts().reset_index(),
            x="produto",
            y="count",
            title="Demandas por Produto",
        )
        graf2.plotly_chart(fig_prod, width="stretch")

    st.subheader("Base Unificada")
    st.dataframe(df, width="stretch")
else:
    st.warning("Arquivo rodomax_demandas.csv ainda nao foi gerado.")

st.divider()
st.subheader("Simulador de Nova Demanda (Modelo de Classificacao)")

with st.form("form_nova_demanda"):
    c1, c2, c3 = st.columns(3)
    produto = c1.selectbox("Produto", ["Soja", "Milho"])
    origem = c2.text_input("Origem", value="Cascavel")
    destino = c3.text_input("Destino", value="Paranagua")

    c4, c5, c6, c7 = st.columns(4)
    peso_kg = c4.number_input("Peso / Saldo (kg)", min_value=1.0, value=1500000.0)
    distancia_km = c5.number_input("Distancia (km)", min_value=1.0, value=490.0)
    valor_frete = c6.number_input("Valor Frete (R$/ton)", min_value=1.0, value=180.0)
    canal = c7.selectbox("Canal", ["email", "whatsapp", "planilha_csv", "api_webhook"])

    enviado = st.form_submit_button("Prever Atendimento")

if enviado:
    classe, confianca = prever_atendimento(
        peso_kg=peso_kg,
        distancia_km=distancia_km,
        valor_frete=valor_frete,
        produto=produto,
        origem=origem,
        destino=destino,
        canal_origem=canal,
    )
    st.success(f"Resultado da Classificacao: {classe} | Confianca: {confianca:.1%}")