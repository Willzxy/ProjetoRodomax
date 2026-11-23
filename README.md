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
   ```
2. Execute o simulador para ler os arquivos de `dados/brutos/`, normalizar os registros e gerar a base unificada (`dados/saida/rodomax_demandas.csv` e `.xlsx`):
   ```bash
   python simulador.py
   ```
3. Execute o treinamento do modelo de Inteligência Artificial para exibir as métricas no terminal e salvar o arquivo `dados/saida/modelo_classificacao.joblib`:
   ```bash
   python src/ia/treinar_modelo.py
   ```
4. *(Opcional)* Teste uma previsão isolada diretamente no terminal antes de abrir a interface web:
   ```bash
   python src/ia/preditor.py
   ```

### 3. Iniciando o Dashboard Local

Pelo terminal, na pasta raiz do projeto, inicie a aplicação web do Streamlit para visualizar os indicadores da operação e simular novas demandas em tempo real:

```bash
streamlit run src/dashboard/app.py
```

---

## Como Reiniciar o Projeto

Para apagar os arquivos gerados durante os testes e executar todo o fluxo novamente do zero (mantendo intactos os arquivos originais em `dados/brutos/`):

1. Execute o script de limpeza na pasta raiz para esvaziar `dados/entrada/` e `dados/saida/`:
   ```bash
   python resetar.py
   ```
2. Rode novamente o pipeline completo na ordem:
   ```bash
   python simulador.py
   python src/ia/treinar_modelo.py
   streamlit run src/dashboard/app.py
   ```

---

## Como Customizar o Projeto

- **Adicionar novas fontes de dados:** Insira novos arquivos `.txt` (WhatsApp ou e-mail), `.json` (Webhooks/API) ou `.csv` na pasta `dados/brutos/` e execute `python simulador.py`.
- **Ajustar regras de extração de texto:** Edite as expressões regulares (Regex) e mapeamentos de campos nos arquivos dentro de `src/normalizadores/` (`padronizar_txt.py`, `padronizar_json.py` e `padronizar_csv.py`) para adaptar ao formato específico de novos documentos.
- **Alterar colunas da planilha unificada:** Modifique os atributos da classe `DemandaPadronizada` em `src/ingestao/schema.py` caso precise incluir ou remover campos na exportação final.
- **Ajustar o modelo de classificação:** No arquivo `src/ia/treinar_modelo.py`, altere a profundidade da árvore (`max_depth`), a divisão de treino/teste (`test_size`) ou substitua o `DecisionTreeClassifier` por outro classificador do Scikit-Learn (como `RandomForestClassifier`, `KNeighborsClassifier` ou `SVC`).
- **Personalizar o dashboard:** Edite `src/dashboard/app.py` para adicionar novos cartões de métricas, filtros laterais ou gráficos interativos com Plotly.
