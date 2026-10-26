# -*- coding: utf-8 -*-
"""Этикетки «Раки варёные» (ООО «Ракомат») для термопринтера АТОЛ BP41, 203 dpi.

  python3 make_label.py             — собрать все макеты
  python3 make_label.py 75x50-all   — только один

Кегли: по ТР ТС 022/2011 ч.4.12 наименование, количество, дата изготовления
и срок годности печатаются шрифтом с высотой строчных букв не менее 2 мм,
остальные сведения — не менее 0,8 мм. У Liberation Sans Narrow строчная = 0,528
кегля, поэтому ключевые строки идут кеглем 3,8 мм, заголовок (прописные,
0,688 кегля) — не меньше 3,0 мм.
"""
from PIL import Image, ImageDraw, ImageFont
import sys

DPI = 203
MM = DPI / 25.4
px = lambda mm: int(round(mm * MM))
FD = "/usr/share/fonts/truetype/liberation/"
font = lambda mm, b=False: ImageFont.truetype(
    FD + f"LiberationSansNarrow-{'Bold' if b else 'Regular'}.ttf", max(6, px(mm)))

X_RATIO, CAP_RATIO = 0.528, 0.688
BIG_MM   = round(2.0 / X_RATIO + 0.15, 1)    # 3.8 мм — ключевые сведения
TITLE_MM = round(2.0 / CAP_RATIO + 0.05, 1)  # 3.0 мм — заголовок из прописных

NB = " "   # неразрывный пробел: по нему wrap() не переносит

DATA = dict(
    name      = "РАКИ ВАРЁНЫЕ",
    name_full = "Раки узкопалые варёные, неразделанные, охлаждённые, в бульоне.",
    ready     = "Продукт готов к употреблению в охлаждённом или разогретом виде.",
    usage     = "Перед подачей разогреть бульон и залить им раков. В ведре и в микроволновой печи не разогревать.",
    packdate  = f"Упаковано в день изготовления. Претензии: rakomat@bk.ru,{NB}тел.{NB}+7{NB}966{NB}339-96-69",
    # --- ключевые сведения (кегль BIG_MM) ---
    netto     = f"Масса нетто 2200{NB}г, раков 930{NB}г",
    netto2    = f"Масса раков: 930{NB}г",
    raw       = f"Сварено из 1{NB}кг живых раков",
    shelf     = f"Срок годности: 5{NB}суток",
    dates     = f"Изготовлено ___.___.___{NB}{NB}Годен до ___.___.___",
    dates_a   = f"Изготовлено 02.09.2026",
    dates_blank = "Изготовлено ____.____.20____",
    dates_b   = "Годен до ___.___.___",
    # --- прочие сведения ---
    sostav    = "Состав: вода питьевая, раки, соль пищевая, семена укропа.",
    allergen  = "Содержит ракообразных.",
    nutrition = f"Пищевая ценность в 100{NB}г: белки — 1,5{NB}г, жиры — 0,1{NB}г, "
                f"углеводы — 0,1{NB}г. Энергетическая ценность — 5{NB}ккал / 25{NB}кДж.",
    storage   = f"Условия хранения: при температуре от +3 до +5{NB}°C.",
    opened    = f"После вскрытия упаковки хранить при температуре от +3 до +5{NB}°C не более 12{NB}часов.",
    size      = "Размер раков: ____________",   # подставляется set_pack()
    maker     = "Изготовитель: ООО «Ракомат», Россия, Московская обл., "
                "д. Осоргино, 202.",
    claims    = f"По вопросам качества: rakomat@bk.ru, тел.{NB}8{NB}966{NB}339-96-69",
    # --- уплотнённые строки для варианта «всё на одной 58x40» ---
    nutrition_c = f"Пищевая ценность в 100{NB}г: белки 1,5{NB}г, жиры 0,1{NB}г, "
                  f"углеводы 0,1{NB}г, 5{NB}ккал (25{NB}кДж).",
    storage_c   = f"Хранить при температуре от +3 до +5{NB}°C, в том числе после "
                  f"вскрытия упаковки, не более 12{NB}ч после вскрытия.",
    tu        = f"ТУ{NB}10.20.34-001-96717702-2026",
    decl      = f"Декларация о соответствии {NB.join('ЕАЭС N RU Д-RU.РА07.В.32767/26'.split())}",
)

# Фасовки: кг живых раков -> (масса нетто с бульоном, г; раков варёных, г).
# Выход варёных раков 93% от живых (930 г из 1 кг — замер по базовой фасовке),
# бульон масштабируется пропорционально. ЦИФРЫ 1,5/3/6 кг — РАСЧЁТНЫЕ,
# перед печатью сверить с реальным взвешиванием.
PACKS = {
    "1":   (2200,   930),
    "1.5": (3300,  1395),
    "3":   (6600,  2790),
}

