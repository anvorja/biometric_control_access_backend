# Biometric control access


python3 -m venv .venv

source .venv/bin/activate

pip install -r requeriments.txt 

alembic init alembic

alembic revision --autogenerate -m "Creacion de tablas"

alembic upgrade head

si hay algún script de carga de datos se ejecuta…. python -m app.db.seed-script
ó  
python -m app.db.test-data-generator

uvicorn app.main:app --reload