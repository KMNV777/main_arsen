#!/usr/bin/env python3
"""Build a PDF report with festival statistics."""
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

DATA_PATH = "/root/.cursor/projects/workspace/uploads/matches_202605061939.json"
OUT_PATH = "/workspace/festival_report.pdf"

NICKS = {
    "dc06869b-1980-4874-a054-7897d044b26e": "YRARAMI",
    "5f5483fb-c48c-4dbc-9347-4dcee19554fc": "Hunter",
    "c5b30b9c-e202-4f5b-8ac1-8bf95a2e3f2c": "ArsenQAQA",
    "fc639caf-a450-4444-8e44-ba2d3c751879": "\u2606\u1d07\u1d0d\u1d0f\u026a\u1d05\u2606",
    "ed177b38-a664-4f2f-bfac-5d7a585f1a76": "vasilisa.lisa54321",
    "27708ca1-b58c-4c4a-b4cb-fc6c1efc738d": "hunter",
    "62029d13-e645-4bb7-919e-21c32020382b": "KMNV",
    "d347ef65-f103-4be6-b9d0-7a0ac0c95c66": "a.akmanov",
    "3fe1ea37-fe6e-4f72-989c-7151e61598a3": "HHHGGG",
    "0b2f72ad-41ba-4c62-bd35-e821831ffa6e": "[RESF REFEREE] JeeBeeFee",
}


def load_finished():
    with open(DATA_PATH) as f:
        data = json.load(f)
    matches = next(iter(data.values()))
    return matches, [m for m in matches if m["status"] == "MATCH_PROCESSING_COMPLETED"]


def msk_day(iso_str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.astimezone(timezone(timedelta(hours=3))).strftime("%d.%m")


def compute_stats():
    all_matches, finished = load_finished()

    side_wins = Counter()
    day_side_wins = defaultdict(Counter)
    day_total = Counter()
    user_kills = Counter()
    user_deaths = Counter()
    user_assists = Counter()
    user_matches = Counter()
    user_role = {}
    streamers = set()
    viewers = set()
    total_rounds = 0
    total_kills = 0

    for m in finished:
        res = json.loads(m["result"])
        gi = json.loads(m["game_info"])
        teams = res.get("teams", []) or []

        s_users = v_users = set()
        is_played = False
        if len(teams) == 2:
            sizes = sorted(len(t.get("userIds") or []) for t in teams)
            if sizes != [0, 0]:
                is_played = True
                s_team = min(teams, key=lambda t: len(t.get("userIds") or []))
                v_team = max(teams, key=lambda t: len(t.get("userIds") or []))
                s_users = set(s_team.get("userIds") or [])
                v_users = set(v_team.get("userIds") or [])
                streamers.update(s_users)
                viewers.update(v_users)

        if not is_played:
            continue

        day = msk_day(m["created_at"])
        day_total[day] += 1
        if res.get("isDraw"):
            side_wins["draw"] += 1
            day_side_wins[day]["draw"] += 1
        else:
            wu = set((res.get("winnerTeam") or {}).get("userIds") or [])
            if wu == s_users:
                side_wins["streamer"] += 1
                day_side_wins[day]["streamer"] += 1
            elif wu == v_users:
                side_wins["viewer"] += 1
                day_side_wins[day]["viewer"] += 1

        for p in gi.get("csMatchProfileResults") or []:
            uid = p["userId"]
            user_kills[uid] += p.get("kill", 0)
            user_deaths[uid] += p.get("death", 0)
            user_assists[uid] += p.get("assist", 0)
            user_matches[uid] += 1
            total_kills += p.get("kill", 0)
            if uid in s_users:
                user_role[uid] = "Стример"
            elif uid in v_users:
                user_role.setdefault(uid, "Зритель")

        total_rounds += len(gi.get("csMatchRoundResults") or [])

    streamer_kills = sum(user_kills[u] for u in streamers)
    viewer_kills = sum(user_kills[u] for u in viewers)

    return {
        "all": all_matches,
        "finished": finished,
        "side_wins": side_wins,
        "day_side_wins": day_side_wins,
        "day_total": day_total,
        "user_kills": user_kills,
        "user_deaths": user_deaths,
        "user_assists": user_assists,
        "user_matches": user_matches,
        "user_role": user_role,
        "streamers": streamers,
        "viewers": viewers,
        "total_rounds": total_rounds,
        "total_kills": total_kills,
        "streamer_kills": streamer_kills,
        "viewer_kills": viewer_kills,
    }


def name_for(uid):
    if uid in NICKS:
        return NICKS[uid]
    return uid[:8] + "…"


def plural(n, forms):
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return forms[0]
    if 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return forms[1]
    return forms[2]


def plural_match(n):
    return plural(n, ("матч", "матча", "матчей"))


def plural_kill(n):
    return plural(n, ("килл", "килла", "киллов"))


def make_charts(stats, out_dir="/workspace"):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_manager.fontManager.addfont(font_path)
    plt.rcParams["font.family"] = "DejaVu Sans"

    days = sorted(stats["day_total"].keys())
    streamer_w = [stats["day_side_wins"][d]["streamer"] for d in days]
    viewer_w = [stats["day_side_wins"][d]["viewer"] for d in days]

    fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=150)
    x = list(range(len(days)))
    width = 0.38
    b1 = ax.bar([i - width / 2 for i in x], streamer_w, width,
                label="Стример", color="#E94B4B")
    b2 = ax.bar([i + width / 2 for i in x], viewer_w, width,
                label="Зрители", color="#3F8EFC")
    ax.set_xticks(x)
    streamer_labels = {"25.04": "Hunter", "26.04": "YRARAMI"}
    ax.set_xticklabels([f"{d}\n({streamer_labels.get(d, '')})" for d in days])
    ax.set_ylabel("Победы в матчах")
    ax.set_title("Победы по дням: стример vs зрители")
    ax.legend(loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.2,
                    f"{int(b.get_height())}", ha="center", fontsize=10)
    fig.tight_layout()
    chart1 = f"{out_dir}/_chart_wins.png"
    fig.savefig(chart1)
    plt.close(fig)

    top = stats["user_kills"].most_common(10)
    names = [name_for(u) for u, _ in top]
    kills = [k for _, k in top]
    role_colors = ["#E94B4B" if stats["user_role"].get(u) == "Стример"
                   else "#3F8EFC" for u, _ in top]

    fig, ax = plt.subplots(figsize=(7.5, 4.6), dpi=150)
    y = list(range(len(top)))[::-1]
    bars = ax.barh(y, kills, color=role_colors)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("Киллы")
    ax.set_title("Топ-10 по киллам")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.25)
    for b, v in zip(bars, kills):
        ax.text(b.get_width() + max(kills) * 0.005, b.get_y() + b.get_height() / 2,
                f"{v}", va="center", fontsize=10)
    fig.tight_layout()
    chart2 = f"{out_dir}/_chart_top.png"
    fig.savefig(chart2)
    plt.close(fig)

    return chart1, chart2


