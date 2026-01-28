import os
from flask import Flask, render_template, request, jsonify
from collections import Counter

app = Flask(__name__)

# --- 2026 Edition: 順番表 (81文字環状構造) ---
CHARS_CIRCLE = ["ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク", "ケ", "コ", "ガ", "ギ", "グ", "ゲ", "ゴ", "サ", "シ", "ス", "セ", "ソ", "ザ", "ジ", "ズ", "ゼ", "ゾ", "タ", "チ", "ツ", "テ", "ト", "ダ", "ヂ", "ヅ", "デ", "ド", "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ", "ヒ", "フ", "ヘ", "ホ", "バ", "ビ", "ブ", "ベ", "ボ", "パ", "ピ", "プ", "ペ", "ポ", "マ", "ミ", "ム", "メ", "モ", "ヤ", "ユ", "ヨ", "ラ", "リ", "ル", "レ", "ロ", "ワ", "ン"]
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
VOICE_MAP = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")

# データベース（国名・首都名）
DATA_STORE = {
    "countries": ["アイスランド", "アイルランド", "アゼルバイジャン", "アフガニスタン", "アメリカ", "アラブシュチョウコクレンポウ", "アルジェリア", "アルゼンチン", "アルバニア", "アルメニア", "アンゴラ", "アンティグアバーブーダ", "アンドラ", "イエメン", "イギリス", "イスラエル", "イタリア", "イラク", "イラン", "インド", "インドネシア", "ウガンダ", "ウクライナ", "ウズベキスタン", "ウルグアイ", "エクアドル", "エジプト", "エストニア", "エスワティニ", "エチオピア", "エリトリア", "エルサルバドル", "オーストラリア", "オーストリア", "オマーン", "オランダ", "ガーナ", "カーボベルデ", "ガイアナ", "カザフスタン", "カタール", "カナダ", "ガボン", "カメルーン", "ガンビア", "カンボジア", "キタマケドニア", "ギニア", "ギニアビサウ", "キプロス", "キューバ", "ギリシャ", "キリバス", "キルギス", "グアテマラ", "クウェート", "クックショトウ", "グレナダ", "クロアチア", "ケニア", "コートジボワール", "コスタリカ", "コソボ", "コモロ", "コロンビア", "コンゴキョウワコク", "コンゴミンシュキョウワコク", "サウジアラビア", "サモア", "サントメプリンシペ", "ザンビア", "サンマリノ", "シエラレオネ", "ジブチ", "ジャマイカ", "ジョージア", "シリア", "シンガポール", "ジンバブエ", "スイス", "スウェーデン", "スーダン", "スペイン", "スリナム", "スリランカ", "スロバキア", "スロベニア", "セーシェル", "セキドウギニア", "セネガル", "セルビア", "セントクリストファーネービス", "セントビンセントグレナディーンショトウ", "セントルシア", "ソマリア", "ソロモンショトウ", "タイ", "ダイカンミンコク", "タジキスタン", "タンザニア", "チェコ", "チャド", "チュウオウアフリカ", "チュウカジンミンキョウワコク", "チュニジア", "チョウセンミンシュシュギジンミンキョウワコク", "チリ", "ツバル", "デンマーク", "ドイツ", "トーゴ", "ドミニカキョウワコク", "ドミニカコク", "トリニダードトバゴ", "トルクメニスタン", "トルコ", "トンガ", "ナイジェリア", "ナウル", "ナミビア", "ニウエ", "ニカラグア", "ニジェール", "ニホン", "ニュージーランド", "ネパール", "ノルウェー", "バーレーン", "ハイチ", "パキスタン", "バチカンシコク", "パナマ", "バヌアツ", "バハマ", "パプアニューギニア", "パラオ", "パラグアイ", "バルバドス", "ハンガリー", "バングラデシュ", "ヒガシティモール", "フィジー", "フィリピン", "フィンランド", "ブータン", "ブラジル", "フランス", "ブルガリア", "ブルキナファソ", "ブルネイ", "ブルンジ", "ベトナム", "ベナン", "ベネズエラ", "ベラルーシ", "ベリーズ", "ペルー", "ベルギー", "ポーランド", "ボスニアヘルツェゴビナ", "ボツワナ", "ボリビア", "ポルトガル", "ホンジュラス", "マーシャルショトウ", "マダガスカル", "マラウイ", "マリ", "マルタ", "マレーシア", "ミクロネシアレンポウ", "ミナミアフリカキョウワコク", "ミナミスーダン", "ミャンマー", "メキシコ", "モーリシャス", "モーリタニア", "モザンビーク", "モナコ", "モルディブ", "モルドバ", "モロッコ", "モンゴル", "モンテネグロ", "ヨルダン", "ラオス", "ラトビア", "リトアニア", "リビア", "リヒテンシュタイン", "リベリア", "ルーマニア", "ルクセンブルク", "ルワンダ", "レソト", "レバノン", "ロシア"],
    "capitals": ["アクラ", "アシガバット", "アスタナ", "アスマラ", "アスンシオン", "アディスアベバ", "アテネ", "アバルア", "アピア", "アブジャ", "アブダビ", "アムステルダム", "アルジェ", "アロフィ", "アンカラ", "アンタナナリボ", "アンドララベリャ", "アンマン", "イスラマバード", "ウィーン", "ウィントフック", "ウェリントン", "ウランバートル", "エルサレム", "エレバン", "オスロ", "オタワ", "カイロ", "カストリーズ", "カトマンズ", "カブール", "カラカス", "カンパラ", "キーウ", "キガリ", "キシナウ", "ギテガ", "キト", "キャンベラ", "キングスタウン", "キングストン", "キンシャサ", "グアテマラシティ", "クアラルンプール", "クウェート", "コナクリ", "コペンハーゲン", "ザグレブ", "サヌア", "サラエボ", "サンサルバドル", "サンティアゴ", "サントドミンゴ", "サントメ", "サンホセ", "サンマリノ", "ジブチ", "ジャカルタ", "ジュバ", "ジョージタウン", "シンガポール", "スコピエ", "ストックホルム", "スバ", "スリジャヤワルダナプラコッテ", "セントジョージズ", "セントジョンズ", "ソウル", "ソフィア", "ダカール", "タシケント", "ダッカ", "ダブリン", "ダマスカス", "タラワ", "タリン", "チュニス", "ティラナ", "ディリ", "ティンプー", "テグシガルパ", "テヘラン", "デリー", "トウキョウ", "ドゥシャンベ", "ドーハ", "ドドマ", "トビリシ", "トリポリ", "ナイロビ", "ナッソー", "ニアメ", "ニコシア", "ヌアクショット", "ヌクアロファ", "ネピドー", "バクー", "バグダッド", "バセテール", "パナマシティ", "バチカン", "ハノイ", "ハバナ", "ハボローネ", "バマコ", "パラマリボ", "ハラレ", "パリ", "パリキール", "ハルツーム", "バレッタ", "バンギ", "バンコク", "バンジュール", "バンダルスリブガワン", "ビエンチャン", "ビクトリア", "ビサウ", "ビシュケク", "ピョンヤン", "ビリニュス", "ファドゥーツ", "ブエノスアイレス", "ブカレスト", "ブダペスト", "フナフティ", "プノンペン", "プライア", "ブラザビル", "ブラジリア", "ブラチスラバ", "プラハ", "フリータウン", "プリシュティナ", "ブリッジタウン", "ブリュッセル", "プレトリア", "ベイルート", "ベオグラード", "ペキン", "ヘルシンキ", "ベルモパン", "ベルリン", "ベルン", "ポートオブスペイン", "ポートビラ", "ポートモレスビー", "ポートルイス", "ボゴタ", "ポドゴリツァ", "ホニアラ", "ポルトープランス", "ポルトノボ", "マジュロ", "マスカット", "マセル", "マドリード", "マナーマ", "マナグア", "マニラ", "マプト", "マラボ", "マルキョク", "マレ", "ミンスク", "ムババーネ", "メキシコシティ", "モガディシュ", "モスクワ", "モナコ", "モロニ", "モンテビデオ", "モンロビア", "ヤウンデ", "ヤムスクロ", "ヤレン", "ラパス", "ラバト", "リーブルビル", "リガ", "リスボン", "リマ", "リヤド", "リュブリャナ", "リロングウェ", "ルアンダ", "ルクセンブルク", "ルサカ", "レイキャビク", "ローマ", "ロゾー", "ロメ", "ロンドン", "ワガドゥグー", "ワシントンディーシー", "ワルシャワ", "ンジャメナ"]
}

