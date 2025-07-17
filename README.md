# VS Code Web

pyenv install 3.11.9
cd your-project-folder
pyenv local 3.11.9

rm -rf .venv
python -m venv .venv
python3.11 -m venv .venv

source .venv/bin/activate

deactivate
pip install -r requirements.txt
uvicorn app.legend_agent:app --reload --port 8000
uvicorn app.main:app --reload --port 8000

lsof -i :7071

func azure functionapp publish scale-detector-func --python
