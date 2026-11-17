import re
from pathlib import Path


def identificar_canal(caminho_arquivo: Path, conteudo_bruto: str) -> str:
    extensao = caminho_arquivo.suffix.lower()

    if extensao == ".json":
        return "api_webhook"
    if extensao == ".csv":
        return "planilha_csv"
    if extensao == ".txt":
        if re.search(r"\[\d{2}/\d{2}/\d{4},?\s+\d{2}:\d{2}", conteudo_bruto) or re.search(
            r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+-", conteudo_bruto
        ):
            return "whatsapp"
        if re.search(r"(De:|From:|Assunto:|Subject:)", conteudo_bruto, re.IGNORECASE):
            return "email"
        return "texto_generico"

    return "desconhecido"