def get_clean_char(w, ignore_voiced, pos="head"):
    if not w: return ""
    w_clean = w.replace("ー", "")
    if not w_clean: return ""
    char = w_clean if pos == "head" else w_clean[-1]
    res = SMALL_TO_LARGE.get(char, char)
    if ignore_voiced: res = res.translate(VOICE_MAP)
    return res

@app.route('/')
def index():
    return render_template('index.html', countries=DATA_STORE["countries"], capitals=DATA_STORE["capitals"])

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    ignore_voiced = d.get('ignore_voiced', False)
    exclude_dup = d.get('exclude_conjugate', False)
    category = d.get('category', 'both')
    word_configs = d.get('word_configs', {})
    shift = int(d.get('shift_count', 0))
    is_gyukou = d.get('is_gyukou', False)
    
    # 複数必須文字の処理
    must_chars = [c.translate(VOICE_MAP) if ignore_voiced else c for c in d.get('must_char', "")]
    start_char = d.get('start_char', "")
    if start_char and ignore_voiced: start_char = start_char.translate(VOICE_MAP)
    
    # 長さモード
    len_mode = d.get('len_mode', 'fixed')
    target_val = int(d.get('max_len', 5))

    # 検索対象プールの作成
    base_pool = DATA_STORE["countries"] if category == "countries" else DATA_STORE["capitals"] if category == "capitals" else list(set(DATA_STORE["countries"] + DATA_STORE["capitals"]))
    pool = [w for w in base_pool if word_configs.get(w) != 2]
    must_words = [w for w, v in word_configs.items() if v == 1]

    if exclude_dup:
        cnt = Counter((get_clean_char(w, ignore_voiced, "head"), get_clean_char(w, ignore_voiced, "tail")) for w in pool)
        pool = [w for w in pool if cnt[(get_clean_char(w, ignore_voiced, "head"), get_clean_char(w, ignore_voiced, "tail"))] == 1]

    results = []

    def solve(path):
        if len(results) >= 500: return
        
        current_text = "".join(path)
        current_len = len(path)
        current_total_chars = len(current_text)

        # 終了判定
        is_finish = False
        if len_mode == 'fixed' and current_len == target_val: is_finish = True
        elif len_mode == 'increasing' and current_len == target_val: is_finish = True
        elif len_mode == 'total_chars' and current_total_chars == target_val: is_finish = True
        
        if is_finish:
            # 必須要素の最終チェック
            if not all(m in path for m in must_words): return
            check_text = current_text.translate(VOICE_MAP if ignore_voiced else {})
            if not all(mc in check_text for mc in must_chars): return
            results.append(list(path))
            return

        # 枝切り
        if len_mode == 'total_chars' and current_total_chars > target_val: return
        if current_len >= 10: return

        last_w = path[-1]
        use_head = is_gyukou and (current_len % 2 == 0)
        base_c = get_clean_char(last_w, ignore_voiced, "head" if use_head else "tail")
        
        try:
            lookup_c = base_c.translate(VOICE_MAP) if base_c not in CHARS_CIRCLE else base_c
            idx = CHARS_CIRCLE.index(lookup_c)
            target = CHARS_CIRCLE[(idx + shift) % len(CHARS_CIRCLE)]
            if ignore_voiced: target = target.translate(VOICE_MAP)
            
            for next_w in pool:
                if next_w not in path:
                    # だんだん長くルール
                    if len_mode == 'increasing' and len(next_w) <= len(last_w): continue
                    
                    check_tail = is_gyukou and (current_len % 2 != 0)
                    next_c = get_clean_char(next_w, ignore_voiced, "tail" if check_tail else "head")
                    if next_c == target:
                        solve(path + [next_w])
        except: return

    sw = d.get('start_word')
    starts = [sw] if (sw and sw in pool) else pool
    for w in starts:
        if not sw and start_char and get_clean_char(w, ignore_voiced, "head") != start_char: continue
        solve([w])

    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
