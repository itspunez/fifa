import asyncio
import logging
import aiohttp
from datetime import datetime, timezone
from formatter import format_event, format_match_start, format_match_end, format_halftime

logger = logging.getLogger(__name__)

BASE_URL = "https://api.football-data.org/v4"
WC_2026_ID = 2000  # football-data.org competition ID for FIFA World Cup

POLL_INTERVAL = 60  # seconds between polls


class MatchMonitor:
    def __init__(self, api_key: str, bot, channel_id: str):
        self.api_key = api_key
        self.bot = bot
        self.channel_id = channel_id
        self.headers = {"X-Auth-Token": api_key}

        # State tracking per match
        # { match_id: { "score": {...}, "status": str, "events": set() } }
        self.state: dict = {}

    async def run(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            self.session = session
            while True:
                try:
                    await self.poll()
                except Exception as e:
                    logger.error(f"Poll error: {e}")
                await asyncio.sleep(POLL_INTERVAL)

    async def poll(self):
        # Fetch today's live + scheduled matches for World Cup
        url = f"{BASE_URL}/competitions/{WC_2026_ID}/matches"
        params = {"status": "LIVE,IN_PLAY,PAUSED"}

        async with self.session.get(url, params=params) as resp:
            if resp.status != 200:
                logger.warning(f"API returned {resp.status}")
                return
            data = await resp.json()

        matches = data.get("matches", [])
        logger.info(f"Live matches found: {len(matches)}")

        for match in matches:
            await self.process_match(match)

    async def process_match(self, match: dict):
        mid = match["id"]
        status = match["status"]
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        home_short = match["homeTeam"].get("shortName") or home
        away_short = match["awayTeam"].get("shortName") or away
        score = match["score"]
        full_score = score.get("fullTime", {})
        half_score = score.get("halfTime", {})

        home_goals = full_score.get("home") or 0
        away_goals = full_score.get("away") or 0

        prev = self.state.get(mid)

        # ── NEW MATCH: first time we see it ──
        if prev is None:
            self.state[mid] = {
                "status": status,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "events": set(),
                "halftime_sent": False,
            }
            if status in ("IN_PLAY", "LIVE"):
                msg = format_match_start(home_short, away_short, home, away)
                await self.send(msg)
            return

        # ── HALFTIME ──
        if status == "PAUSED" and not prev.get("halftime_sent"):
            self.state[mid]["halftime_sent"] = True
            msg = format_halftime(home_short, away_short, home_goals, away_goals)
            await self.send(msg)

        # ── GOALS ──
        prev_home = prev["home_goals"]
        prev_away = prev["away_goals"]

        if home_goals > prev_home:
            for _ in range(home_goals - prev_home):
                scorer = await self.get_last_scorer(mid, "HOME_TEAM")
                msg = format_event("goal", home_short, away_short, home_goals, away_goals, scorer)
                await self.send(msg)

        if away_goals > prev_away:
            for _ in range(away_goals - prev_away):
                scorer = await self.get_last_scorer(mid, "AWAY_TEAM")
                msg = format_event("goal", home_short, away_short, home_goals, away_goals, scorer, team="away")
                await self.send(msg)

        # ── MATCH ENDED ──
        if status == "FINISHED" and prev["status"] != "FINISHED":
            msg = format_match_end(home_short, away_short, home, away, home_goals, away_goals)
            await self.send(msg)

        # Update state
        self.state[mid].update({
            "status": status,
            "home_goals": home_goals,
            "away_goals": away_goals,
        })

    async def get_last_scorer(self, match_id: int, team_side: str) -> dict | None:
        """Fetch match detail to get last goal scorer info."""
        url = f"{BASE_URL}/matches/{match_id}"
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
            goals = data.get("goals", [])
            # Filter by team side and get the last goal
            team_goals = [g for g in goals if g.get("team", {}).get("id") and
                          self._is_team_side(g, team_side, data)]
            if team_goals:
                last = team_goals[-1]
                return {
                    "name": last.get("scorer", {}).get("name", ""),
                    "minute": last.get("minute", ""),
                    "type": last.get("type", "REGULAR"),
                }
        except Exception as e:
            logger.error(f"Scorer fetch error: {e}")
        return None

    def _is_team_side(self, goal: dict, side: str, match_data: dict) -> bool:
        goal_team_id = goal.get("team", {}).get("id")
        if side == "HOME_TEAM":
            return goal_team_id == match_data["homeTeam"]["id"]
        return goal_team_id == match_data["awayTeam"]["id"]

    async def send(self, text: str):
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=text,
                parse_mode="HTML",
            )
            logger.info(f"Sent: {text[:60]}...")
        except Exception as e:
            logger.error(f"Send error: {e}")
