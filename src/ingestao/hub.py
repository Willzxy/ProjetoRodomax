from dataclasses import asdict
from pathlib import Path
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from src.ingestao.identificador import identificar_canal
from src.ingestao.schema import DemandaPadronizada
from src.normalizadores.padronizar_csv import normalizar_csv
from src.normalizadores.padronizar_json import normalizar_json
from src.normalizadores.padronizar_txt import normalizar_email, normalizar_whatsapp


def completar_dados_faltantes(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    validos_prod = df[df["produto"].astype(str).str.strip() != ""]
    moda_rota = validos_prod.groupby(["origem", "destino"])["produto"].agg(lambda s: s.mode().iloc[0]).to_dict()
    moda_origem = validos_prod.groupby("origem")["produto"].agg(lambda s: s.mode().iloc[0]).to_dict()
    moda_global = validos_prod["produto"].mode().iloc[0]

    def preencher_produto(row):
        if str(row["produto"]).strip():
            return row["produto"]
        return moda_rota.get((row["origem"], row["destino"])) or moda_origem.get(row["origem"]) or moda_global

    df["produto"] = df.apply(preencher_produto, axis=1)

    validos_frete = df[df["valor_frete"] > 0]
    mediana_rota = validos_frete.groupby(["origem", "destino"])["valor_frete"].median().to_dict()
    tarifa_km_mediana = (validos_frete["valor_frete"] / validos_frete["distancia_km"].replace(0, np.nan)).median()

    def preencher_frete(row):
        if row["valor_frete"] > 0:
            return round(float(row["valor_frete"]), 2)
        est = mediana_rota.get((row["origem"], row["destino"]))
        if est is not None and not np.isnan(est):
            return round(float(est), 2)
        return round(float(row["distancia_km"] * tarifa_km_mediana), 2)

    df["valor_frete"] = df.apply(preencher_frete, axis=1)

    df.loc[df["peso_kg"] <= 0, "peso_kg"] = 37000.0
    df["peso_kg"] = df["peso_kg"].round(2)

    def preencher_atendida(row):
        if str(row["atendida"]).strip() in ("Sim", "Nao"):
            return row["atendida"]
        return "Sim" if (row["valor_frete"] / max(row["distancia_km"], 1.0)) >= 0.25 else "Nao"

    df["atendida"] = df.apply(preencher_atendida, axis=1)
    return df


def formatar_excel(caminho_xlsx: Path) -> None:
    wb = load_workbook(caminho_xlsx)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    col_frete = headers.index("valor_frete") + 1
    col_peso = headers.index("peso_kg") + 1
    col_dist = headers.index("distancia_km") + 1

    for row_idx in range(2, ws.max_row + 1):
        ws.cell(row=row_idx, column=col_frete).number_format = '"R$ "#,##0.00'
        ws.cell(row=row_idx, column=col_peso).number_format = '#,##0.00'
        ws.cell(row=row_idx, column=col_dist).number_format = '#,##0.0" km"'

    wb.save(caminho_xlsx)


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

        df_final = completar_dados_faltantes(pd.DataFrame(todos_registros))
        self.arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
        df_final.to_excel(self.arquivo_saida, index=False)
        formatar_excel(self.arquivo_saida)
        df_final.to_csv(self.arquivo_saida.with_suffix(".csv"), index=False)
        return df_final