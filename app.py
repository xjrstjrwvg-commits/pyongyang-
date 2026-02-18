import os
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 50音の環状リスト（自分用の特殊接続ロジック）
KANA_LIST = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"

def shift_kana(char, n):
    """文字をn個分、50音順にずらす（ン の次は ア）"""
    if char not in KANA_LIST: return char
    idx = KANA_LIST.index(char)
    new_idx = (idx + n) % len(KANA_LIST)
    return KANA_LIST[new_idx]

# 辞書データ（自分用：50単語を目指すなら、さらに単語を追加してください）
DICTIONARIES = {
    "country": ["アイスランド", "アメリカ", "パキスタン", "ンジャメナ", "ナミビア", "アルゼンチン"], 
    "animal": ["アヒル", "イヌ", "ウサギ"],
}

SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
VOICE_MAP = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")

def get_clean_char(w, pos="head"):
    text = w.replace("ー", "")
    char = text[0] if pos == "head" else text[-1]
    return SMALL_TO_LARGE.get(char, char).translate(VOICE_MAP)

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    max_len = min(int(d.get('max_len', 5)), 50)
    shift_n = int(d.get('shift', 0)) # 50音をいくつずらすか（例：+1）
    exclude_conjugates = d.get('exclude_conjugates', False)
    
    word_pool = []
    for cat in d.get('categories', ["country"]):
        word_pool.extend(DICTIONARIES.get(cat, []))
    word_pool = list(set(word_pool))

    results = []
    start_time = time.time()
    timeout = 15 

    def solve(path, used_pairs):
        if time.time() - start_time > timeout or len(results) >= 100: return
        
        if len(path) == max_len:
            results.append(list(path))
            return
        
        # 1. 前の単語の末尾を取得
        last_tail = get_clean_char(path[-1], "tail")
        # 2. 50音環状シフトを適用（例：ン → ア）
        required_head = shift_kana(last_tail, shift_n)

        for next_w in word_pool:
            if next_w in path: continue
            
            # 3. 次の単語の先頭と比較
            next_head = get_clean_char(next_w, "head")

            if next_head == required_head:
                pair = tuple(sorted([path[-1], next_w]))
                if exclude_conjugates and pair in used_pairs: continue
                
                new_used = used_pairs.copy()
                new_used.add(pair)
                solve(path + [next_w], new_used)

    # 探索開始
    sw = d.get('start_word')
    starts = [sw] if (sw in word_pool) else word_pool
    for w in starts:
        solve([w], set())

    return jsonify({"routes": results, "count": len(results)})
