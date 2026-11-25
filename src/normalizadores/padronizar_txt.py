import re
from datetime import datetime
from src.ingestao.schema import DemandaPadronizada
from src.normalizadores.limpeza import (
    estimar_atendimento,
    estimar_distancia_km,
    padronizar_cidade,
    padronizar_produto,
    parse_numero_br,
)


def normalizar_whatsapp(conteudo: str) -> list[DemandaPadronizada]:
    blocos = re.split(r"(?=^---\s*Mensagem\s+\d+)", conteudo, flags=re.MULTILINE)
    avisos_ruido = (
        "sinalizar o mais breve possivel",
        "entrar em contrato para realizar o agendamento",
    )
    registros = []

    for bloco in blocos:
        bloco = bloco.strip()
        if not bloco:
            continue
        linhas = bloco.splitlines()
        cabecalho = linhas[0]
        corpo = "\n".join(linhas[1:]).strip()
        if not corpo or any(a in corpo.lower() for a in avisos_ruido):
            continue

        m_cab = re.search(r"Mensagem\s+(\d+)\s*\|\s*([^|]+)\|\s*(.+?)\s*---", cabecalho)
        num_msg = int(m_cab.group(1)) if m_cab else len(registros) + 1
        data_msg = m_cab.group(2).strip() if m_cab else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cliente = m_cab.group(3).strip() if m_cab else "WhatsApp"

        m_prod = re.search(
            r"(SOJA(?:\s+EM\s+GR[AÃ]OS|\s+COMERCIAL|\s+COML)?|MILHO(?:\s+EM\s+GR[AÃD]OS|\s+EM\s+GRADS)?|MII\s*HO)",
            corpo,
            re.IGNORECASE,
        )
        produto = padronizar_produto(m_prod.group(1)) if m_prod else "Nao Informado"

        origem, destino = "Nao Informada", "Nao Informada"
        corpo_limpo = re.sub(r"[^\w\s.,:/\-()?]", " ", corpo)
        corpo_limpo = re.sub(r"\s+", " ", corpo_limpo).strip()

        padroes_rota = (
            r"Rota:\s*([A-Za-zÀ-ÿ.\s/]+?)\s+[xX]\s+([A-Za-zÀ-ÿ.\s/]+?)(?:\s+Produto|\s+-|\s*,|$)",
            r"([A-Za-zÀ-ÿ.\s/]+?)\s*\([^)]*\)\s*[xX]\s*([A-Za-zÀ-ÿ.\s/]+?)(?:\s*-|\s*,|$)",
            r"(?:abriu vaga agora em|pra|confirmado pra)\s+([A-Za-zÀ-ÿ.\s/]+?)\s+[xX]\s+([A-Za-zÀ-ÿ.\s/]+?)(?:\?|,|\s+-|$)",
            r"(?:faz\s+\d+\s*-\s*|SOJA(?:\s+EM\s+GRAOS)?\s*-\s*|MILHO(?:\s+EM\s+GRAOS)?\s*-\s*)([A-Za-zÀ-ÿ.\s/]+?)\s+pra\s+([A-Za-zÀ-ÿ.\s/]+?)(?:\s*-|\s*,|$)",
            r"(?:precisamos de \d+ veiculos pra|valor do frete)\s+([A-Za-zÀ-ÿ.\s/]+?)\s*-\s*([A-Za-zÀ-ÿ.\s/]+?)(?:\?| ainda|,|$)",
            r"^([A-Za-zÀ-ÿ.\s/]+?)\s+[xX]\s+([A-Za-zÀ-ÿ.\s/]+?)\s*-",
        )
        for padrao in padroes_rota:
            m_rota = re.search(padrao, corpo_limpo, re.IGNORECASE)
            if m_rota:
                origem = padronizar_cidade(m_rota.group(1))
                destino = padronizar_cidade(m_rota.group(2))
                break

        if origem == "Nao Informada":
            m_saldo_cid = re.search(r"saldo de\s+([A-Za-zÀ-ÿ.\s/]+?)\s+caiu", corpo_limpo, re.IGNORECASE)
            if m_saldo_cid:
                origem = padronizar_cidade(m_saldo_cid.group(1))
                destino = "Paranagua"

        m_frete = re.search(r"R\$\s*(\d+(?:[.,]\d+)?)", corpo)
        valor_frete = parse_numero_br(m_frete.group(1)) if m_frete else None

        m_saldo = re.search(
            r"saldo\s*(?:de\s+[A-Za-zÀ-ÿ\s]+?\s+caiu\s+pra\s+)?(\d+(?:[.,]\d+)*)",
            corpo,
            re.IGNORECASE,
        )
        saldo_ton = parse_numero_br(m_saldo.group(1)) if m_saldo else None
        peso_kg = round(saldo_ton * 1000.0, 2) if saldo_ton else 0.0

        m_prazo = re.search(r"(?:ate as|emb ate|previsao de chegada)\s*([0-9:h]+)", corpo, re.IGNORECASE)
        prazo = m_prazo.group(1) if m_prazo else ("Hoje" if "hoje" in corpo.lower() or "hj" in corpo.lower() else "Nao Informado")

        distancia_km = estimar_distancia_km(origem, destino)

        status_wpp = None
        if "confirmado pra" in corpo.lower():
            status_wpp = "confirmado"
        elif "urgente" in corpo.lower() or "qual o valor" in corpo.lower():
            status_wpp = "pendente"

        atendida = estimar_atendimento(valor_frete, distancia_km, status_wpp)

        registros.append(
            DemandaPadronizada(
                id_registro=f"WPP-{num_msg:04d}",
                canal_origem="whatsapp",
                data_recebimento=data_msg,
                cliente=cliente,
                produto=produto,
                origem=origem,
                destino=destino,
                peso_kg=peso_kg,
                distancia_km=distancia_km,
                prazo=prazo,
                valor_frete=valor_frete if valor_frete is not None else 0.0,
                atendida=atendida,
                texto_original=corpo,
            )
        )

    return registros


