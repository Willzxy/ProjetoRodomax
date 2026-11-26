from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
CAMINHO_CSV = BASE_DIR / "dados" / "saida" / "rodomax_demandas.csv"
CAMINHO_MODELO = BASE_DIR / "dados" / "saida" / "modelo_classificacao.joblib"

st.set_page_config(page_title="HUB Rodomax - IA", layout="wide")
st.title("HUB Integrador Rodomax - Dashboard e Classificacao")

if not CAMINHO_CSV.exists():
    st.warning("Arquivo rodomax_demandas.csv ainda nao foi gerado.")
    st.stop()

df_raw = pd.read_csv(CAMINHO_CSV)

if "codigo_entrega" not in df_raw.columns:
    df_raw.insert(0, "codigo_entrega", [f"ENT-{i:04d}" for i in range(1, len(df_raw) + 1)])

colunas_modelo = [
    "peso_kg",
    "distancia_km",
    "valor_frete",
    "produto",
    "origem",
    "destino",
    "canal_origem",
]

modelo = joblib.load(CAMINHO_MODELO) if CAMINHO_MODELO.exists() else None


def proximo_numero_entrega(dataframe: pd.DataFrame) -> int:
    numeros = (
        dataframe["codigo_entrega"]
        .astype(str)
        .str.extract(r"(\d+)")[0]
        .dropna()
        .astype(int)
    )
    return int(numeros.max()) + 1 if not numeros.empty else 1


if "msg_sucesso" in st.session_state:
    st.success(st.session_state.pop("msg_sucesso"))

with st.expander("➕ Registrar Nova Demanda", expanded=False):
    with st.form("form_registrar_demanda", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        cliente = f1.text_input("Cliente / Solicitante", value="Cliente Novo")
        produto = f2.selectbox(
            "Produto",
            ["Soja em Graos", "Soja", "Soja Comercial", "Milho em Graos", "Milho"],
        )
        canal_origem = f3.selectbox(
            "Canal de Origem",
            ["whatsapp", "email", "planilha_csv", "api_webhook"],
        )

        f4, f5, f6 = st.columns(3)
        origem = f4.text_input("Origem", value="Cascavel")
        destino = f5.text_input("Destino", value="Paranagua")
        prazo = f6.text_input("Prazo", value="Hoje")

        f7, f8, f9 = st.columns(3)
        peso_kg = f7.number_input("Peso / Saldo (kg)", min_value=1.0, value=37000.0)
        distancia_km = f8.number_input("Distancia (km)", min_value=1.0, value=490.0)
        valor_frete = f9.number_input("Valor Frete (R$/ton)", min_value=1.0, value=160.0)

        salvar = st.form_submit_button("Registrar Demanda")

    if salvar:
        prox_num = proximo_numero_entrega(df_raw)
        novo_codigo = f"ENT-{prox_num:04d}"
        novo_id = f"MAN-{prox_num:04d}"

        if modelo is not None:
            entrada_nova = pd.DataFrame(
                [
                    {
                        "peso_kg": float(peso_kg),
                        "distancia_km": float(distancia_km),
                        "valor_frete": float(valor_frete),
                        "produto": produto,
                        "origem": origem.strip() or "Nao Informada",
                        "destino": destino.strip() or "Nao Informada",
                        "canal_origem": canal_origem,
                    }
                ]
            )
            atendida_nova = str(modelo.predict(entrada_nova)[0])
        else:
            atendida_nova = "Sim" if (float(valor_frete) / float(distancia_km)) >= 0.25 else "Nao"

        nova_demanda = {
            "codigo_entrega": novo_codigo,
            "id_registro": novo_id,
            "canal_origem": canal_origem,
            "data_recebimento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cliente": cliente.strip() or "Cliente Manual",
            "produto": produto,
            "origem": origem.strip() or "Nao Informada",
            "destino": destino.strip() or "Nao Informada",
            "peso_kg": round(float(peso_kg), 2),
            "distancia_km": round(float(distancia_km), 1),
            "prazo": prazo.strip() or "Hoje",
            "valor_frete": round(float(valor_frete), 2),
            "atendida": atendida_nova,
            "texto_original": f"Cadastro manual: {produto} | {origem} -> {destino} | R$ {valor_frete:.2f}/ton",
        }

        df_nova = pd.DataFrame([nova_demanda])
        df_atualizado = pd.concat([df_nova, df_raw], ignore_index=True)
        df_atualizado.to_csv(CAMINHO_CSV, index=False)
        st.session_state["msg_sucesso"] = f"Demanda {novo_codigo} registrada e adicionada no topo da tabela."
        st.rerun()

df = df_raw.copy()

if modelo is not None and all(c in df.columns for c in colunas_modelo):
    df["previsao_ia"] = modelo.predict(df[colunas_modelo])
    probabilidades = modelo.predict_proba(df[colunas_modelo])
    df["confianca_ia"] = [round(float(max(p)) * 100.0, 1) for p in probabilidades]
else:
    df["previsao_ia"] = df["atendida"] if "atendida" in df.columns else "Nao"
    df["confianca_ia"] = 100.0

df["tarifa_km"] = df.apply(
    lambda r: round(float(r["valor_frete"]) / float(r["distancia_km"]), 4)
    if float(r["distancia_km"]) > 0
    else 0.0,
    axis=1,
)

col1, col2, col3 = st.columns(3)
col1.metric("Total de Demandas", len(df))
if "peso_kg" in df.columns:
    col2.metric("Saldo Total (ton)", f"{df['peso_kg'].sum() / 1000:,.0f}")
if "valor_frete" in df.columns:
    col3.metric("Frete Medio (R$/ton)", f"R$ {df['valor_frete'].mean():,.2f}")

graf1, graf2 = st.columns(2)
if "canal_origem" in df.columns:
    fig_canal = px.pie(df, names="canal_origem", title="Demandas por Canal")
    graf1.plotly_chart(fig_canal, width="stretch")
if "produto" in df.columns:
    contagem_prod = df["produto"].value_counts().reset_index()
    contagem_prod.columns = ["produto", "quantidade"]
    fig_prod = px.bar(
        contagem_prod,
        x="produto",
        y="quantidade",
        text="quantidade",
        title="Demandas por Produto",
    )
    graf2.plotly_chart(fig_prod, width="stretch")

st.subheader("Base Unificada")
st.dataframe(
    df,
    width="stretch",
    hide_index=True,
    column_config={
        "codigo_entrega": st.column_config.TextColumn("ID Entrega"),
        "valor_frete": st.column_config.NumberColumn("Frete (R$/ton)", format="R$ %.2f"),
        "peso_kg": st.column_config.NumberColumn("Peso / Saldo (kg)", format="%.2f kg"),
        "distancia_km": st.column_config.NumberColumn("Distancia (km)", format="%.1f km"),
        "tarifa_km": st.column_config.NumberColumn("Tarifa/km", format="R$ %.2f"),
        "confianca_ia": st.column_config.NumberColumn("Confianca IA", format="%.1f%%"),
    },
)