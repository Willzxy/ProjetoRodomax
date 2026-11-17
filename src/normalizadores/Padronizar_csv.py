from datetime import datetime
from pathlib import Path
import pandas as pd
from src.ingestao.schema import DemandaPadronizada


def normalizar_csv(caminho_arquivo: Path) -> list[DemandaPadronizada]:
    try:
        df = pd.read_csv(caminho_arquivo, sep=None, engine="python")
    except Exception:
        df = pd.read_csv(caminho_arquivo)

    registros = []

    for idx, linha in df.iterrows():
        valor_frete = float(linha.get("valor_frete", linha.get("frete", 2800.0)))
        atendida_raw = linha.get("atendida", linha.get("status"))
        if pd.notna(atendida_raw):
            atendida = "Sim" if str(atendida_raw).lower() in ("sim", "1", "true", "atendida") else "Nao"
        else:
            atendida = "Sim" if valor_frete >= 2200.0 else "Nao"

        registros.append(
            DemandaPadronizada(
                id_registro=str(linha.get("id", f"CSV-{idx + 1:04d}")),
                canal_origem="planilha_csv",
                data_recebimento=str(linha.get("data", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                cliente=str(linha.get("cliente", f"Cliente_CSV_{idx + 1}")),
                produto=str(linha.get("produto", "Fertilizantes")),
                origem=str(linha.get("origem", "Ponta Grossa")),
                destino=str(linha.get("destino", "Cascavel")),
                peso_kg=float(linha.get("peso_kg", linha.get("peso", 10000.0))),
                distancia_km=float(linha.get("distancia_km", linha.get("distancia", 400.0))),
                prazo=str(linha.get("prazo", "48h")),
                valor_frete=valor_frete,
                atendida=atendida,
                texto_original=str(linha.to_dict()),
            )
        )

    return registros