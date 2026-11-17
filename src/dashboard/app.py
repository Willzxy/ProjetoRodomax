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
        col2.metric("Peso Total (kg)", f"{df['peso_kg'].sum():,.0f}")
    if "valor_frete" in df.columns:
        col3.metric("Frete Medio (R$)", f"{df['valor_frete'].mean():,.2f}")

    graf1, graf2 = st.columns(2)
    if "canal_origem" in df.columns:
        fig_canal = px.pie(df, names="canal_origem", title="Demandas por Canal")
        graf1.plotly_chart(fig_canal, use_container_width=True)
    if "produto" in df.columns:
        fig_prod = px.bar(
            df["produto"].value_counts().reset_index(),
            x="produto",
            y="count",
            title="Demandas por Produto",
        )
        graf2.plotly_chart(fig_prod, use_container_width=True)

    st.subheader("Base Unificada")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Arquivo rodomax_demandas.csv ainda nao foi gerado.")

st.divider()
st.subheader("Simulador de Nova Demanda (Modelo de Classificacao)")

with st.form("form_nova_demanda"):
    c1, c2, c3 = st.columns(3)
    produto = c1.text_input("Produto", value="Graos")
    origem = c2.text_input("Origem", value="Curitiba")
    destino = c3.text_input("Destino", value="Londrina")

    c4, c5, c6, c7 = st.columns(4)
    peso_kg = c4.number_input("Peso (kg)", min_value=1.0, value=12000.0)
    distancia_km = c5.number_input("Distancia (km)", min_value=1.0, value=380.0)
    valor_frete = c6.number_input("Valor Frete (R$)", min_value=1.0, value=3500.0)
    canal = c7.selectbox("Canal", ["whatsapp", "email", "api_webhook", "planilha_csv"])

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