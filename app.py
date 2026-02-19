import os, time, sys, re
from flask import Flask, render_template, request, jsonify

sys.setrecursionlimit(10000)
app = Flask(__name__)

KANA_LIST = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
VOICE_MAP = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")

def to_katakana(text):
    return "".join([chr(ord(c) + 96) if "ぁ" <= c <= "わ" else c for c in text])

# 辞書データ
DICTIONARY_MASTER = {
    "country": ["アメリカ", "コスタリカ", "コロンビア", "リトアニア", "アイスランド", "イタリア", "インド", "ブラジル", "フランス", "ドイツ", "ニホン"],
    "capital": ["ワシントン", "サンホセ", "ボゴタ", "ビリニュス", "レイキャビク", "ローマ", "ニューデリー", "ブラジリア", "パリ", "ベルリン", "トウキョウ"]
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
    return KANA_LIST[(KANA_LIST.index(char) + n) % len(KANA_LIST)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_dictionary')
def get_dictionary():
    return jsonify(DICTIONARY_MASTER)

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    max_len = min(int(d.get('max_len', 5)), 50)
    pos_shift = int(d.get('pos_shift', 0))
    kana_shift = int(d.get('kana_shift', 0))
    round_trip = d.get('round_trip', False) # 牛耕モードスイッチ
    
    start_char = to_katakana(d.get('start_char', "")).translate(VOICE_MAP)
    end_char = to_katakana(d.get('end_char', "")).translate(VOICE_MAP)
    blocked_words = set(d.get('blocked_words', []))
    force_words = set(d.get('force_words', []))
    
    selected_cats = d.get('categories', ["country"])
    word_pool = [w for cat in selected_cats for w in DICTIONARY_MASTER.get(cat, []) if w not in blocked_words]

    results = []
    start_time = time.time()
    
    def solve(path, current_total_len):
        if time.time() - start_time > 15 or len(results) >= 1500: return
        if len(path) == max_len:
            if not force_words.issubset(set(path)): return
            # 最後の単語の尻文字チェック
            if end_char and get_clean_char(path[-1], "tail", pos_shift) != end_char: return
            results.append(list(path))
            return
        
        # 1つ前の単語
        last_word = path[-1]
        
        # 牛耕(round_trip)がONの場合の接続判定
        if round_trip:
            if len(path) % 2 != 0:
                # 奇数番目(1,3,5...) → 偶数番目への接続：語尾(尻) ＝ 語尾(尻)
                src_char = get_clean_char(last_word, "tail", pos_shift)
                target_pos = "tail"
            else:
                # 偶数番目(2,4,6...) → 奇数番目への接続：語頭(頭) ＝ 語頭(頭)
                src_char = get_clean_char(last_word, "head", pos_shift)
                target_pos = "head"
        else:
            # 通常モード：語尾(尻) ＝ 語頭(頭)
            src_char = get_clean_char(last_word, "tail", pos_shift)
            target_pos = "head"

        required_char = shift_kana(src_char, kana_shift)

        for next_w in word_pool:
            if next_w in path: continue 
            if get_clean_char(next_w, target_pos, pos_shift) == required_char:
                solve(path + [next_w], current_total_len + len(next_w))

    sw = to_katakana(d.get('start_word', ""))
    starts = [sw] if (sw in word_pool) else word_pool
    for w in starts:
        if not sw and start_char and get_clean_char(w, "head", pos_shift) != start_char: continue
        solve([w], len(w))

    sort_type = d.get('sort_type', 'kana')
    if sort_type == 'len_desc': results.sort(key=lambda x: (len("".join(x)), x), reverse=True)
    elif sort_type == 'len_asc': results.sort(key=lambda x: (len("".join(x)), x))
    else: results.sort()
    
    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
