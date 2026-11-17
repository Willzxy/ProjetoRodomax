import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PASTAS_LIMPAR = [
    BASE_DIR / "dados" / "entrada",
    BASE_DIR / "dados" / "saida",
]

for pasta in PASTAS_LIMPAR:
    if pasta.exists():
        for item in pasta.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"Pasta limpa: {pasta}")