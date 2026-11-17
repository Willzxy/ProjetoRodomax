from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
CAMINHO_MODELO = BASE_DIR / "dados" / "saida" / "modelo_classificacao.joblib"


def prever_atendimento(
    peso_kg: float,
    distancia_km: float,
    valor_frete: float,
    produto: str,
    origem: str,
    destino: str,
    canal_origem: str = "whatsapp",
) -> tuple[str, float]:
    modelo = joblib.load(CAMINHO_MODELO)
    entrada = pd.DataFrame(
        [
            {
                "peso_kg": peso_kg,
                "distancia_km": distancia_km,
                "valor_frete": valor_frete,
                "produto": produto,
                "origem": origem,
                "destino": destino,
                "canal_origem": canal_origem,
            }
        ]
    )
    classe_prevista = str(modelo.predict(entrada)[0])
    probabilidades = modelo.predict_proba(entrada)[0]
    confianca = float(max(probabilidades))
    return classe_prevista, confianca


if __name__ == "__main__":
    resultado, confianca = prever_atendimento(
        peso_kg=15000.0,
        distancia_km=500.0,
        valor_frete=4200.0,
        produto="Soja",
        origem="Curitiba",
        destino="Londrina",
    )
    print(f"Demanda sera atendida? {resultado} (Confianca: {confianca:.1%})")