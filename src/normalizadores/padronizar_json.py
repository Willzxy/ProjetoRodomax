import json
from datetime import datetime
from src.ingestao.schema import DemandaPadronizada
from src.normalizadores.limpeza import (
    estimar_atendimento,
    estimar_distancia_km,
    padronizar_cidade,
    padronizar_produto,
    parse_numero_br,
)


def normalizar_json(conteudo: str) -> list[DemandaPadronizada]:
    dados = json.loads(conteudo)
    lista_itens = dados if isinstance(dados, list) else [dados]
    registros = []

    for idx, item in enumerate(lista_itens, start=1):
        origem = padronizar_cidade(item.get("ponto_origem", item.get("origem", "")))
        destino = padronizar_cidade(item.get("ponto_destino", item.get("destino", "")))
        produto = padronizar_produto(item.get("produto", ""))
        vol_ton = parse_numero_br(item.get("volume_ton", 0.0)) or 0.0
        distancia_km = estimar_distancia_km(origem, destino)
        valor_frete = parse_numero_br(item.get("valor_frete", item.get("frete"))) or 0.0
        atendida = estimar_atendimento(valor_frete, distancia_km, item.get("status"))

        registros.append(
            DemandaPadronizada(
                id_registro=f"API-{item.get('id_agendamento', idx)}",
                canal_origem="api_webhook",
                data_recebimento=str(item.get("data_hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                cliente=str(item.get("codigo_rodo", f"Cliente_API_{idx}")),
                produto=produto,
                origem=origem,
                destino=destino,
                peso_kg=round(vol_ton * 1000.0, 2),
                distancia_km=distancia_km,
                prazo=str(item.get("janela_atendimento", "Comercial")),
                valor_frete=round(valor_frete, 2),
                atendida=atendida,
                texto_original=json.dumps(item, ensure_ascii=False),
            )
        )

    return registros