from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup


SOLOBOOM_URL = "https://soloboom.net/leaderboard"


# -------------------------------------------------------------------------
# MODELO DE DADOS
# -------------------------------------------------------------------------
@dataclass
class Player:
    position: int
    nickname: str          # ex: Faker
    summoner_name: str     # ex: Faker#SB5
    region: str            # ex: BR Pro
    wins: int
    losses: int
    winrate: float         # 75.7
    rank: str              # ex: MASTER I
    lp: int                # 681
    live: bool
    twitch_url: Optional[str]
    opgg_url: Optional[str]

    def format_for_chat(self) -> str:
        wl = f"{self.wins}/{self.losses}"

        # EXATO: aqui incluímos o summoner name logo após o nickname
        msg = (
            f"{self.nickname} ({self.summoner_name}) está em {self.position}º no SoloBoom ({self.region}) "
            f"– {wl} ({self.winrate:.1f}%) – {self.rank} – {self.lp} LP"
        )

        return msg


# -------------------------------------------------------------------------
# SCRAPING
# -------------------------------------------------------------------------
async def fetch_leaderboard_html(url: str = SOLOBOOM_URL) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (SoloBoomRankBot)"}
        )
        resp.raise_for_status()
        return resp.text


def parse_leaderboard(html: str) -> List[Player]:
    soup = BeautifulSoup(html, "html.parser")
    players: List[Player] = []

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 12:
            continue

        try:
            position = int(tds[0].get_text(strip=True))
        except ValueError:
            continue

        nickname = tds[2].get_text(strip=True)
        summoner_name = tds[3].get_text(strip=True)
        region = tds[4].get_text(strip=True)

        # Coluna 'En Vivo' / 'Off'
        status_td = tds[5]
        status_text = status_td.get_text(strip=True).lower()
        live = "en vivo" in status_text or "live" in status_text
        twitch_a = status_td.find("a")
        twitch_url = twitch_a["href"] if twitch_a and twitch_a.has_attr("href") else None

        # W/L – ex: "81 / 26"
        wins, losses = _parse_wins_losses(tds[7].get_text(strip=True))

        # Winrate – ex: "75.7%"
        winrate = _parse_winrate(tds[8].get_text(strip=True))

        # Rank + LP
        rank_str = tds[9].get_text(" ", strip=True)
        lp = _parse_lp(tds[10].get_text(strip=True))

        # OP.GG
        opgg_a = tds[11].find("a")
        opgg_url = opgg_a["href"] if opgg_a and opgg_a.has_attr("href") else None

        players.append(
            Player(
                position=position,
                nickname=nickname,
                summoner_name=summoner_name,
                region=region,
                wins=wins,
                losses=losses,
                winrate=winrate,
                rank=rank_str,
                lp=lp,
                live=live,
                twitch_url=twitch_url,
                opgg_url=opgg_url,
            )
        )

    return players


# -------------------------------------------------------------------------
# BUSCA INTELIGENTE: CASE-INSENSITIVE E PARCIAL
# -------------------------------------------------------------------------
def find_player(players: List[Player], query: str) -> Optional[Player]:
    """
    Busca dinâmica por nick:
      - case-insensitive (lower())
      - busca parcial (ex: 'master', 'kirito')
      - se mais de um, retorna o melhor colocado
    """
    q = query.strip().lower()
    if not q:
        return None

    # 1) match exato
    exact = [p for p in players if p.nickname.lower() == q]
    if exact:
        return exact[0]

    # 2) match parcial
    partial = [p for p in players if q in p.nickname.lower()]
    if partial:
        return sorted(partial, key=lambda p: p.position)[0]

    return None


async def get_player_message(nick: str) -> str:
    html = await fetch_leaderboard_html()
    players = parse_leaderboard(html)
    player = find_player(players, nick)

    if not player:
        return f"{nick}: não encontrado na tabela do SoloBoom."
    
    return player.format_for_chat()


# -------------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------------
def _parse_wins_losses(text: str) -> tuple[int, int]:
    try:
        parts = text.replace(" ", "").split("/")
        return int(parts[0]), int(parts[1])
    except Exception:
        return 0, 0


def _parse_winrate(text: str) -> float:
    try:
        return float(text.replace("%", "").replace(",", ".").strip())
    except Exception:
        return 0.0


def _parse_lp(text: str) -> int:
    try:
        return int(text.split()[0])
    except Exception:
        return 0


# -------------------------------------------------------------------------
# CLI PARA RODAR NO TERMINAL (LOCAL TEST) 🎯
# -------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import asyncio
    import json

    parser = argparse.ArgumentParser(
        description="Consulta o leaderboard do SoloBoom e mostra o rank de um nick."
    )
    parser.add_argument("nick", help="Nick a procurar (ex: Master_yi_doente)")
    parser.add_argument("--json", action="store_true", help="Output em JSON")

    args = parser.parse_args()

    async def main():
        html = await fetch_leaderboard_html()
        players = parse_leaderboard(html)
        player = find_player(players, args.nick)

        if not player:
            print(f"{args.nick}: não encontrado na tabela do SoloBoom.")
            return

        if args.json:
            print(json.dumps(asdict(player), ensure_ascii=False))
        else:
            print(player.format_for_chat())

    asyncio.run(main())