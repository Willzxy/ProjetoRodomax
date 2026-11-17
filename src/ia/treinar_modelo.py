from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parents[2]
CAMINHO_CSV = BASE_DIR / "dados" / "saida" / "rodomax_demandas.csv"
CAMINHO_MODELO = BASE_DIR / "dados" / "saida" / "modelo_classificacao.joblib"

df = pd.read_csv(CAMINHO_CSV)

colunas_numericas = ["peso_kg", "distancia_km", "valor_frete"]
colunas_categoricas = ["produto", "origem", "destino", "canal_origem"]
coluna_alvo = "atendida"

df = df.dropna(subset=colunas_numericas + colunas_categoricas + [coluna_alvo])

X = df[colunas_numericas + colunas_categoricas]
y = df[coluna_alvo]

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X, y, test_size=0.2, random_state=42
)

preprocessador = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), colunas_categoricas),
        ("num", "passthrough", colunas_numericas),
    ]
)

baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_treino, y_treino)
pred_baseline = baseline.predict(X_teste)

modelo = Pipeline(
    steps=[
        ("preprocessamento", preprocessador),
        ("classificador", DecisionTreeClassifier(max_depth=5, random_state=42)),
    ]
)

modelo.fit(X_treino, y_treino)
pred_modelo = modelo.predict(X_teste)

acc_base = accuracy_score(y_teste, pred_baseline)
acc_modelo = accuracy_score(y_teste, pred_modelo)
matriz = confusion_matrix(y_teste, pred_modelo)

print(f"Acuracia Linha de Base (Classe Mais Comum): {acc_base:.2%}")
print(f"Acuracia Arvore de Decisao: {acc_modelo:.2%}")
print("Matriz de Confusao:")
print(matriz)

CAMINHO_MODELO.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(modelo, CAMINHO_MODELO)
print(f"Modelo salvo em: {CAMINHO_MODELO}")