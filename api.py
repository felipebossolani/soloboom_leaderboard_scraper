from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse

from soloboom_rank import get_player_message

app = FastAPI(
    title="SoloBoom Rank API",
    description="API simples para consultar o rank de jogadores no SoloBoom.",
    version="0.1.0",
)


@app.get("/rank", response_class=PlainTextResponse)
async def rank(
    nick: str = Query(..., description="Nick a procurar no SoloBoom (ex: Faker)")
):
    """
    Exemplo:
      GET /rank?nick=Faker
    Retorna uma string pronta para ser usada em chat (Twitch, Discord, etc.).
    """
    return await get_player_message(nick)


# Execução direta: python api.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )