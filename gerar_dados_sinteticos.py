"""
Gerador de dados sinteticos brutos e ruidosos - Projeto UNIVEL x RODOMAX
Simula as 4 fontes de ingestao descritas no projeto: WhatsApp, E-mails, Webhooks/API e CSV/Tabular.

Os padroes de ruido (formato de valores, campos vazios, cidade x destino) foram calibrados
para refletir o material real de referencia do projeto (planilha "Modelo atual consolidado"
e prints de WhatsApp/e-mail): fretes normalmente em reais fechados, destino concentrado em
Paranagua (fluxo de exportacao), coluna "Local carga" quase sempre vazia e "Cliente" raramente
preenchido na planilha bruta (so e resolvido depois via cruzamento com o CRM).

Uso: python gerar_dados_sinteticos.py
"""

import json
import random
from pathlib import Path

random.seed(42)

OUT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Dados de referencia (municipios, produtos, terminais etc.)
# ---------------------------------------------------------------------------

MUNICIPIOS_ORIGEM = [
    "Cantagalo", "Castro", "Pirai do Sul", "Lapa", "Roncador", "Candoi",
    "Guarapuava", "Sao Jorge do Ivai", "Itambe", "Corbelia", "Manoel Ribas",
    "Ivatuba", "Japura", "Pinhao", "Engenheiro Beltrao", "Fenix",
    "Quinta do Sol", "Mangueirinha", "Toledo", "Marechal Candido Rondon",
    "Cascavel", "Palotina", "Nova Aurora", "Assis Chateaubriand",
    "Boa Vista da Aparecida", "Aquidaban", "Dourados", "Ponta Pora",
    "Laguna Carapa", "Rio Brilhante", "Sidrolandia",
]

MUNICIPIOS_ORIGEM_TYPO = {
    "Pirai do Sul": ["Pirai do Sul", "Piraí do Sul", "PIRAI DO SU"],
    "Sao Jorge do Ivai": ["Sao Jorge do Ivai", "S. Jorge do Ivai", "Sao Jorge Ivai"],
    "Marechal Candido Rondon": ["Marechal Candido Rondon", "Mal. C. Rondon", "MARECHAL C RONDON"],
    "Engenheiro Beltrao": ["Engenheiro Beltrao", "Eng. Beltrao", "ENGENHEIRO BELTRAO"],
}

# Destino de exportacao: no material de referencia, a esmagadora maioria das cargas
# tem como destino final o porto de Paranagua. Os demais sao fluxos internos (industria/silo).
MUNICIPIOS_DESTINO = [
    "Paranagua", "Maringa", "Guarapuava", "Videira", "Lacerdopolis",
    "Sidrolandia", "Xanxere", "Cascavel", "Toledo",
]

MUNICIPIOS_DESTINO_TYPO = {
    "Paranagua": ["Paranagua", "PARANAGUA", "Paranaguá", "PARANAGUÁ", "Paranagu"],
    "Maringa": ["Maringa", "MARINGA", "Maringá", "Maring"],
    "Xanxere": ["Xanxere", "Xao Xico/SC", "XANXERE/SC"],
}

# UF real de cada municipio, usada para gerar o ruido "as vezes vem com /UF, as vezes nao".
CIDADE_UF = {
    "Cantagalo": "PR", "Castro": "PR", "Pirai do Sul": "PR", "Lapa": "PR",
    "Roncador": "PR", "Candoi": "PR", "Guarapuava": "PR", "Sao Jorge do Ivai": "PR",
    "Itambe": "PR", "Corbelia": "PR", "Manoel Ribas": "PR", "Ivatuba": "PR",
    "Japura": "PR", "Pinhao": "PR", "Engenheiro Beltrao": "PR", "Fenix": "PR",
    "Quinta do Sol": "PR", "Mangueirinha": "PR", "Toledo": "PR",
    "Marechal Candido Rondon": "PR", "Cascavel": "PR", "Palotina": "PR",
    "Nova Aurora": "PR", "Assis Chateaubriand": "PR", "Boa Vista da Aparecida": "PR",
    "Paranagua": "PR",
    "Aquidaban": "MS", "Dourados": "MS", "Ponta Pora": "MS",
    "Laguna Carapa": "MS", "Rio Brilhante": "MS", "Sidrolandia": "MS",
    "Videira": "SC", "Lacerdopolis": "SC", "Xanxere": "SC",
}

