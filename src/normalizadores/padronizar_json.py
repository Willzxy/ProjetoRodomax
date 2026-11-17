import json
from datetime import datetime
from src.ingestao.schema import DemandaPadronizada


def normalizar_json(conteudo: str) -> list[DemandaPadronizada]:
    dados = json.loads(conteudo)
    lista_itens = dados if isinstance(dados, list) else [dados]
    registros = []

    for idx, item in enumerate(lista_itens, start=1):
        valor_frete = float(item.get("valor_frete", item.get("frete", 3000.0)))
        atendida_raw = item.get("atendida", item.get("status"))
        if atendida_raw is not None:
            atendida = "Sim" if str(atendida_raw).lower() in ("sim", "1", "true", "atendida") else "Nao"
        else:
            atendida = "Sim" if valor_frete >= 2200.0 else "Nao"

        registros.append(
            DemandaPadronizada(
                id_registro=str(item.get("id", f"API-{idx:04d}")),
                canal_origem="api_webhook",
                data_recebimento=str(item.get("data", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                cliente=str(item.get("cliente", f"Cliente_API_{idx}")),
                produto=str(item.get("produto", "Insumos")),
                origem=str(item.get("origem", "Maringa")),
                destino=str(item.get("destino", "Londrina")),
                peso_kg=float(item.get("peso_kg", item.get("peso", 8000.0))),
                distancia_km=float(item.get("distancia_km", item.get("distancia", 115.0))),
                prazo=str(item.get("prazo", "24h")),
                valor_frete=valor_frete,
                atendida=atendida,
                texto_original=json.dumps(item, ensure_ascii=False),
            )
        )

    return registros