# Калибр по перечню товаров (Приложение №3 к договору 12-65 от 28.10.2026):
# «до 40», «40/70», «70+» — масса одного рака в граммах.
CALIBRE = {
    "do40":   f"до 40{NB}г",
    "4070":   f"40–70{NB}г",
    "70plus": f"от 70{NB}г",
}

def set_pack(kg, cal=None):
    """Подставить в DATA массы, строку о сырье и калибр для фасовки kg ('1', '1.5', ...)."""
    netto, meat = PACKS[kg]
    human = kg.replace(".", ",")
    # нетто больших фасовок — в кг, иначе строка не влезает в 58 мм
    n = f"{netto/1000:.1f}".replace(".", ",") + f"{NB}кг" if netto >= 3000 else f"{netto}{NB}г"
    DATA["netto"]  = f"Масса нетто {n}, раков {meat}{NB}г"
    DATA["netto2"] = f"Масса раков: {meat}{NB}г"
    DATA["raw"]    = f"Сварено из {human}{NB}кг живых раков"
    if cal:
        DATA["size"] = f"Размер раков: {CALIBRE[cal]}"

BIG  = {"name_full", "netto", "raw", "shelf", "dates", "dates_a", "dates_b", "dates_blank"}
MID  = set()                        # масса идёт кеглем состава
BUMP = {"sostav": 1.2, "usage": 1.2, "ready": 1.2}
BOLD_OFF = {"name_full"}              # эти строки чуть крупнее прочего текста
BOLD = {"allergen", "netto", "raw", "size", "netto2", "storage", "storage_c", "shelf", "dates", "dates_a",
        "dates_blank", "usage", "ready",
        "dates_b", "opened"}

PRESETS = {
    "100x70": dict(w=100, h=70, m=2.5, logo=13, title_pos="right",
                   body=["sostav","allergen","nutrition","netto","netto2","storage",
                         "shelf","opened","dates","maker","claims"],
                   foot=["tu","decl"], foot_mm=2.0),
    "70x50-all": dict(w=70, h=50, m=1.8, logo=7, title_mm=4.2, title_pos="right", rule=False, eac_mm=6.0,
                   body=["name_full","sostav","allergen","nutrition_c","netto",
                         "shelf","dates_a","storage_c","usage"],
                   foot=["packdate","maker","tu"], foot_mm=1.5),
    "70x55-all": dict(w=70, h=55, m=1.8, logo=7, title_mm=4.2, title_pos="right", rule=False, eac_mm=6.0,
                   body=["name_full","sostav","allergen","nutrition_c","netto",
                         "shelf","dates_a","storage_c","usage"],
                   foot=["packdate","maker","tu"], foot_mm=1.5),
    "70x60-all": dict(w=70, h=60, m=1.8, logo=7, title_mm=4.2, title_pos="right", rule=False, eac_mm=6.0,
                   body=["name_full","sostav","allergen","nutrition_c","netto",
                         "shelf","dates_a","storage_c","usage"],
                   foot=["packdate","maker","tu"], foot_mm=1.5),
    "58x80-all": dict(w=58, h=80, m=1.8, mt=3.5, logo=7, logo_align="center", title_mm=0, rule=False, eac_mm=6.0,
                   body=["name_full","sostav","allergen","nutrition_c","netto","raw",
                         "shelf","dates_a","storage_c","ready","usage"],
                   foot=["packdate","maker","tu"], foot_mm=1.9),
    "58x80-blank": dict(w=58, h=80, m=1.8, mt=3.5, logo=7, logo_align="center", title_mm=0, rule=False, eac_mm=6.0,
                   body=["name_full","sostav","allergen","nutrition_c","netto","raw",
                         "shelf","dates_blank","storage_c","ready","usage"],
                   foot=["packdate","maker","tu"], foot_mm=1.9),
    "58x40-A": dict(w=58, h=40, m=1.4, logo=5, logo_align="center",
                   title_mm=0, rule=False, eac_mm=6.0, eac_pos="tr",
                   body=["name_full","netto","shelf","dates_a"],
                   foot=[], foot_mm=1.5),
    "58x40-B": dict(w=58, h=40, m=1.5, logo=0, title_mm=3.0, title_align="center",
                   rule=False, eac_mm=6.0,
                   body=["sostav","allergen","nutrition_c","storage_c","usage"],
                   foot=["packdate","maker","tu"], foot_mm=1.5),
    "58x40-1": dict(w=58, h=40, m=1.8, logo=5, title_pos="right",
                   body=["netto","netto2","shelf","dates_a"], foot=["tu"], foot_mm=1.5),
    "58x40-2": dict(w=58, h=40, m=1.8, logo=0, title_mm=2.6, suffix="  · состав и хранение",
                   body=["sostav","allergen","nutrition","storage","opened","maker"],
                   foot=["decl","claims"], foot_mm=1.5),
    # комплект на рулон 50x30: ключевые сведения крупно на первой наклейке
    "50x30-1": dict(w=50, h=30, m=1.6, logo=0, rule=False, eac_pos="tr",
                   title_align="center", title_mm=3.6, logo_bottom=5,
                   body=["netto","netto2","shelf","dates_a"], foot=[], foot_mm=1.5),
    "50x50-all": dict(w=50, h=50, m=1.6, logo=0, rule=False, eac_pos="tr",
                   title_align="center", title_mm=3.0,
                   body=["netto","netto2","shelf","dates_a","sostav","allergen",
                         "nutrition","storage","opened","maker"],
                   foot=["tu","decl"], foot_mm=1.2),
    "50x30-2": dict(w=50, h=30, m=1.8, logo=0, title_mm=2.6,
                   body=["sostav","allergen","nutrition"], foot=["tu"], foot_mm=1.5),
    "50x30-3": dict(w=50, h=30, m=1.8, logo=0, title_mm=2.6,
                   body=["storage","opened","maker","claims"],
                   foot=["decl"], foot_mm=1.5),
}

