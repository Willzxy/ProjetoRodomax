# Rodomax Hub Integrador de Dados

Sistema para ingestão, limpeza e padronização de demandas de transporte recebidas por múltiplos canais (WhatsApp, e-mail, API e planilhas CSV), aplicando Inteligência Artificial para prever o atendimento das cargas e exibindo indicadores operacionais em um dashboard interativo.

> **Projeto Universitário** desenvolvido para a disciplina de **Data Science e Inteligência Artificial** (Tecnologia em Análise e Desenvolvimento de Sistemas).

---

## Tecnologias Utilizadas

- **Back-end e Pipeline de Dados:** Python 3 (arquitetura modular com ingestão, roteamento e normalizadores)
- **Manipulação e Exportação de Dados:** Pandas e OpenPyXL
- **Inteligência Artificial:** Scikit-Learn (Árvore de Decisão) e Joblib
- **Front-end / Dashboard:** Streamlit e Plotly

---

## Como Executar o Projeto

### 1. Pré-requisitos

- Python 3.10 ou superior instalado
- Gerenciador de pacotes `pip` habilitado

### 2. Instalação e Preparação da Base de Dados

1. Na pasta raiz do projeto, instale as dependências listadas no arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
