import shutil
import time
from pathlib import Path
from src.ingestao.hub import HubIngestao


def simular_chegada_dados(pasta_brutos: Path, pasta_entrada: Path, intervalo_segundos: float = 0.5):
    if not pasta_brutos.exists():
        raise FileNotFoundError(f"Pasta nao encontrada: {pasta_brutos}")

    pasta_entrada.mkdir(parents=True, exist_ok=True)

    for arquivo in sorted(pasta_brutos.iterdir()):
        if arquivo.is_file():
            destino = pasta_entrada / arquivo.name
            shutil.copy2(arquivo, destino)
            print(f"[SIMULADOR] Novo dado recebido na entrada: {arquivo.name}")
            time.sleep(intervalo_segundos)


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parent
    brutos = raiz / "dados" / "brutos"
    entrada = raiz / "dados" / "entrada"
    saida = raiz / "dados" / "saida" / "rodomax_demandas.xlsx"

    simular_chegada_dados(brutos, entrada, intervalo_segundos=0.5)

    hub = HubIngestao(pasta_entrada=entrada, arquivo_saida=saida)
    df_resultado = hub.executar_pipeline()

    print(f"[HUB] Pipeline concluido. Total de registros unificados: {len(df_resultado)}")
    print(f"[HUB] Planilhas salvas em: {saida.parent}")