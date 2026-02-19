import os, time, sys, re
from flask import Flask, render_template, request, jsonify

# 深い探索に対応
sys.setrecursionlimit(10000)
app = Flask(__name__)

KANA_LIST = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
VOICE_MAP = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")

def to_katakana(text):
    """ひらがなをカタカナに変換"""
    return "".join([chr(ord(c) + 96) if "ぁ" <= c <= "わ" else c for c in text])

# 辞書データ（国名と首都）
DICTIONARIES = {
    "country": ["アイスランド", "アイルランド", "アゼルバイジャン", "アフガニスタン", "アメリカ", "アラブシュチョウコクレンポウ", "アルジェリア", "アルゼンチン", "アルバニア", "アルメニア", "アンゴラ", "アンティグアバーブーダ", "アンドラ", "イエメン", "イギリス", "イスラエル", "イタリア", "イラク", "イラン", "インド", "インドネシア", "ウガンダ", "ウクライナ", "ウズベキスタン", "ウルグアイ", "エクアドル", "エジプト", "エストニア", "エスワティニ", "エチオピア", "エリトリア", "エルサルバドル", "オーストラリア", "オーストリア", "オマーン", "オランダ", "ガーナ", "カーボベルデ", "ガイアナ", "カザフスタン", "カタール", "カナダ", "ガボン", "カメルーン", "ガンビア", "カンボジア", "キタマケドニア", "ギニア", "ギニアビサウ", "キプロス", "キューバ", "ギリシャ", "キリバス", "キルギス", "グアテマラ", "クウェート", "クックショトウ", "グレナダ", "クロアチア", "ケニア", "コートジボワール", "コスタリカ", "コソボ", "コモロ", "コロンビア", "コンゴキョウワコク", "コンゴミンシュキョウワコク", "サウジアラビア", "サモア", "サントメプリンシペ", "ザンビア", "サンマリノ", "シエラレオネ", "ジブチ", "ジャマイカ", "ジョージア", "シリア", "シンガポール", "ジンバブエ", "スイス", "スウェーデン", "スーダン", "スペイン", "スリナム", "スリランカ", "スロバキア", "スロベニア", "セーシェル", "セキドウギニア", "セネガル", "セルビア", "セントクリストファーネービス", "セントビンセントグレナディーンショトウ", "セントルシア", "ソマリア", "ソロモンショトウ", "タイ", "ダイカンミンコク", "タジキスタン", "タンザニア", "チェコ", "チャド", "チュウオウアフリカ", "チュウカジンミンキョウワコク", "チュニジア", "チョウセンミンシュシュギジンミンキョウワコク", "チリ", "ツバル", "デンマーク", "ドイツ", "トーゴ", "ドミニカキョウワコク", "ドミニカコク", "トリニダードトバゴ", "トルクメニスタン", "トルコ", "トンガ", "ナイジェリア", "ナウル", "ナミビア", "ニウエ", "ニカラグア", "ニジェール", "ニホン", "ニュージーランド", "ネパール", "ノルウェー", "バーレーン", "ハイチ", "パキスタン", "バチカンシコク", "パナマ", "バヌアツ", "バハマ", "パプアニューギニア", "パラオ", "パラグアイ", "バルバドス", "ハンガリー", "バングラデシュ", "ヒガシティモール", "フィジー", "フィリピン", "フィンランド", "ブータン", "ブラジル", "フランス", "ブルガリア", "ブルキナファソ", "ブルネイ", "ブルンジ", "ベトナム", "ベナン", "ベネズエラ", "ベラルーシ", "ベリーズ", "ペルー", "ベルギー", "ポーランド", "ボスニアヘルツェゴビナ", "ボツワナ", "ボリビア", "ポルトガル", "ホンジュラス", "マーシャルショトウ", "マダガスカル", "マラウイ", "マリ", "マルタ", "マレーシア", "ミクロネシアレンポウ", "ミナミアフリカキョウワコク", "ミナミスーダン", "ミャンマー", "メキシコ", "モーリシャス", "モーリタニア", "モザンビーク", "モナコ", "モルディブ", "モルドバ", "モロッコ", "モンゴル", "モンテネグロ", "ヨルダン", "ラオス", "ラトビア", "リトアニア", "リビア", "リヒテンシュタイン", "リベリア", "ルーマニア", "ルクセンブルク", "ルワンダ", "レソト", "レバノン", "ロシア"],
    "capital": ["レイキャビク", "ダブリン", "バクー", "カブール", "ワシントン", "アブダビ", "アルジェ", "ブエノスアイレス", "ティラナ", "エレバン", "ルアンダ", "セントジョンズ", "アンドララベリャ", "サナア", "ロンドン", "エルサレム", "ローマ", "バグダッド", "テヘラン", "ジャカルタ", "カンパラ", "キーウ", "タシケント", "モンテビデオ", "キト", "カイロ", "タリン", "ムババーネ", "アディスアベバ", "アスマラ", "サンサルバドル", "キャンベラ", "ウィーン", "マスカット", "アムステルダム", "アクラ", "プライア", "ジョージタウン", "アスタナ", "ドーハ", "オタワ", "リーブルビル", "ヤウンデ", "バンジュール", "プノンペン", "スコピエ", "コナクリ", "ビサウ", "ニコシア", "ハバナ", "アテネ", "タラワ", "ビシュケク", "グアテマラシティ", "クウェートシティ", "アバルア", "セントジョージズ", "ザグレブ", "ナイロビ", "ヤムスクロ", "サンホセ", "プリシュティナ", "モロニ", "ボゴタ", "ブラザビル", "キンシャサ", "リヤド", "アピア", "サントメ", "ルサカ", "サンマリノ", "フリータウン", "ジブチ", "キングストン", "トビリシ", "ダマスカス", "シンガポール", "ハラレ", "ベルン", "ストックホルム", "ハルツーム", "マドリード", "パラマリボ", "スリジャヤワルダナプラコッテ", "ブラチスラバ", "リュブリャナ", "ビクトリア", "マラボ", "ダカール", "ベオグラード", "バセテール", "キングスタウン", "カストリーズ", "モガディシュ", "ホニアラ", "バンコク", "ソウル", "ドゥシャンベ", "ドドマ", "プラハ", "ヌジャメナ", "バンギ", "ペキン", "チュニス", "ピョンヤン", "サンティアゴ", "フナフティ", "コペンハーゲン", "ベルリン", "ロメ", "サントドミンゴ", "ロゾー", "ポートオブスペイン", "アシガバート", "アンカラ", "ヌクアロファ", "アブジャ", "アイウォ", "ウィントフック", "アロフィ", "マナグア", "ニアメ", "トウキョウ", "ウェリントン", "カトマンズ", "オスロ", "マナマ", "ポルトープランス", "イスラマバード", "バチカン", "パナマシティ", "ポートビラ", "ナッソー", "ポートモレスビー", "マルキョク", "アスンシオン", "ブリッジタウン", "ブダペスト", "ダッカ", "ディリ", "スバ", "マニラ", "ヘルシンキ", "ティンプー", "ブラジリア", "パリ", "ソフィア", "ワガドゥグ", "バンダルスリブガワン", "ギテガ", "ハノイ", "ポルトノボ", "カラカス", "ミンスク", "ベルモパン", "リマ", "ブリュッセル", "ワルシャワ", "サラエボ", "ハボローネ", "ラパス", "リスボン", "テグシガルパ", "マジュロ", "アンタナナリボ", "リロングウェ", "バマコ", "バレッタ", "クアラルンプール", "パリキール", "プレトリア", "ジュバ", "ネーピードー", "メキシコシティ", "ポートルイス", "ヌアクショット", "マプト", "モナコ", "マレ", "キシニョフ", "ラバト", "ウランバートル", "ポドゴリツァ", "アンマン", "ビエンチャン", "リガ", "ビリニュス", "トリポリ", "ファドゥーツ", "モンロビア", "ブカレスト", "ルクセンブルク", "キガリ", "マセル", "ベイルート", "モスクワ"]
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

@app.route('/get_dictionary')
def get_dictionary():
    return jsonify(DICTIONARIES)

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    max_len = min(int(d.get('max_len', 5)), 50)
    pos_shift = int(d.get('pos_shift', 0))
    kana_shift = int(d.get('kana_shift', 0))
    exclude_conjugates = d.get('exclude_conjugates', False)
    round_trip = d.get('round_trip', False)
    target_total_len = d.get('target_total_len')
    
    start_char = to_katakana(d.get('start_char', "")).translate(VOICE_MAP)
    end_char = to_katakana(d.get('end_char', "")).translate(VOICE_MAP)
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