PRODUTOS = ["SOJA", "MILHO", "MILHO EM GRAOS", "SOJA EM GRAOS"]
PRODUTOS_TYPO = {
    "MILHO": ["MILHO", "Milho", "MIlho", "MII HO"],
    "MILHO EM GRAOS": ["MILHO EM GRAOS", "MILHO EM GRADS", "Milho em graos", "MILHO EM GRÃOS"],
    "SOJA": ["SOJA", "Soja", "SOJA COMERCIAL", "SOJA COML"],
}

TERMINAIS = [
    "C231-TOLEDO", "C217-CORBELIA", "VILA NOVA", "VILA IPIRANGA",
    "GRASEL & CIA LTDA", "CVALE-TOLEDO", "INDASA AGROINDUSTRIA",
    "C305-CASCAVEL", "C118-PALOTINA", "BUNGE-CASCAVEL",
]

BALANCA_RESTRICOES = [
    "Balanca 20 metros - 6, 7 e 9 eixos",
    "Balanca 25 metros - 06, 07 e 09 eixos ate 25 metros",
    "Balanca 20 metros, 6, 7 e 9 eixo (3x3)",
    "Balanca 30 metros, 6, 7 e nove eixos ate 26 metros",
    "Balanca 20 metros - somente 06 e 07 eixos",
    "Balanca 25 metros / 26 km de estrada de chao",
    "Sem restricao de balanca",
    "Balanca 20m - 6, 7 e 9 eixos",
    "Balanca 25 metros / 2,3 km de estrada de chao",
]

VEICULOS = ["Bitrem", "Rodotrem", "Truck", "Carreta LS", "Vanderleia", "Bitrem 3x3", "Romeu e Julieta"]

CLIENTES_FAKE = [
    "Agro Sul Ltda", "Cooperativa Vale do Iguacu", "Cerealista Parana Norte",
    "Grupo Cambio Agro", "Rondon Graos SA", "Cooperativa Cascavel",
    "Toledo Cereais", "Palotina Agroindustrial", "Fronteira Oeste Graos",
]

NOMES_REMETENTE = [
    "Eduardo Manini", "Carla Winter", "Jose Ricardo Faccin", "Marcia Lopes",
    "Anderson Kruger", "Patricia Zanetti",
]

