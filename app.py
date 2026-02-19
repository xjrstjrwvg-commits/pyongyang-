import os, time, sys, re
from flask import Flask, render_template, request, jsonify

sys.setrecursionlimit(5000)
app = Flask(__name__)

KANA_LIST = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
VOICE_MAP = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")

# ひらがなをカタカナに変換する関数
def to_katakana(text):
    return "".join([chr(ord(c) + 96) if "ぁ" <= c <= "わ" else c for c in text])

# 辞書データ（一部抜粋）
DICTIONARIES = {
    "country": ["アイスランド", "アメリカ", "アルゼンチン", "パキスタン", "ンジャメナ", "ナミビア", "イタリア", "スペイン"],
    "capital": ["レイキャビク", "ワシントン", "ブエノスアイレス", "イスラマバード", "マドリード"]
}

def get_clean_char(w, pos="head", offset=0):
    text = w.replace("ー", "")
    if pos == "head":
        char = text[offset] if len(text) > offset else text
    else:
        char = text[-(1+offset)] if len(text) > offset else text[-1]
    return SMALL_TO_LARGE.get(char, char).translate(VOICE_MAP)

def shift_kana(char, n):
    if char not in KANA_LIST: return char
    idx = KANA_LIST.index(char)
    return KANA_LIST[(idx + n) % len(KANA_LIST)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    max_len = min(int(d.get('max_len', 5)), 50)
    pos_shift = int(d.get('pos_shift', 0))
    kana_shift = int(d.get('kana_shift', 0))
    exclude_conjugates = d.get('exclude_conjugates', False)
    round_trip = d.get('round_trip', False)
    target_total_len = d.get('target_total_len')
    
    # 入力をカタカナ・清音に統一
    start_char = to_katakana(d.get('start_char', "")).translate(VOICE_MAP)
    end_char = to_katakana(d.get('end_char', "")).translate(VOICE_MAP)
    # 複数必須文字の処理（カンマや読点で分割）
    raw_must = re.split('[、,]', to_katakana(d.get('must_char', "")))
    must_chars = [c.translate(VOICE_MAP) for c in raw_must if c]

    selected_cats = d.get('categories', ["country"])
    word_pool = list(set([w for cat in selected_cats for w in DICTIONARIES.get(cat, [])]))

    results = []
    start_time = time.time()
    timeout = 15

    def solve(path, current_total_len, used_pairs):
        if time.time() - start_time > timeout or len(results) >= 1500: return
        
        if len(path) == max_len:
            if target_total_len is not None and current_total_len != target_total_len: return
            if end_char and get_clean_char(path[-1], "tail", pos_shift) != end_char: return
            if must_chars:
                full = "".join(path).translate(VOICE_MAP)
                if not all(mc in full for mc in must_chars): return
            results.append(list(path))
            return
        
        last_tail = get_clean_char(path[-1], "tail", pos_shift)
        target_head = shift_kana(last_tail, kana_shift)

        for next_w in word_pool:
            if not round_trip and next_w in path: continue
            if round_trip and len(path) >= 1 and next_w == path[-1]: continue 

            if get_clean_char(next_w, "head", pos_shift) == target_head:
                pair = tuple(sorted([path[-1], next_w]))
                if exclude_conjugates and pair in used_pairs: continue
                new_used = used_pairs.copy(); new_used.add(pair)
                solve(path + [next_w], current_total_len + len(next_w), new_used)

    sw = to_katakana(d.get('start_word', ""))
    starts = [sw] if (sw in word_pool) else word_pool
    starts.sort()

    for w in starts:
        if len(results) >= 1500: break
        if not sw and start_char and get_clean_char(w, "head", pos_shift) != start_char: continue
        solve([w], len(w), set())

    sort_type = d.get('sort_type', 'kana')
    if sort_type == 'length':
        results.sort(key=lambda x: (len("".join(x)), x))
    else:
        results.sort()

    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
