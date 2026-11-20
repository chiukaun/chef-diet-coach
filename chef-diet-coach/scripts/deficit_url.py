#!/usr/bin/env python3
"""每日熱量赤字折線圖：組出 QuickChart（Chart.js v4）圖片網址。

藍線是每天的赤字，點的顏色：綠＝達到當週目標，橘＝有赤字但沒達標，紅＝吃得比消耗多。
灰色虛線是當週每日目標（赤字階梯），紫色線是每週平均。

用法：
  python3 deficit_url.py '[["12/1",80,100,1],["12/2",150,100,1],["12/8",260,200,2]]'
  每一項是 [日期, 赤字, 當週每日赤字目標, 第幾週]，只放已結算的日子。
  加 --config 會印出 JS 設定（本機預覽用），不印網址。
"""
import json
import sys
import urllib.parse

LINE = "#6AADD4"
GREEN = "#57C27D"
ORANGE = "#E29A4C"
RED = "#E5534B"
TARGET = "#9A9A9A"
GRID = "#2A2A2A"
TICK = "#8C8C8C"
LABEL = "#D0D0D0"
AVG = "#C9A7F0"
FONT = "'Noto Sans TC', 'Noto Sans CJK TC', sans-serif"
W, H = 640, 380


def color(d, t):
    if d >= t:
        return GREEN
    if d > 0:
        return ORANGE
    return RED


def build_config(rows):
    labels = [r[0] for r in rows]
    vals = [round(float(r[1]), 1) for r in rows]
    tgts = [float(r[2]) for r in rows]
    weeks = [r[3] for r in rows]
    pts = [color(d, t) for d, t in zip(vals, tgts)]
    sums = {}
    for w, v in zip(weeks, vals):
        sums.setdefault(w, []).append(v)
    avg_of = {w: round(sum(v) / len(v), 1) for w, v in sums.items()}
    avgs = [avg_of[w] for w in weeks]
    # 每週平均的數字標在該週第二天（只有一天就標第一天），避開邊緣
    label_idx = []
    for w in dict.fromkeys(weeks):
        idxs = [i for i, x in enumerate(weeks) if x == w]
        label_idx.append(idxs[1] if len(idxs) > 1 else idxs[0])
    lo = min(min(vals), 0)
    hi = max(max(vals), max(tgts))
    ymin = min(int((lo // 200) * 200), -200)
    ymax = int(-(-hi // 200) * 200) + 200
    cfg = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "每日赤字",
                    "data": vals,
                    "borderColor": LINE,
                    "backgroundColor": LINE,
                    "borderWidth": 2,
                    "tension": 0,
                    "pointRadius": 5,
                    "pointBackgroundColor": pts,
                    "pointBorderColor": pts,
                    "datalabels": {
                        "display": True,
                        "align": "top",
                        "anchor": "end",
                        "offset": 4,
                        "color": LABEL,
                        "font": {"family": FONT, "size": 11},
                        "formatter": "__FMT__",
                    },
                },
                {
                    "label": "週目標",
                    "data": tgts,
                    "borderColor": TARGET,
                    "backgroundColor": TARGET,
                    "borderWidth": 1.5,
                    "borderDash": [6, 4],
                    "pointRadius": 0,
                    "stepped": "middle",
                    "datalabels": {"display": False},
                },
                {
                    "label": "週平均",
                    "data": avgs,
                    "borderColor": AVG,
                    "backgroundColor": AVG,
                    "borderWidth": 2,
                    "pointRadius": 0,
                    "stepped": "middle",
                    "datalabels": {
                        "display": True,
                        "align": "top",
                        "anchor": "end",
                        "offset": 4,
                        "color": AVG,
                        "font": {"family": FONT, "size": 11, "weight": 700},
                        "formatter": "__AVGFMT__",
                    },
                },
            ],
        },
        "options": {
            "animation": False,
            "layout": {"padding": {"top": 10, "right": 20, "left": 14, "bottom": 4}},
            "scales": {
                "x": {
                    "grid": {"display": False},
                    "ticks": {"color": TICK, "font": {"family": FONT, "size": 11}},
                },
                "y": {
                    "min": ymin,
                    "max": ymax,
                    "ticks": {"stepSize": 200, "color": TICK, "font": {"family": FONT, "size": 11}},
                    "grid": {"color": GRID},
                    "border": {"display": False},
                },
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "每日熱量赤字（大卡）",
                    "color": LABEL,
                    "font": {"family": FONT, "size": 14, "weight": 700},
                    "padding": {"bottom": 12},
                },
                "legend": {
                    "display": True,
                    "position": "bottom",
                    "labels": {
                        "color": "#A6A6A6",
                        "font": {"family": FONT, "size": 12},
                        "boxWidth": 18,
                        "boxHeight": 2,
                        "padding": 16,
                    },
                },
                "tooltip": {"enabled": False},
                "annotation": {
                    "annotations": {
                        "zero": {
                            "type": "line",
                            "yMin": 0,
                            "yMax": 0,
                            "borderColor": "#5A5A5A",
                            "borderWidth": 1,
                        }
                    }
                },
            },
        },
    }
    return cfg, label_idx


def to_js(cfg, label_idx):
    s = json.dumps(cfg, ensure_ascii=False, separators=(",", ":"))
    s = s.replace('"__FMT__"', "(v)=>Math.round(v)")
    idx = json.dumps(label_idx)
    return s.replace('"__AVGFMT__"', "(v,c)=>" + idx + ".includes(c.dataIndex)?'平均 '+Math.round(v):''")


def build_url(rows):
    return (f"https://quickchart.io/chart?v=4&w={W}&h={H}&devicePixelRatio=2"
            f"&bkg=%23191919&c=" + urllib.parse.quote(to_js(*build_config(rows)), safe=""))


if __name__ == "__main__":
    rows = json.loads(sys.argv[1])
    if "--config" in sys.argv:
        print(to_js(*build_config(rows)))
    else:
        print(build_url(rows))
