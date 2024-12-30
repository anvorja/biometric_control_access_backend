# Biometric control access

python3 -m venv .venv

source .venv/bin/activate

pip install -r requeriments.txt 

.env en [drive](https://drive.google.com/drive/folders/1p4tAIsf14WVmowL-IwcBU3StA_897baN?usp=drive_link)

(copiar env.py de alembic por fuera )

(eliminar carpeta alembic y  alembic.ini)

alembic init alembic

(copiar env.py en la nueva carpeta generada de alembic)

alembic revision --autogenerate -m "Creacion de modelos y sus tablas"

alembic upgrade head

si hay algún script de carga de datos se ejecuta…. python -m app.db.seed_script
también está para el historial:  
python -m app.db.test-data-generator

uvicorn app.main:app --reload