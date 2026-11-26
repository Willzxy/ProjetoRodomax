from pathlib import Path
import pandas as pd
from src.ingestao.schema import DemandaPadronizada
from src.normalizadores.limpeza import (
    estimar_atendimento,
    estimar_distancia_km,
    padronizar_cidade,
    padronizar_produto,
    parse_numero_br,
)


def normalizar_csv(caminho_arquivo: Path) -> list[DemandaPadronizada]:
    df = pd.read_csv(caminho_arquivo, sep=None, engine="python")
    registros = []

    for idx, linha in df.iterrows():
        cliente = str(linha.get("Cliente", "")).strip()
        if not cliente or cliente.lower() == "nan":
            cliente = "Carteira Rodomax"

        origem = padronizar_cidade(linha.get("Cidade Carga", ""))
        destino = padronizar_cidade(linha.get("Destino", ""))
        produto = padronizar_produto(linha.get("Produto", ""))
        distancia_km = estimar_distancia_km(origem, destino)

        valor_frete = (
            parse_numero_br(linha.get("Frete Empresa"))
            or parse_numero_br(linha.get("Frete Moto 8% PJ"))
            or parse_numero_br(linha.get("Frete Moto 10%"))
            or 0.0
        )

        data_ag = str(linha.get("Data_Agendamento", "")).strip()
        if not data_ag or data_ag.lower() == "nan":
            data_ag = "2026-06-01"

        status_raw = str(linha.get("Status", "")).strip()
        atendida = estimar_atendimento(valor_frete, distancia_km, status_raw)

        registros.append(
            DemandaPadronizada(
                id_registro=f"CSV-{idx + 1:04d}",
                canal_origem="planilha_csv",
                data_recebimento=data_ag,
                cliente=cliente,
                produto=produto,
                origem=origem,
                destino=destino,
                peso_kg=0.0,
                distancia_km=distancia_km,
                prazo=status_raw if status_raw and status_raw.lower() != "nan" else "Programado",
                valor_frete=round(valor_frete, 2),
                atendida=atendida,
                texto_original=str(linha.to_dict()),
            )
        )

    return registros