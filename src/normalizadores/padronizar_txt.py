import re
from datetime import datetime
from src.ingestao.schema import DemandaPadronizada


def _extrair_numero(padrao: str, texto: str, padrao_retorno: float) -> float:
    match = re.search(padrao, texto, re.IGNORECASE)
    if match:
        valor_str = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(valor_str)
        except ValueError:
            return padrao_retorno
    return padrao_retorno


def _extrair_texto(padrao: str, texto: str, padrao_retorno: str) -> str:
    match = re.search(padrao, texto, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return padrao_retorno


def normalizar_whatsapp(conteudo: str) -> list[DemandaPadronizada]:
    registros = []
    blocos = re.split(r"(?=\[?\d{2}/\d{2}/\d{4})", conteudo)

    for idx, bloco in enumerate(blocos, start=1):
        bloco = bloco.strip()
        if not bloco:
            continue

        cliente = _extrair_texto(r"-\s*([^:]+):", bloco, f"Cliente_WPP_{idx}")
        produto = _extrair_texto(r"(?:produto|carga|material)[:\s]+([^\n,;]+)", bloco, "Carga Geral")
        origem = _extrair_texto(r"(?:origem|de|saindo de)[:\s]+([^\n,;]+)", bloco, "Cascavel")
        destino = _extrair_texto(r"(?:destino|para|entrega em)[:\s]+([^\n,;]+)", bloco, "Curitiba")
        prazo = _extrair_texto(r"(?:prazo|data)[:\s]+([^\n,;]+)", bloco, "48h")
        peso_kg = _extrair_numero(r"(\d+(?:[.,]\d+)?)\s*(?:kg|quilos)", bloco, 5000.0)
        distancia_km = _extrair_numero(r"(\d+(?:[.,]\d+)?)\s*km", bloco, 350.0)
        valor_frete = _extrair_numero(r"(?:r\$|frete|valor)[:\s]*(\d+(?:[.,]\d+)?)", bloco, 2500.0)
        atendida = "Sim" if valor_frete >= 2000.0 else "Nao"

        registros.append(
            DemandaPadronizada(
                id_registro=f"WPP-{idx:04d}",
                canal_origem="whatsapp",
                data_recebimento=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                cliente=cliente,
                produto=produto,
                origem=origem,
                destino=destino,
                peso_kg=peso_kg,
                distancia_km=distancia_km,
                prazo=prazo,
                valor_frete=valor_frete,
                atendida=atendida,
                texto_original=bloco,
            )
        )

    return registros


def normalizar_email(conteudo: str) -> list[DemandaPadronizada]:
    blocos = re.split(r"(?=De:|From:)", conteudo, flags=re.IGNORECASE)
    registros = []

    for idx, bloco in enumerate(blocos, start=1):
        bloco = bloco.strip()
        if not bloco:
            continue

        cliente = _extrair_texto(r"(?:De|From):\s*([^\n<]+)", bloco, f"Cliente_EML_{idx}")
        produto = _extrair_texto(r"(?:produto|carga|mercadoria)[:\s]+([^\n,;]+)", bloco, "Graos")
        origem = _extrair_texto(r"(?:origem|coleta)[:\s]+([^\n,;]+)", bloco, "Toledo")
        destino = _extrair_texto(r"(?:destino|entrega)[:\s]+([^\n,;]+)", bloco, "Paranagua")
        prazo = _extrair_texto(r"(?:prazo|entrega ate)[:\s]+([^\n,;]+)", bloco, "72h")
        peso_kg = _extrair_numero(r"(\d+(?:[.,]\d+)?)\s*(?:kg|quilos)", bloco, 12000.0)
        distancia_km = _extrair_numero(r"(\d+(?:[.,]\d+)?)\s*km", bloco, 500.0)
        valor_frete = _extrair_numero(r"(?:r\$|frete|valor)[:\s]*(\d+(?:[.,]\d+)?)", bloco, 4200.0)
        atendida = "Sim" if valor_frete >= 2500.0 else "Nao"

        registros.append(
            DemandaPadronizada(
                id_registro=f"EML-{idx:04d}",
                canal_origem="email",
                data_recebimento=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                cliente=cliente,
                produto=produto,
                origem=origem,
                destino=destino,
                peso_kg=peso_kg,
                distancia_km=distancia_km,
                prazo=prazo,
                valor_frete=valor_frete,
                atendida=atendida,
                texto_original=bloco,
            )
        )

    return registros