MESES = {1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
         7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"}

# Janelas de atendimento plausiveis (inicio, fim) - sempre fim > inicio, dentro do horario comercial.
JANELAS_ATENDIMENTO = [
    (6, 14), (7, 15), (7, 17), (8, 17), (8, 18),
    (9, 17), (10, 19), (13, 18), (11, 17), (8, 16),
]


def rand_data_2026(mixed: bool = False) -> str:
    dia = random.randint(1, 28)
    mes = random.randint(1, 12)
    ano = 2026
    fmt = random.choice(["br", "iso", "br_dash", "extenso"]) if mixed else "br"
    if fmt == "iso":
        return f"{ano}-{mes:02d}-{dia:02d}"
    if fmt == "br_dash":
        return f"{dia:02d}-{mes:02d}-{ano}"
    if fmt == "extenso":
        return f"{dia:02d}/{MESES[mes]}/{ano}"
    return f"{dia:02d}/{mes:02d}/{ano}"


def rand_valor(min_v: float = 38, max_v: float = 230, moeda: bool = True) -> str:
    """Fretes reais tendem a fechar em valores inteiros de R$; centavos sao a excecao."""
    if random.random() < 0.65:
        valor = float(random.randint(int(min_v), int(max_v)))
    else:
        valor = round(random.uniform(min_v, max_v), 2)

    if valor == int(valor):
        txt = str(int(valor)) if random.random() < 0.6 else f"{int(valor)},00"
    elif random.random() < 0.5:
        txt = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        txt = f"{valor:.2f}"
    return f"R$ {txt}" if moeda else txt


def rand_saldo() -> str:
    """Saldos de contrato tanto aparecem como inteiro puro ("saldo 37") quanto fracionado."""
    saldo = round(random.uniform(5, 8000), 2)
    if random.random() < 0.3:
        return str(int(round(saldo)))
    if random.random() < 0.5:
        return f"{saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{saldo:.2f}"


def talvez(valor: str, prob_nulo: float = 0.08) -> str:
    return "" if random.random() < prob_nulo else valor


def com_uf(cidade: str, prob: float = 0.15) -> str:
    """As vezes a cidade vem com sufixo /UF (como no material de origem: 'Guarapuava/PR')."""
    if "/" in cidade or random.random() >= prob:
        return cidade
    return f"{cidade}/{CIDADE_UF.get(cidade, 'PR')}"


def escolhe_destino_base() -> str:
    if random.random() < 0.55:
        return "Paranagua"
    outros = [c for c in MUNICIPIOS_DESTINO if c != "Paranagua"]
    return random.choice(outros)


def sorteia_par_cidades() -> tuple[str, str]:
    """Garante que origem e destino nunca coincidam (rota de zero km nao existe na operacao)."""
    origem = random.choice(MUNICIPIOS_ORIGEM)
    destino = escolhe_destino_base()
    tentativas = 0
    while destino == origem and tentativas < 5:
        destino = escolhe_destino_base()
        tentativas += 1
    return origem, destino


def aplica_ruido_origem(cidade: str) -> str:
    if cidade in MUNICIPIOS_ORIGEM_TYPO and random.random() < 0.4:
        return random.choice(MUNICIPIOS_ORIGEM_TYPO[cidade])
    return com_uf(cidade)


def aplica_ruido_destino(cidade: str) -> str:
    if cidade in MUNICIPIOS_DESTINO_TYPO and random.random() < 0.5:
        return random.choice(MUNICIPIOS_DESTINO_TYPO[cidade])
    return com_uf(cidade)


def produto_ruidoso() -> str:
    p = random.choice(PRODUTOS)
    if p in PRODUTOS_TYPO and random.random() < 0.45:
        return random.choice(PRODUTOS_TYPO[p])
    return p


def produto_csv() -> str:
    """Na planilha consolidada o produto costuma vir limpo em Title Case (Soja/Milho)."""
    if random.random() < 0.25:
        return produto_ruidoso()
    return random.choice(["Soja", "Milho"])


def sorteia_janela() -> tuple[int, int, int]:
    inicio, fim = random.choice(JANELAS_ATENDIMENTO)
    hora_evento = random.randint(inicio, fim - 1)
    return inicio, fim, hora_evento


# ---------------------------------------------------------------------------
# 1. WHATSAPP - 80 mensagens
# ---------------------------------------------------------------------------

def gerar_whatsapp(n: int = 80) -> list[dict]:
    mensagens = []
    emojis_rota = ["🚚", "🌾", "💰"]

    templates_completos = [
        "⚠️ EMBARQUE EM OPORTUNIDADE PARA HOJE ⚠️\n"
        "🚚 Rota: {origem} x {destino}\n"
        "🌾 Produto: {produto}\n"
        "💰 Frete: {frete}\n"
        "OPORTUNIDADE PRA {n_veic} LS, SALDO {saldo} TONS\n"
        "{balanca}\n"
        "NAO ENVIAR SEM LINHA NO SHARE E SALDO\n"
        "INFORMAR PLACA E PESO DO VEICULO",

        "Embarques de {data}\n"
        "📍{origem} (FAZ. {fazenda}) x {destino} - Tarifa Final: {frete} (carregamento ate as {hora})",

        "faz {faz_num} - {origem} pra {destino}, {produto}, saldo {saldo} ton, {frete}/ton, precisa de {veiculo} {eixos} eixos",

        "bom dia! ainda tem saldo pra {origem} x {destino}?? {produto} aqui, temos {n_veic} carretas pra hj",

        "{origem} X {destino} - {produto} - emb ate {hora}h - {frete} - {balanca}",

        "pessoal, atualizando: saldo de {origem} caiu pra {saldo} ton, {produto}, mesma tarifa {frete}",

        "URGENTE!! precisamos de {n_veic} veiculos pra {origem} - {destino} ainda hoje, {produto}, {frete} o frete",

        "{motorista_placa} confirmado pra {origem} x {destino}, previsao de chegada {hora}h",

        "Caso tenham algum problema com veiculos ja autorizados, sinalizar o mais breve possivel",

        "Atencao! Para garantir o embarque, e necessario entrar em contrato para realizar o agendamento no portal",

        "galera, {origem} fechou. abriu vaga agora em {origem2} x {destino}, {produto}, {frete}, saldo {saldo}",

        "oi bom dia, qual o valor do frete {origem} - {destino}? e o saldo, quantas ton ainda tem?",

        "{produto} - {origem} pra {destino} - {balanca} - so vira com no minimo {n_veic} eixos",
    ]

    for i in range(n):
        tpl = random.choice(templates_completos)
        origem_base, destino_base = sorteia_par_cidades()
        origem = aplica_ruido_origem(origem_base)
        destino = aplica_ruido_destino(destino_base)
        origem2_base = random.choice([c for c in MUNICIPIOS_ORIGEM if c != origem_base])
        origem2 = aplica_ruido_origem(origem2_base)

        produto = produto_ruidoso()
        frete = rand_valor()
        saldo = rand_saldo()
        balanca = random.choice(BALANCA_RESTRICOES)
        veiculo = random.choice(VEICULOS)
        n_veic = random.randint(1, 6)
        eixos = random.choice(["6", "7", "9", "6 e 7", "7 e 9"])
        hora = random.choice(["17:00", "18:00", "08:00", "15:30", "19h"])
        data = rand_data_2026(mixed=True)
        fazenda = random.choice(["PEDRAS", "CAMBUCA", "NOVO HORIZONTE", "SAO JOAO", "BOA VISTA"])
        faz_num = random.randint(1, 40)
        motorista_placa = f"{random.choice(['ABC', 'BRA', 'RDX'])}{random.randint(1000, 9999)}"

        texto = tpl.format(
            origem=origem, origem2=origem2, destino=destino, produto=produto,
            frete=frete, saldo=saldo, balanca=balanca, veiculo=veiculo,
            n_veic=n_veic, eixos=eixos, hora=hora, data=data, fazenda=fazenda,
            faz_num=faz_num, motorista_placa=motorista_placa,
        )

        if random.random() < 0.12:
            texto += f" {random.choice(emojis_rota)}"
        if random.random() < 0.08:
            texto = "👍 " + texto

        mensagens.append({
            "id": i + 1,
            "timestamp": f"{rand_data_2026()} {random.randint(6,22):02d}:{random.randint(0,59):02d}",
            "remetente": random.choice(["Rodomax - Central", "Cliente Agro", "Transportador"]),
            "mensagem": texto,
        })

    return mensagens


# ---------------------------------------------------------------------------
# 2. E-MAILS COMERCIAIS - 100 textos
# ---------------------------------------------------------------------------

def gerar_linha_tabela_email(st_id: int) -> str:
    origem_base, destino_base = sorteia_par_cidades()
    origem = aplica_ruido_origem(origem_base)
    local_emb = origem if random.random() < 0.6 else aplica_ruido_origem(origem_base)
    destino = aplica_ruido_destino(destino_base)
    local_desemb = talvez(destino, prob_nulo=0.25)
    produto = produto_ruidoso()
    saldo = rand_saldo()
    valor_ton = rand_valor(moeda=random.random() < 0.7)
    return f"{st_id} | {origem} | {local_emb} | {destino} | {local_desemb} | {produto} | {saldo} | {valor_ton}"


def gerar_emails(n: int = 100) -> list[dict]:
    emails = []
    assuntos = [
        "M. Interno - Milho e Soja", "M. Interno Milho e Soja",
        "Mapa Interno - Milho/Soja", "M.Interno - Soja e Milho",
    ]
    saudacoes = ["Prezados, bom dia.", "Prezados, boa tarde.", "Bom dia a todos,", "Prezados,"]
    fechamentos = [
        "Atenciosamente,", "Att,", "Abs,", "Qualquer duvida estou a disposicao.",
    ]

    for i in range(n):
        remetente = random.choice(NOMES_REMETENTE)
        assunto = random.choice(assuntos)
        data_hora = f"{random.choice(['seg','ter','qua','qui','sex'])} {rand_data_2026(mixed=True)} {random.randint(8,18):02d}:{random.randint(0,59):02d}"
        n_linhas = random.randint(3, 8)

        st_base = random.randint(560000, 570999)
        linhas = [gerar_linha_tabela_email(st_base + j) for j in range(n_linhas)]

        header = (
            f"ENC: {random.choice(['', 'FW: ', 'RES: '])}M. Interno Milho e Soja\n"
            f"{remetente} Rodomax\n"
            f"Para: Central Rodomax\n"
            f"Assunto: {assunto}\n"
            f"{data_hora}\n"
        )
        if random.random() < 0.3:
            header += "(i) Esta mensagem foi AutoEncaminhada.\n"

        corpo = (
            f"{random.choice(saudacoes)}\n\n"
            f"Seguem embarques em andamento, marcacoes via portal.\n\n"
            f"ST/Codigo | Municipio Embarque | Local Embarque | Municipio Destino | Local Desembarque | Produto | Saldo | R$/TON\n"
            + "\n".join(linhas)
        )

        assinatura = f"\n\n{random.choice(fechamentos)}\n{remetente}\nRodomax Transportes"

        texto_email = header + "\n" + corpo + assinatura
        emails.append({"id": i + 1, "email_texto": texto_email})

    return emails


# ---------------------------------------------------------------------------
# 3. WEBHOOKS / API - 10 estruturas JSON
# ---------------------------------------------------------------------------

def gerar_webhooks(n: int = 10) -> list[dict]:
    registros = []
    status_opcoes = ["AGENDADO", "PENDENTE", "CONFIRMADO", "CANCELADO"]

    for _ in range(n):
        origem_term = random.choice(TERMINAIS)
        pool_destino = [t for t in TERMINAIS + MUNICIPIOS_DESTINO if t != origem_term]
        destino_term = random.choice(pool_destino)
        inicio, fim, hora_evento = sorteia_janela()

        registro = {
            "id_agendamento": 23000 + random.randint(1, 999),
            "data_hora": f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{hora_evento:02d}:00:00-03:00",
            "codigo_rodo": f"RODO {random.randint(23000, 23999)}",
            "ponto_origem": origem_term,
            "ponto_destino": destino_term if random.random() > 0.1 else None,
            "produto": produto_ruidoso(),
            "volume_ton": round(random.uniform(3, 250), 1),
            "janela_atendimento": f"{inicio:02d}:00-{fim:02d}:00",
            "status": random.choice(status_opcoes),
        }
        if random.random() < 0.2:
            registro["volume_ton"] = str(registro["volume_ton"]).replace(".", ",")
        registros.append(registro)

    return registros


# ---------------------------------------------------------------------------
# 4. CSV / TABULAR
# ---------------------------------------------------------------------------

def gerar_csv(n: int = 150) -> str:
    status_opcoes = ["Ativo", "Cotas atendidas em D+1", "Prioridade", "Inativo", "Ativo "]
    cabecalho = (
        "Status,Cliente,Produto,Cidade Carga,Destino,Local carga,Local descarga,"
        "Frete Empresa,Frete Moto 10%,Frete Moto 8% PJ,Observacao,Data_Agendamento"
    )
    linhas = [cabecalho]

    for _ in range(n):
        status = random.choice(status_opcoes)
        # Na planilha real a coluna Cliente quase nunca vem preenchida na origem -
        # a associacao so acontece depois, na etapa de "Juncoes Logicas com o CRM".
        cliente = talvez(random.choice(CLIENTES_FAKE), prob_nulo=0.55)
        produto = produto_csv()

        cidade_carga_base, destino_base = sorteia_par_cidades()
        cidade_carga = aplica_ruido_origem(cidade_carga_base)
        destino = aplica_ruido_destino(destino_base)

        # "Local carga" fica vazio na quase totalidade dos registros da planilha real.
        local_carga = talvez(cidade_carga, prob_nulo=0.8)
        # "Local descarga" normalmente repete o destino (ex.: Paranagua), com poucas lacunas.
        local_descarga = talvez(destino, prob_nulo=0.2)

        frete_base = round(random.uniform(70, 230), 2)
        usa_virgula = random.random() < 0.5

        def fmt_valor(v: float) -> str:
            if random.random() < 0.55:
                return str(int(round(v)))
            if usa_virgula:
                return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{v:.2f}"

        frete_empresa = talvez(fmt_valor(frete_base), prob_nulo=0.1)
        frete_moto_10 = talvez(fmt_valor(round(frete_base * 0.83, 2)), prob_nulo=0.15)
        frete_moto_8pj = talvez(fmt_valor(round(frete_base * 0.85, 2)), prob_nulo=0.15)

        observacao = talvez(random.choice(BALANCA_RESTRICOES), prob_nulo=0.2)
        data_agendamento = talvez(rand_data_2026(mixed=True), prob_nulo=0.25)

        campos = [
            status, cliente, produto, cidade_carga, destino, local_carga,
            local_descarga, frete_empresa, frete_moto_10, frete_moto_8pj,
            observacao, data_agendamento,
        ]
        campos_csv = [f'"{c}"' if "," in c else c for c in campos]
        linhas.append(",".join(campos_csv))

    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Escrita dos arquivos de saida
# ---------------------------------------------------------------------------

def main() -> None:
    whatsapp = gerar_whatsapp(80)
    with open(OUT_DIR / "01_whatsapp_mensagens.txt", "w", encoding="utf-8") as f:
        for m in whatsapp:
            f.write(f"--- Mensagem {m['id']} | {m['timestamp']} | {m['remetente']} ---\n")
            f.write(m["mensagem"] + "\n\n")

    emails = gerar_emails(100)
    with open(OUT_DIR / "02_emails_comerciais.txt", "w", encoding="utf-8") as f:
        for e in emails:
            f.write(f"===== EMAIL {e['id']:03d} =====\n")
            f.write(e["email_texto"] + "\n\n")

    webhooks = gerar_webhooks(10)
    with open(OUT_DIR / "03_webhooks_api.json", "w", encoding="utf-8") as f:
        json.dump(webhooks, f, ensure_ascii=False, indent=2)

    csv_texto = gerar_csv(150)
    with open(OUT_DIR / "04_exportacao_csv.csv", "w", encoding="utf-8") as f:
        f.write(csv_texto)

    print("Arquivos gerados em:", OUT_DIR)
    print(" - 01_whatsapp_mensagens.txt (80 mensagens)")
    print(" - 02_emails_comerciais.txt (100 e-mails)")
    print(" - 03_webhooks_api.json (10 registros)")
    print(" - 04_exportacao_csv.csv (150 linhas + cabecalho)")


if __name__ == "__main__":
    main()
