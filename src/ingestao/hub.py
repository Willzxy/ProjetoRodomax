from dataclasses import asdict
from pathlib import Path
import pandas as pd
from src.ingestao.identificador import identificar_canal
from src.ingestao.schema import DemandaPadronizada
from src.normalizadores.padronizar_csv import normalizar_csv
from src.normalizadores.padronizar_json import normalizar_json
from src.normalizadores.padronizar_txt import normalizar_email, normalizar_whatsapp


class HubIngestao:
    def __init__(self, pasta_entrada: Path, arquivo_saida: Path):
        self.pasta_entrada = pasta_entrada
        self.arquivo_saida = arquivo_saida

    def processar_arquivo(self, caminho: Path) -> list[DemandaPadronizada]:
        conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
        canal = identificar_canal(caminho, conteudo)

        if canal == "whatsapp":
            return normalizar_whatsapp(conteudo)
        if canal == "email":
            return normalizar_email(conteudo)
        if canal == "api_webhook":
            return normalizar_json(conteudo)
        if canal == "planilha_csv":
            return normalizar_csv(caminho)

        return []

    def executar_pipeline(self) -> pd.DataFrame:
        todos_registros = []
        for arquivo in sorted(self.pasta_entrada.iterdir()):
            if arquivo.is_file():
                registros = self.processar_arquivo(arquivo)
                todos_registros.extend(asdict(r) for r in registros)

        df_final = pd.DataFrame(todos_registros)
        self.arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
        df_final.to_excel(self.arquivo_saida, index=False)
        df_final.to_csv(self.arquivo_saida.with_suffix(".csv"), index=False)
        return df_final