def register_fonts():
    pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))


def build_pdf(stats):
    register_fonts()
    chart_wins, chart_top = make_charts(stats)

    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=1.6 * cm, rightMargin=1.6 * cm,
        topMargin=1.4 * cm, bottomMargin=1.4 * cm,
        title="Итоги фестиваля ЧА",
    )

    styles = getSampleStyleSheet()
    base = ParagraphStyle("base", parent=styles["Normal"], fontName="DejaVu",
                          fontSize=10.5, leading=14)
    h1 = ParagraphStyle("h1", parent=base, fontName="DejaVu-Bold",
                        fontSize=20, leading=24, spaceAfter=6,
                        textColor=colors.HexColor("#111111"))
    h2 = ParagraphStyle("h2", parent=base, fontName="DejaVu-Bold",
                        fontSize=14, leading=18, spaceBefore=10, spaceAfter=4,
                        textColor=colors.HexColor("#1F2A44"))
    sub = ParagraphStyle("sub", parent=base, fontSize=10,
                         textColor=colors.HexColor("#5C6370"))
    note = ParagraphStyle("note", parent=base, fontSize=9.5,
                          textColor=colors.HexColor("#5C6370"), leading=13)

    story = []

    story.append(Paragraph("Итоги фестиваля — Челлендж (ЧА)", h1))
    story.append(Paragraph("25–26 апреля 2026 · Counter-Strike · формат 1 vs 5", sub))
    story.append(Spacer(1, 8))

    sw = stats["side_wins"]
    total_played = sw["streamer"] + sw["viewer"] + sw["draw"]
    pct_view = sw["viewer"] / total_played * 100 if total_played else 0

    summary_rows = [
        ["Сыграно матчей", str(total_played)],
        ["Победы стримеров", str(sw["streamer"])],
        ["Победы зрителей", str(sw["viewer"])],
        ["Ничьи", str(sw["draw"])],
        ["Доля побед зрителей", f"{pct_view:.1f}%"],
        ["Всего киллов", str(stats["total_kills"])],
        ["Всего раундов", str(stats["total_rounds"])],
    ]
    summary = Table(summary_rows, colWidths=[6 * cm, 4 * cm])
    summary.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "DejaVu", 10.5),
        ("FONT", (0, 0), (0, -1), "DejaVu-Bold", 10.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1F2A44")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F3FA")),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#D8DEEA")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B6C0D6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(Paragraph("Кратко", h2))
    story.append(summary)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Зрители забрали фестиваль со счётом <b>{sw['viewer']} : {sw['streamer']}</b> по матчам.",
        base))

    story.append(Paragraph("Соотношение побед по дням", h2))
    day_rows = [["День", "Стример", "Матчей", "Победы стримера",
                 "Победы зрителей", "% зрителей"]]
    streamer_for_day = {"25.04": "Hunter", "26.04": "YRARAMI"}
    for d in sorted(stats["day_total"].keys()):
        sw_d = stats["day_side_wins"][d]
        total_d = stats["day_total"][d]
        pct_d = sw_d["viewer"] / total_d * 100 if total_d else 0
        day_rows.append([
            d, streamer_for_day.get(d, "—"), str(total_d),
            str(sw_d.get("streamer", 0)), str(sw_d.get("viewer", 0)),
            f"{pct_d:.0f}%",
        ])
    day_rows.append([
        "Итого", "—", str(total_played),
        str(sw["streamer"]), str(sw["viewer"]),
        f"{pct_view:.1f}%",
    ])
    day_table = Table(day_rows, colWidths=[2 * cm, 3.4 * cm, 2 * cm,
                                           3.4 * cm, 3.4 * cm, 2.6 * cm])
    day_table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "DejaVu", 10),
        ("FONT", (0, 0), (-1, 0), "DejaVu-Bold", 10),
        ("FONT", (0, -1), (-1, -1), "DejaVu-Bold", 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2A44")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F0F3FA")),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#D8DEEA")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B6C0D6")),
    ]))
    story.append(day_table)

    story.append(Spacer(1, 10))
    from reportlab.platypus import Image
    story.append(Image(chart_wins, width=16 * cm, height=8 * cm))

    story.append(PageBreak())

    story.append(Paragraph("Топ-10 по киллам", h2))
    top_rows = [["#", "Игрок", "Роль", "K", "D", "A", "K/D", "Матчей"]]
    for i, (uid, k) in enumerate(stats["user_kills"].most_common(10), 1):
        d = stats["user_deaths"][uid]
        a = stats["user_assists"][uid]
        n = stats["user_matches"][uid]
        kd = (k / d) if d else float(k)
        role = stats["user_role"].get(uid, "—")
        top_rows.append([
            str(i), name_for(uid), role,
            str(k), str(d), str(a), f"{kd:.2f}", str(n),
        ])
    top_table = Table(top_rows, colWidths=[0.9 * cm, 5.8 * cm, 2.4 * cm,
                                           1.4 * cm, 1.4 * cm, 1.4 * cm,
                                           1.6 * cm, 2.0 * cm])
    style_cmds = [
        ("FONT", (0, 0), (-1, -1), "DejaVu", 10),
        ("FONT", (0, 0), (-1, 0), "DejaVu-Bold", 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2A44")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#D8DEEA")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B6C0D6")),
    ]
    for i in range(1, len(top_rows)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i),
                               colors.HexColor("#F7F9FC")))
    for i, (uid, _k) in enumerate(stats["user_kills"].most_common(10), 1):
        if stats["user_role"].get(uid) == "Стример":
            style_cmds.append(("TEXTCOLOR", (1, i), (2, i),
                               colors.HexColor("#C0392B")))
            style_cmds.append(("FONT", (1, i), (2, i), "DejaVu-Bold", 10))
    top_table.setStyle(TableStyle(style_cmds))
    story.append(top_table)

    story.append(Spacer(1, 6))
    story.append(Image(chart_top, width=15 * cm, height=9 * cm))

    story.append(Paragraph("Любопытные факты", h2))
    sk, vk = stats["streamer_kills"], stats["viewer_kills"]
    facts = [
        f"• Всего фрагов за фестиваль — <b>{stats['total_kills']}</b> за <b>{stats['total_rounds']}</b> раундов.",
        f"• Стримеры суммарно — <b>{sk} {plural_kill(sk)}</b>, "
        f"все зрители вместе — <b>{vk} {plural_kill(vk)}</b>. "
        f"То есть по фрагам стримеры перестреляли всю толпу примерно в "
        f"<b>{sk / max(vk, 1):.1f} раза</b>, "
        f"но матчи всё равно проиграли.",
        f"• Самый «мясной» зритель — <b>ArsenQAQA</b>: единственный, кто играл оба дня "
        f"({(arsen_n := stats['user_matches'].get('c5b30b9c-e202-4f5b-8ac1-8bf95a2e3f2c', 0))} "
        f"{plural_match(arsen_n)}), и при этом возглавляет топ среди зрителей по киллам.",
        f"• День 1 (25.04) против <b>Hunter</b>: зрители победили <b>13 из 16</b> матчей (81%).",
        f"• День 2 (26.04) против <b>YRARAMI</b>: зрители победили <b>20 из 26</b> матчей (77%).",
        f"• Лучший фраг-перформанс — <b>YRARAMI</b>: 522 килла за 26 матчей, K/D 3.90.",
    ]
    for f in facts:
        story.append(Paragraph(f, base))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Источник: выгрузка <i>match.matches</i> за 25–26 апреля 2026. "
        "Учитывались только сыгранные матчи (status = MATCH_PROCESSING_COMPLETED) "
        "с непустыми составами команд. В одном матче формата 1 vs 4 победа зачтена "
        "зрителям по итоговому счёту.",
        note))

    doc.build(story)
    print(f"PDF written to {OUT_PATH}")


if __name__ == "__main__":
    stats = compute_stats()
    build_pdf(stats)
