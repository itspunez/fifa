"""
Message formatter — bilingual FA/EN for the World Cup Telegram channel.
"""

GOAL_TYPE_FA = {
    "REGULAR": "⚽",
    "OWN": "🥅 (گل به خودی / Own Goal)",
    "PENALTY": "🎯 (پنالتی / Penalty)",
}


def _score_line(h: int, a: int) -> str:
    return f"<b>{h} – {a}</b>"


def format_match_start(home_short: str, away_short: str,
                        home_full: str, away_full: str) -> str:
    return (
        f"🟢 <b>بازی شروع شد! / Match Started!</b>\n\n"
        f"🏳️ {home_short} <b>vs</b> {away_short} 🏳️\n"
        f"<i>{home_full} vs {away_full}</i>\n\n"
        f"🏆 FIFA World Cup 2026\n"
        f"⏱ نود دقیقه پیش روست — Let's go! 🔥"
    )


def format_halftime(home_short: str, away_short: str,
                     home_goals: int, away_goals: int) -> str:
    score = _score_line(home_goals, away_goals)
    return (
        f"⏸ <b>سوت پایان نیمه اول / Half-Time</b>\n\n"
        f"🏳️ {home_short} {score} {away_short} 🏳️\n\n"
        f"نیمه دوم به زودی شروع میشه ⚽\n"
        f"Second half coming up!"
    )


def format_event(event_type: str,
                  home_short: str, away_short: str,
                  home_goals: int, away_goals: int,
                  scorer: dict | None = None,
                  team: str = "home") -> str:

    if event_type == "goal":
        emoji = GOAL_TYPE_FA.get(scorer.get("type", "REGULAR") if scorer else "REGULAR", "⚽")
        minute = f"{scorer['minute']}'" if scorer and scorer.get("minute") else ""
        name = scorer.get("name", "نامشخص / Unknown") if scorer else "نامشخص / Unknown"
        goal_type_label = GOAL_TYPE_FA.get(scorer.get("type", "REGULAR") if scorer else "REGULAR", "⚽")
        score = _score_line(home_goals, away_goals)

        team_label = home_short if team == "home" else away_short

        return (
            f"{emoji} <b>گول! / GOAL!</b>\n\n"
            f"🏳️ {home_short} {score} {away_short} 🏳️\n\n"
            f"⚽ زننده: <b>{name}</b> — {team_label} {minute}\n"
            f"⚽ Scorer: <b>{name}</b> — {team_label} {minute}\n"
            f"{goal_type_label if scorer and scorer.get('type') != 'REGULAR' else ''}"
        ).strip()

    return ""


def format_yellow_card(home_short: str, away_short: str,
                        player: str, team: str, minute: str) -> str:
    return (
        f"🟨 <b>کارت زرد / Yellow Card</b>\n\n"
        f"👤 <b>{player}</b> — {team}\n"
        f"⏱ دقیقه {minute}' | Minute {minute}'\n\n"
        f"{home_short} vs {away_short}"
    )


def format_red_card(home_short: str, away_short: str,
                     player: str, team: str, minute: str) -> str:
    return (
        f"🟥 <b>کارت قرمز! / Red Card!</b>\n\n"
        f"👤 <b>{player}</b> — {team}\n"
        f"⏱ دقیقه {minute}' | Minute {minute}'\n\n"
        f"{home_short} vs {away_short}"
    )


def format_match_end(home_short: str, away_short: str,
                      home_full: str, away_full: str,
                      home_goals: int, away_goals: int) -> str:
    score = _score_line(home_goals, away_goals)

    if home_goals > away_goals:
        result_fa = f"🏆 برنده: {home_short}"
        result_en = f"🏆 Winner: {home_short}"
    elif away_goals > home_goals:
        result_fa = f"🏆 برنده: {away_short}"
        result_en = f"🏆 Winner: {away_short}"
    else:
        result_fa = "🤝 مساوی"
        result_en = "🤝 Draw"

    return (
        f"🔴 <b>سوت پایان / Full-Time</b>\n\n"
        f"🏳️ {home_short} {score} {away_short} 🏳️\n"
        f"<i>{home_full} vs {away_full}</i>\n\n"
        f"{result_fa}\n"
        f"{result_en}\n\n"
        f"🏆 FIFA World Cup 2026"
    )
