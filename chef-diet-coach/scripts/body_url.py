#!/usr/bin/env python3
"""腰圍折線圖（可以加體重）：組出 QuickChart（Chart.js v4）圖片網址。

腰圍是主線（左軸，點上標數字），體重有填就用虛線畫在右軸。縱軸上下限自動算。

用法：
  python3 body_url.py '[["12/1",92.5,80.2],["12/8",91.8,79.6],["12/15",91.0,null]]'
  每一項是 [日期, 腰圍公分, 體重公斤（沒量就 null 或省略）]。
  加 --config 會印出 JS 設定（本機預覽用），不印網址。
"""
import json
import math
import sys
import urllib.parse

WAIST = "#5EB8A8"
WEIGHT = "#E3BB58"
GRID = "#2A2A2A"
TICK = "#8C8C8C"
LABEL = "#D0D0D0"
FONT = "'Noto Sans TC', 'Noto Sans CJK TC', sans-serif"
W, H = 640, 380


def bounds(vals, step):
    lo, hi = min(vals), max(vals)
    lo = math.floor(lo / step) * step - step
    hi = math.ceil(hi / step) * step + step
    return round(lo, 1), round(hi, 1)


def build_config(rows):
    labels = [r[0] for r in rows]
    waist = [None if r[1] is None else round(float(r[1]), 1) for r in rows]
    weight = [None if len(r) < 3 or r[2] is None else round(float(r[2]), 1) for r in rows]
    has_weight = any(v is not None for v in weight)

    wv = [v for v in waist if v is not None]
    wmin, wmax = bounds(wv, 0.5)
    datasets = [{
        "label": "腰圍（公分）",
        "data": waist,
        "yAxisID": "y",
        "borderColor": WAIST,
        "backgroundColor": WAIST,
        "borderWidth": 2,
        "tension": 0,
        "pointRadius": 4,
        "spanGaps": True,
        "datalabels": {
            "display": True, "align": "top", "anchor": "end", "offset": 4,
            "color": WAIST, "font": {"family": FONT, "size": 11},
            "formatter": "__FMT__",
        },
    }]
    scales = {
        "x": {"grid": {"display": False}, "ticks": {"color": TICK, "font": {"family": FONT, "size": 11}}},
        "y": {
            "position": "left", "min": wmin, "max": wmax,
            "ticks": {"stepSize": 0.5, "color": TICK, "font": {"family": FONT, "size": 11}},
            "grid": {"color": GRID}, "border": {"display": False},
        },
    }
    if has_weight:
        kv = [v for v in weight if v is not None]
        kmin, kmax = bounds(kv, 0.5)
        datasets.append({
            "label": "體重（公斤）",
            "data": weight,
            "yAxisID": "y1",
            "borderColor": WEIGHT,
            "backgroundColor": WEIGHT,
            "borderWidth": 1.5,
            "borderDash": [5, 4],
            "tension": 0,
            "pointRadius": 3,
            "spanGaps": True,
            "datalabels": {"display": False},
        })
        scales["y1"] = {
            "position": "right", "min": kmin, "max": kmax,
            "ticks": {"color": TICK, "font": {"family": FONT, "size": 11}},
            "grid": {"display": False}, "border": {"display": False},
        }
    return {
        "type": "line",
        "data": {"labels": labels, "datasets": datasets},
        "options": {
            "animation": False,
            "layout": {"padding": {"top": 10, "right": 16, "left": 12, "bottom": 4}},
            "scales": scales,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "腰圍與體重" if has_weight else "腰圍（公分）",
                    "color": LABEL,
                    "font": {"family": FONT, "size": 14, "weight": 700},
                    "padding": {"bottom": 12},
                },
                "legend": {
                    "display": has_weight,
                    "position": "bottom",
                    "labels": {"color": "#A6A6A6", "font": {"family": FONT, "size": 12},
                               "boxWidth": 18, "boxHeight": 2, "padding": 16},
                },
                "tooltip": {"enabled": False},
            },
        },
    }


def to_js(cfg):
    s = json.dumps(cfg, ensure_ascii=False, separators=(",", ":"))
    return s.replace('"__FMT__"', "(v)=>v==null?'':v.toFixed(1)")


def build_url(rows):
    cfg = to_js(build_config(rows))
    return (f"https://quickchart.io/chart?v=4&w={W}&h={H}&devicePixelRatio=2"
            f"&bkg=%23191919&c=" + urllib.parse.quote(cfg, safe=""))


if __name__ == "__main__":
    rows = json.loads(sys.argv[1])
    if "--config" in sys.argv:
        print(to_js(build_config(rows)))
    else:
        print(build_url(rows))
