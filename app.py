import os
import time
import sys
from flask import Flask, render_template, request, jsonify

# 50単語以上の深い探索に備えて再帰限界を引き上げ
sys.setrecursionlimit(2000)

app = Flask(__name__)

# 50音環状リスト
KANA_LIST = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
VOICE_MAP = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")

# 辞書データ（自分用：ここへ自由に数千語追加可能）
DICTIONARIES = {
    "country": ["アイスランド", "アイルランド", "アメリカ", "アルゼンチン", "イタリア", "インドネシア", "ウガンダ", "エジプト", "オーストラリア", "カナダ", "カンボジア", "シンガポール", "スペイン", "タイ", "ドイツ", "ニホン", "パキスタン", "ブラジル", "フランス", "ベトナム", "メキシコ", "ロシア", "ンジャメナ"],
    "animal": ["アヒル", "イヌ", "ウサギ", "エナガ", "オオカミ", "カバ", "キリン", "パンダ", "ペンギン"],
    "custom": [] 
}

def get_clean_char(w, pos="head", offset=0):
    """物理的な位置ずらしと清音化を処理"""
    text = w.replace("ー", "")
    if pos == "head":
        char = text[offset] if len(text) > offset else text[0]
    else:
        char = text[-(1+offset)] if len(text) > offset else text[-1]
    return SMALL_TO_LARGE.get(char, char).translate(VOICE_MAP)

def shift_kana(char, n):
    """50音の環状スライドを実行"""
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
    pos_shift = int(d.get('pos_shift', 0))    # 物理位置(2文字目など)
    kana_shift = int(d.get('kana_shift', 0))  # 50音(ア→イなど)
    
    ignore_voiced = d.get('ignore_voiced', True)
    exclude_conjugates = d.get('exclude_conjugates', False)
    round_trip = d.get('round_trip', False)
    must_chars = [c.translate(VOICE_MAP) for c in d.get('must_char', "")]
    limit_one = d.get('limit_one', False)

    word_pool = []
    for cat in d.get('categories', ["country"]):
        word_pool.extend(DICTIONARIES.get(cat, []))
    word_pool = list(set(word_pool))

    results = []
    start_time = time.time()
    timeout = 15 # 15秒間フルパワー探索

    def solve(path, used_pairs):
        if time.time() - start_time > timeout or len(results) >= 100: return
        
        if len(path) == max_len:
            # 必須字フィルタの最終チェック
            if must_chars:
                full = "".join(path).translate(VOICE_MAP)
                if not all(mc in full for mc in must_chars): return
                if limit_one and not all(full.count(mc) == 1 for mc in must_chars): return
            results.append(list(path))
            return
        
        # 接続元の末尾取得 + 50音シフト適用
        last_tail = get_clean_char(path[-1], "tail", pos_shift)
        target_head = shift_kana(last_tail, kana_shift)

        for next_w in word_pool:
            # 往復(round_trip)設定による重複許可の制御
            if not round_trip and next_w in path: continue
            if round_trip and len(path) >= 1 and next_w == path[-1]: continue # 直前重複は禁止

            # 接続先の先頭取得
            if get_clean_char(next_w, "head", pos_shift) == target_head:
                pair = tuple(sorted([path[-1], next_w]))
                if exclude_conjugates and pair in used_pairs: continue
                
                new_used = used_pairs.copy()
                new_used.add(pair)
                solve(path + [next_w], new_used)

    sw = d.get('start_word')
    starts = [sw] if (sw in word_pool) else word_pool
    for w in starts:
        if len(results) >= 100: break
        solve([w], set())

    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