def normalizar_email(conteudo: str) -> list[DemandaPadronizada]:
    blocos = re.split(r"(?=^=====\s*EMAIL\s+\d+\s*=====)", conteudo, flags=re.MULTILINE)
    registros = []

    for bloco in blocos:
        bloco = bloco.strip()
        if not bloco:
            continue
        linhas = [l.strip() for l in bloco.splitlines() if l.strip()]
        remetente = linhas[2].replace(" Rodomax", "").strip() if len(linhas) > 2 else "Email Comercial"
        data_email = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for l in linhas[:8]:
            if re.match(r"^(?:seg|ter|qua|qui|sex|sab|dom)\s+", l, re.IGNORECASE):
                data_email = l
                break

        for linha in linhas:
            if not re.match(r"^\d{5,}\s*\|", linha):
                continue
            partes = [p.strip() for p in linha.split("|")]
            if len(partes) < 8:
                continue

            codigo = partes[0]
            origem = padronizar_cidade(partes[1])
            destino = padronizar_cidade(partes[3])
            produto = padronizar_produto(partes[5])
            saldo_ton = parse_numero_br(partes[6]) or 0.0
            valor_frete = parse_numero_br(partes[7]) or 0.0
            distancia_km = estimar_distancia_km(origem, destino)
            atendida = estimar_atendimento(valor_frete, distancia_km)

            registros.append(
                DemandaPadronizada(
                    id_registro=f"EML-{codigo}",
                    canal_origem="email",
                    data_recebimento=data_email,
                    cliente=remetente,
                    produto=produto,
                    origem=origem,
                    destino=destino,
                    peso_kg=round(saldo_ton * 1000.0, 2),
                    distancia_km=distancia_km,
                    prazo="Programado",
                    valor_frete=valor_frete,
                    atendida=atendida,
                    texto_original=linha,
                )
            )

    return registros