# SoloBoom Leaderboard Scraper

Script que faz web scraping do leaderboard do site `soloboom.net` e retorna uma mensagem resumida com os dados de um jogador específico.  
Pode ser usado via CLI, via API ou integrado com Twitch (Nightbot ou StreamElements).

---

## 1. Requisitos

Python 3.10+ instalado.

Crie e ative o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate      # mac/linux
# venv\Scripts\activate       # windows
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## 2. Uso local (CLI)

```bash
python soloboom.py "faker"
python soloboom.py faker
python soloboom.py faker --json
```

---

## 3. Subir API localmente

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Teste no navegador:
```
http://127.0.0.1:8000/rank?nick=Faker
```

Ou via terminal:
```bash
curl "http://127.0.0.1:8000/rank?nick=faker"
```

---

## 4. Deploy no Railway

1. Suba o projeto no GitHub.
2. Acesse: https://railway.app/
3. New Project → Deploy from GitHub Repo.
4. Após o build, vá em **Settings > Start Command** e configure:
```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```
5. Teste com a URL gerada:
```
https://SEU-NOME.up.railway.app/rank?nick=faker
```

---

## 5. Comando na Twitch

### **Nightbot**
Acesse: https://nightbot.tv/

**Command:**
```
!rank
```
**Message:**
```text
$(urlfetch https://SEU-NOME.up.railway.app/rank?nick=$(querystring))
```

Exemplos:
```
!rank faker
!rank yi
!rank kirito
```

---

### **StreamElements**
Acesse: https://streamelements.com/

**Command:**
```
!rank
```
**Response:**
```text
${urlfetch https://SEU-NOME.up.railway.app/rank?nick=${1}}
```

**Com nick padrão (opcional):**
```text
${urlfetch https://SEU-NOME.up.railway.app/rank?nick=${1|Faker}}
```

---

## Estrutura do projeto

```
soloboom.py          # lógica principal + CLI
api.py               # endpoint FastAPI
requirements.txt
Procfile
.gitignore
README.md
```

---

Projeto pronto para uso local, deploy e integração com Twitch.
