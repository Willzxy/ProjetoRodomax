import math
import re
import unicodedata

COORDENADAS_CIDADES = {
    "Aquidaban": (-23.16, -51.96),
    "Assis Chateaubriand": (-24.42, -53.52),
    "Boa Vista da Aparecida": (-25.43, -53.41),
    "Candoi": (-25.57, -52.05),
    "Cantagalo": (-25.37, -52.13),
    "Cascavel": (-24.96, -53.46),
    "Castro": (-24.79, -50.01),
    "Corbelia": (-24.80, -53.31),
    "Curitiba": (-25.43, -49.27),
    "Dourados": (-22.22, -54.81),
    "Engenheiro Beltrao": (-23.80, -52.27),
    "Fenix": (-23.92, -51.98),
    "Guarapuava": (-25.39, -51.46),
    "Itambe": (-23.66, -51.99),
    "Ivatuba": (-23.62, -52.22),
    "Japura": (-23.47, -52.56),
    "Lacerdopolis": (-27.26, -51.56),
    "Laguna Carapa": (-22.55, -55.15),
    "Lapa": (-25.77, -49.72),
    "Londrina": (-23.31, -51.16),
    "Mangueirinha": (-25.94, -52.17),
    "Manoel Ribas": (-24.52, -51.67),
    "Marechal Candido Rondon": (-24.56, -54.06),
    "Maringa": (-23.42, -51.94),
    "Nova Aurora": (-24.53, -53.26),
    "Palotina": (-24.28, -53.84),
    "Paranagua": (-25.52, -48.51),
    "Pinhao": (-25.70, -51.66),
    "Pirai do Sul": (-24.53, -49.95),
    "Ponta Pora": (-22.54, -55.73),
    "Quinta do Sol": (-23.85, -52.14),
    "Rio Brilhante": (-21.80, -54.55),
    "Roncador": (-24.60, -52.27),
    "Sao Francisco do Sul": (-26.24, -48.64),
    "Sao Jorge do Ivai": (-23.43, -52.29),
    "Sidrolandia": (-20.93, -54.96),
    "Toledo": (-24.72, -53.74),
    "Videira": (-27.01, -51.15),
    "Xanxere": (-26.88, -52.40),
}


def remover_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", str(texto))
        if not unicodedata.combining(c)
    )


def parse_numero_br(valor) -> float | None:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return None
    s = str(valor).strip()
    if not s or s.lower() == "nan":
        return None
    s = re.sub(r"R\$|\s|/ton|tons?|kg", "", s, flags=re.IGNORECASE).strip()
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def padronizar_produto(texto: str) -> str:
    if not texto or str(texto).strip().lower() == "nan":
        return ""
    limpo = remover_acentos(texto).upper().strip()
    limpo = re.sub(r"\s+", " ", limpo)
    if "SOJA" in limpo:
        if "GRAO" in limpo:
            return "Soja em Graos"
        if "COM" in limpo:
            return "Soja Comercial"
        return "Soja"
    if any(p in limpo for p in ("MILHO", "MII HO", "MIIHO", "MILH")):
        if "GRAO" in limpo or "GRAD" in limpo:
            return "Milho em Graos"
        return "Milho"
    return str(texto).strip().title()


def padronizar_cidade(texto: str) -> str:
    if not texto or str(texto).strip().lower() == "nan":
        return ""
    s = remover_acentos(str(texto)).strip()
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"/[A-Z]{2}\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^(?:CVALE|BUNGE|C\d+)-", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[?.,!]+$", "", s).strip()
    s = re.sub(r"\s+", " ", s)
    chave = s.lower()

    mapa = {
        "paranagu": "Paranagua",
        "paranagua": "Paranagua",
        "maring": "Maringa",
        "maringa": "Maringa",
        "pirai do su": "Pirai do Sul",
        "pirai do sul": "Pirai do Sul",
        "mal. c. rondon": "Marechal Candido Rondon",
        "mal c rondon": "Marechal Candido Rondon",
        "marechal c rondon": "Marechal Candido Rondon",
        "marechal candido rondon": "Marechal Candido Rondon",
        "eng. beltrao": "Engenheiro Beltrao",
        "eng beltrao": "Engenheiro Beltrao",
        "engenheiro beltrao": "Engenheiro Beltrao",
        "s. jorge do ivai": "Sao Jorge do Ivai",
        "s jorge do ivai": "Sao Jorge do Ivai",
        "sao jorge ivai": "Sao Jorge do Ivai",
        "sao jorge do ivai": "Sao Jorge do Ivai",
        "xao xico": "Sao Francisco do Sul",
        "indasa agroindustria": "Cascavel",
        "vila nova": "Toledo",
        "vila ipiranga": "Toledo",
    }
    if chave in mapa:
        return mapa[chave]
    for cidade_oficial in COORDENADAS_CIDADES:
        if cidade_oficial.lower() == chave:
            return cidade_oficial
    return s.title()


def estimar_distancia_km(origem: str, destino: str) -> float:
    c1 = COORDENADAS_CIDADES.get(origem)
    c2 = COORDENADAS_CIDADES.get(destino)
    if not c1 or not c2:
        return 350.0
    if origem == destino:
        return 35.0
    lat1, lon1 = math.radians(c1[0]), math.radians(c1[1])
    lat2, lon2 = math.radians(c2[0]), math.radians(c2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    dist_reta = 6371.0 * 2 * math.asin(math.sqrt(a))
    return round(dist_reta * 1.25, 1)


def estimar_atendimento(
    valor_frete: float | None,
    distancia_km: float,
    status_raw: str | None = None,
) -> str:
    if status_raw:
        st = remover_acentos(status_raw).lower().strip()
        if any(k in st for k in ("confirmado", "agendado", "ativo", "prioridade", "atendidas")):
            return "Sim"
        if any(k in st for k in ("cancelado", "inativo", "pendente")):
            return "Nao"
    if valor_frete is not None and valor_frete > 0 and distancia_km > 0:
        return "Sim" if (valor_frete / distancia_km) >= 0.25 else "Nao"
    return ""