# --- 58x80 под каждую фасовку: 58x80-1.5kg, 58x80-3kg, 58x80-6kg, и blank-версии ---
# --- пять позиций перечня товаров арендатора (Приложение №3, 12-65 от 28.10.2026) ---
ASSORT = [("do40", "1"), ("do40", "1.5"), ("4070", "1"), ("do40", "3"), ("70plus", "1")]
for _cal, _kg in ASSORT:
    _body = list(PRESETS["58x80-all"]["body"])
    _body.insert(_body.index("raw") + 1, "size")
    for _base, _tag in (("58x80-all", ""), ("58x80-blank", "-blank")):
        _b = list(PRESETS[_base]["body"]); _b.insert(_b.index("raw") + 1, "size")
        PRESETS[f"58x80-{_cal}-{_kg}kg{_tag}"] = dict(
            PRESETS[_base], pack=_kg, calibre=_cal, body=_b)


def build(key, out=None, quiet=False):
    p = PRESETS[key]
    if p.get("pack"):
        set_pack(p["pack"], p.get("calibre"))
    W, H, M = px(p["w"]), px(p["h"]), px(p["m"])
    MT = px(p.get("mt", p["m"]))   # верхнее поле: термоголовка подрезает самый край
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)

    def wrap(text, f, maxw):
        lines, cur = [], ""
        for w in text.split(" "):
            t = (cur + " " + w).strip() if cur else w
            if d.textlength(t, font=f) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        return lines

    # --- знак ЕАС: три буквы, вписанные в квадрат (Решение КТС № 711) ---
    eac = px(p.get("eac_mm", 6.0 if p["w"] < 70 else 8.0))

    # --- шапка ---
    y0, lw, lh = MT, 0, 0
    if p["logo"]:
        logo = Image.open("logo.png").convert("L")
        lh = px(p["logo"]); lw = int(logo.width * lh / logo.height)
        cap = W - 2*M
        if p.get("title_pos") == "right":
            cap = int(cap * 0.42)
        if lw > cap:
            lw, lh = cap, int(logo.height * cap / logo.width)
        lx = M + (W - 2*M - lw) // 2 if p.get("logo_align") == "center" else M
        img.paste(logo.resize((lw, lh), Image.LANCZOS), (lx, MT))
        y0 = MT + lh + px(1.0)

    # заголовок: кегль не ниже TITLE_MM, ужимается только если иначе не влезает
    tsize = p.get("title_mm", TITLE_MM)
    title = DATA["name"] + p.get("suffix", "")
    if tsize <= 0:
        pass
    elif p.get("title_pos") == "right" and lw:
        tx = M + lw + px(3)
        rcap = W - M - tx - (eac + px(2) if p.get("eac_pos") == "tr" else 0)
        while tsize > 2.0 and d.textlength(title, font=font(tsize, True)) > rcap:
            tsize -= 0.1
        ft = font(tsize, True)
        d.text((tx, MT + (lh - int(ft.size * 1.02)) // 2), title, font=ft, fill=0)
    else:
        tcap = W - 2*M - (eac + px(2) if p.get("eac_pos") == "tr" else 0)
        while tsize > 2.0 and d.textlength(title, font=font(tsize, True)) > tcap:
            tsize -= 0.1
        ft = font(tsize, True)
        tx = M
        if p.get("title_align") == "center":
            tx = M + (tcap - int(d.textlength(title, font=ft))) // 2
        d.text((tx, y0), title, font=ft, fill=0)
        y0 += int(ft.size * 1.02) + px(0.5)
    if p.get("rule", True) and tsize > 0:
        d.line([(M, y0), (W - M, y0)], fill=0, width=max(1, px(0.25)))
        y0 += px(0.8)

    # --- знак ЕАС: официальное изображение (Решение КТС № 711), eac.png ---
    ex = W - M - eac
    ey = MT if p.get("eac_pos") == "tr" else H - M - eac
    import os
    if os.path.exists("eac.png"):
        src_m = Image.open("eac.png").convert("RGBA")
        flat = Image.new("RGBA", src_m.size, (255, 255, 255, 255))
        flat.alpha_composite(src_m)
        mark = flat.convert("L").resize((eac, eac), Image.LANCZOS)
        img.paste(mark, (ex, ey))
    else:
        s8 = eac / 8.0
        bar = lambda a,b,c,e: d.rectangle([ex+a*s8, ey+b*s8, ex+c*s8-1, ey+e*s8-1], fill=0)
        T, LW = 1.15, 2.6
        e_, a_, c_ = 0.0, 2.7, 5.4
        bar(e_,0,e_+T,8); bar(e_,0,e_+LW,T); bar(e_,3.5,e_+LW-0.4,3.5+T); bar(e_,8-T,e_+LW,8)
        bar(a_,0,a_+T,8); bar(a_+LW-T,0,a_+LW,8); bar(a_,0,a_+LW,T); bar(a_,3.5,a_+LW,3.5+T)
        bar(c_,0,c_+T,8); bar(c_,0,c_+LW,T); bar(c_,8-T,c_+LW,8)

    # --- подвал (переносится с учётом места под знак ЕАС) ---
    foot_mm = max(p["foot_mm"], round(0.8 / X_RATIO + 0.05, 2))
    ff = font(foot_mm)
    lhf = int(ff.size * 1.25)
    foot_lines = [ln for k in p["foot"] for ln in wrap(DATA[k], ff, W - 2*M - eac - px(2))]
    foot_y = H - M - lhf * len(foot_lines)
    for i, ln in enumerate(foot_lines):
        d.text((M, foot_y + i*lhf), ln, font=ff, fill=0)

    # --- тело: ключевые сведения фиксированным кеглем, прочие — подбором ---
    limit = (foot_y if p.get("eac_pos") == "tr" else min(foot_y, ey)) - px(1.0)
    def layout(sz, draw=False):
        y = y0
        for k in p["body"]:
            fs = p.get("big_mm", BIG_MM) if k in BIG else \
                 p.get("mid_mm", BIG_MM) if k in MID else sz * BUMP.get(k, 1)
            f = font(fs, k in BOLD)
            for ln in wrap(DATA[k], f, W - 2*M):
                if draw: d.text((M, y), ln, font=f, fill=0)
                y += int(f.size * 1.16)
            y += px(0.4)
        return y
    steps = [round(3.0 - i*0.05, 2) for i in range(37)]   # 3,00 … 1,20 с шагом 0,05
    size = next((c for c in steps
                 if layout(c) <= limit), None)
    if size is None:
        print(f"!! {key}: не влезает — нужен формат крупнее или меньше текста"); return
    layout(size, draw=True)
    if size * X_RATIO < 0.8:
        print(f"!! {key}: строчные {size*X_RATIO:.2f} мм — ниже минимума 0,8 мм")

    if p.get("logo_bottom"):
        lg = Image.open("logo.png").convert("L")
        bh = px(p["logo_bottom"]); bw = int(lg.width * bh / lg.height)
        cap = W - 2*M - eac - px(2)
        if bw > cap: bw, bh = cap, int(lg.height * cap / lg.width)
        img.paste(lg.resize((bw, bh), Image.LANCZOS), (M, H - M - bh))

    if p.get("rotate"): img = img.rotate(-90, expand=True)
    stem = out or f"label-{key}"
    img.save(f"{stem}.png", dpi=(DPI, DPI))
    img.convert("1", dither=Image.NONE).save(f"{stem}.pdf", resolution=DPI)
    bm = p.get("big_mm", BIG_MM)
    if not quiet:
        print(f"{stem} — {p['w']}x{p['h']} мм, ключевые {bm} мм "
              f"(строчная {bm*X_RATIO:.2f}), прочее {size} мм "
              f"(строчная {size*X_RATIO:.2f})")
    return f"{stem}.pdf"

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--date" in args:                       # --date 04.09.2026 → «Изготовлено 04.09.2026»
        i = args.index("--date")
        DATA["dates_a"] = f"Изготовлено {args[i+1]}"
        del args[i:i+2]
    for k in (args or PRESETS):
        build(k)
