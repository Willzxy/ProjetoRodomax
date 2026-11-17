from dataclasses import dataclass

@dataclass
class DemandaPadronizada:
    id_registro: str
    canal_origem: str
    data_recebimento: str
    cliente: str
    produto: str
    origem: str
    destino: str
    peso_kg: float
    distancia_km: float
    prazo: str
    valor_frete: float
    atendida: str
    texto_original: str