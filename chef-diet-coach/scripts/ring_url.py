#!/usr/bin/env python3
"""今天的熱量／蛋白質環形圖：組出 QuickChart（Chart.js v4）圖片網址。

整圈 = 目標。每個餐次一段顏色，預留的東西是空心橘框，剩下的是暗色底軌，
中間寫「還能吃 X 大卡」或「還差 X 克」，下面再一行「已吃 Y 大卡／克」（11/25 起）。
網址直接放進 Notion 圖片區塊，Notion 會自己去載圖，不用上傳檔案。

用法：
  python3 ring_url.py kcal '{"breakfast":450,"lunch":700,"reserve":300,"target":2000}'
  python3 ring_url.py prot '{"breakfast":25,"lunch":40,"reserve":25,"target":140}'
  加 --config 會印出 Chart.js 設定（本機預覽用），不印網址。

鍵：breakfast 早餐、whey 乳清（或蛋白飲）、lunch 午餐、snack 點心、dinner 晚餐、
drinks 飲料、reserve 預留、target 目標。沒吃的餐次可以省略。
可以加 "reserve_label":"預留乳清" 改圖例上預留那一格的名字（預設「預留」）。
"""
import json
import sys
import urllib.parse

ORDER = [
    ("breakfast", "早餐", "#E3BB58"),
    ("whey", "乳清", "#E29A4C"),
    ("lunch", "午餐", "#5EB8A8"),
    ("snack", "點心", "#AE90D6"),
    ("dinner", "晚餐", "#6AADD4"),
    ("drinks", "飲料", "#DA8FB4"),
]
TRACK = "#2A2A2A"
RESERVE = "#E29A4C"
TEXT = "#F2F2F2"
MUTED = "#8C8C8C"
LEGEND = "#A6A6A6"
OVER_ORANGE = "#E29A4C"
OVER_RED = "#E5534B"
FONT = "'Noto Sans TC', 'Noto Sans CJK TC', sans-serif"
W, H = 440, 400


def build_config(kind, g):
    eaten = sum(float(g.get(k, 0) or 0) for k, _, _ in ORDER)
    res = float(g.get("reserve", 0) or 0)
    tgt = float(g["target"])
    rem = tgt - eaten - res

    data, fill, stroke, width, names = [], [], [], [], []
    for k, name, color in ORDER:
        v = float(g.get(k, 0) or 0)
        if v > 0:
            data.append(round(v, 1)); fill.append(color); stroke.append(color); width.append(0); names.append(name)
    if res > 0:
        data.append(round(res, 1)); fill.append("rgba(0,0,0,0)"); stroke.append(RESERVE); width.append(1.5); names.append(g.get("reserve_label") or "預留")
    if rem > 0:
        data.append(round(rem, 1)); fill.append(TRACK); stroke.append("#3C3C3C"); width.append(1)
        names.append("還能吃" if kind == "kcal" else "還差")

    unit = "大卡" if kind == "kcal" else "克"
    small = {"family": FONT, "size": 13, "weight": 400}
    big = {"family": FONT, "size": 44, "weight": 700}
    eaten_line = f"已吃 {int(round(eaten))} {unit}"
    eaten_font = {"family": FONT, "size": 13, "weight": 700}
    if kind == "kcal":
        if rem >= -1e-9:
            lines = ["還能吃", str(int(round(max(rem, 0)))), unit, eaten_line]
            colors = [MUTED, TEXT, MUTED, LEGEND]
        else:
            over = int(round(-rem))
            lines = ["超過", str(over), unit, eaten_line]
            colors = [MUTED, OVER_ORANGE if over <= 200 else OVER_RED, MUTED, LEGEND]
        fonts = [small, big, small, eaten_font]
    else:
        if eaten >= tgt - 1e-9:
            lines, colors, fonts = ["今天吃了", str(int(round(eaten))), unit], [MUTED, TEXT, MUTED], [small, big, small]
        elif rem > 1e-9:
            lines = ["還差", str(int(round(rem))), unit, eaten_line]
            colors, fonts = [MUTED, TEXT, MUTED, LEGEND], [small, big, small, eaten_font]
        else:
            mid = {"family": FONT, "size": 20, "weight": 700}
            lines = ["含預留", "已達標", f"已吃 {int(round(eaten))} 克", f"含預留 {int(round(eaten + res))} 克"]
            colors = [TEXT, TEXT, MUTED, MUTED]
            fonts = [mid, mid, small, small]

    return {
        "type": "doughnut",
        "data": {
            "labels": names,
            "datasets": [{
                "data": data,
                "backgroundColor": fill,
                "borderColor": stroke,
                "borderWidth": width,
                "borderRadius": 6,
                "spacing": 4,
                "hoverOffset": 0,
            }],
        },
        "options": {
            "cutout": "86%",
            "radius": "92%",
            "animation": False,
            "layout": {"padding": {"top": 18, "bottom": 6, "left": 12, "right": 12}},
            "plugins": {
                "legend": {
                    "display": True,
                    "position": "bottom",
                    "labels": {
                        "color": LEGEND,
                        "font": {"family": FONT, "size": 12},
                        "usePointStyle": True,
                        "pointStyle": "circle",
                        "boxWidth": 7,
                        "boxHeight": 7,
                        "padding": 14,
                    },
                },
                "datalabels": {"display": False},
                "tooltip": {"enabled": False},
                "annotation": {
                    "annotations": {
                        "center": {
                            "type": "doughnutLabel",
                            "content": lines,
                            "font": fonts,
                            "color": colors,
                        }
                    }
                },
            },
        },
    }


def build_url(kind, g):
    cfg = json.dumps(build_config(kind, g), ensure_ascii=False, separators=(",", ":"))
    return (f"https://quickchart.io/chart?v=4&w={W}&h={H}&devicePixelRatio=2"
            f"&bkg=%23191919&c=" + urllib.parse.quote(cfg, safe=""))


if __name__ == "__main__":
    kind, raw = sys.argv[1], json.loads(sys.argv[2])
    if "--config" in sys.argv:
        print(json.dumps(build_config(kind, raw), ensure_ascii=False))
    else:
        print(build_url(kind, raw))
