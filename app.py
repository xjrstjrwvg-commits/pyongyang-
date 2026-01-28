import os
from flask import Flask, render_template, request, jsonify
from collections import Counter

app = Flask(__name__)

# 81文字環状構造
CHARS_CIRCLE = ["ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク", "ケ", "コ", "ガ", "ギ", "グ", "ゲ", "ゴ", "サ", "シ", "ス", "セ", "ソ", "ザ", "ジ", "ズ", "ゼ", "ゾ", "タ", "チ", "ツ", "テ", "ト", "ダ", "ヂ", "ヅ", "デ", "ド", "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ", "ヒ", "フ", "ヘ", "ホ", "バ", "ビ", "ブ", "ベ", "ボ", "パ", "ピ", "プ", "ペ", "ポ", "マ", "ミ", "ム", "メ", "モ", "ヤ", "ユ", "ヨ", "ラ", "リ", "ル", "レ", "ロ", "ワ", "ン"]
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ", "ヶ": "ケ", "ヵ": "カ"}
VOICE_MAP = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")

DATA_STORE = {
    "countries": ["アイスランド", "アイルランド", "アゼルバイジャン", "アフガニスタン", "アメリカ", "アラブシュチョウコクレンポウ", "アルジェリア", "アルゼンチン", "アルバニア", "アルメニア", "アンゴラ", "アンティグアバーブーダ", "アンドラ", "イエメン", "イギリス", "イスラエル", "イタリア", "イラク", "イラン", "インド", "インドネシア", "ウガンダ", "ウクライナ", "ウズベキスタン", "ウルグアイ", "エクアドル", "エジプト", "エストニア", "エスワティニ", "エチオピア", "エリトリア", "エルサルバドル", "オーストラリア", "オーストリア", "オマーン", "オランダ", "ガーナ", "カーボベルデ", "ガイアナ", "カザフスタン", "カタール", "カナダ", "ガボン", "カメルーン", "ガンビア", "カンボジア", "キタマケドニア", "ギニア", "ギニアビサウ", "キプロス", "キューバ", "ギリシャ", "キリバス", "キルギス", "グアテマラ", "クウェート", "クックショトウ", "グレナダ", "クロアチア", "ケニア", "コートジボワール", "コスタリカ", "コソボ", "コモロ", "コロンビア", "コンゴキョウワコク", "コンゴミンシュキョウワコク", "サウジアラビア", "サモア", "サントメプリンシペ", "ザンビア", "サンマリノ", "シエラレオネ", "ジブチ", "ジャマイカ", "ジョージア", "シリア", "シンガポール", "ジンバブエ", "スイス", "スウェーデン", "スーダン", "スペイン", "スリナム", "スリランカ", "スロバキア", "スロベニア", "セーシェル", "セキドウギニア", "セネガル", "セルビア", "セントクリストファーネービス", "セントビンセントグレナディーンショトウ", "セントルシア", "ソマリア", "ソロモンショトウ", "タイ", "ダイカンミンコク", "タジキスタン", "タンザニア", "チェコ", "チャド", "チュウオウアフリカ", "チュウカジンミンキョウワコク", "チュニジア", "チョウセンミンシュシュギジンミンキョウワコク", "チリ", "ツバル", "デンマーク", "ドイツ", "トーゴ", "ドミニカキョウワコク", "ドミニカコク", "トリニダードトバゴ", "トルクメニスタン", "トルコ", "トンガ", "ナイジェリア", "ナウル", "ナミビア", "ニウエ", "ニカラグア", "ニジェール", "ニホン", "ニュージーランド", "ネパール", "ノルウェー", "バーレーン", "ハイチ", "パキスタン", "バチカンシコク", "パナマ", "バヌアツ", "バハマ", "パプアニューギニア", "パラオ", "パラグアイ", "バルバドス", "ハンガリー", "バングラデシュ", "ヒガシティモール", "フィジー", "フィリピン", "フィンランド", "ブータン", "ブラジル", "フランス", "ブルガリア", "ブルキナファソ", "ブルネイ", "ブルンジ", "ベトナム", "ベナン", "ベネズエラ", "ベラルーシ", "ベリーズ", "ペルー", "ベルギー", "ポーランド", "ボスニアヘルツェゴビナ", "ボツワナ", "ボリビア", "ポルトガル", "ホンジュラス", "マーシャルショトウ", "マダガスカル", "マラウイ", "マリ", "マルタ", "マレーシア", "ミクロネシアレンポウ", "ミナミアフリカキョウワコク", "ミナミスーダン", "ミャンマー", "メキシコ", "モーリシャス", "モーリタニア", "モザンビーク", "モナコ", "モルディブ", "モルドバ", "モロッコ", "モンゴル", "モンテネグロ", "ヨルダン", "ラオス", "ラトビア", "リトアニア", "リビア", "リヒテンシュタイン", "リベリア", "ルーマニア", "ルクセンブルク", "ルワンダ", "レソト", "レバノン", "ロシア"],
    "capitals": ["アクラ", "アシガバット", "アスタナ", "アスマラ", "アスンシオン", "アディスアベバ", "アテネ", "アバルア", "アピア", "アブジャ", "アブダビ", "アムステルダム", "アルジェ", "アロフィ", "アンカラ", "アンタナナリボ", "アンドララベリャ", "アンマン", "イスラマバード", "ウィーン", "ウィントフック", "ウェリントン", "ウランバートル", "エルサレム", "エレバン", "オスロ", "オタワ", "カイロ", "カストリーズ", "カトマンズ", "カブール", "カラカス", "カンパラ", "キーウ", "キガリ", "キシナウ", "ギテガ", "キト", "キャンベラ", "キングスタウン", "キングストン", "キンシャサ", "グアテマラシティ", "クアラルンプール", "クウェート", "コナクリ", "コペンハーゲン", "ザグレブ", "サヌア", "サラエボ", "サンサルバドル", "サンティアゴ", "サントドミンゴ", "サントメ", "サンホセ", "サンマリノ", "ジブチ", "ジャカルタ", "ジュバ", "ジョージタウン", "シンガポール", "スコピエ", "ストックホルム", "スバ", "スリジャヤワルダナプラコッテ", "セントジョージズ", "セントジョンズ", "ソウル", "ソフィア", "ダカール", "タシケント", "ダッカ", "ダブリン", "ダマスカス", "タラワ", "タリン", "チュニス", "ティラナ", "ディリ", "ティンプー", "テグシガルパ", "テヘラン", "デリー", "トウキョウ", "ドゥシャンベ", "ドーハ", "ドドマ", "トビリシ", "トリポリ", "ナイロビ", "ナッソー", "ニアメ", "ニコシア", "ヌアクショット", "ヌクアロファ", "ネピドー", "バクー", "バグダッド", "バセテール", "パナマシティ", "バチカン", "ハノイ", "ハバナ", "ハボローネ", "バマコ", "パラマリボ", "ハラレ", "パリ", "パリキール", "ハルツーム", "バレッタ", "バンギ", "バンコク", "バンジュール", "バンダルスリブガワン", "ビエンチャン", "ビクトリア", "ビサウ", "ビシュケク", "ピョンヤン", "ビリニュス", "ファドゥーツ", "ブエノスアイレス", "ブカレスト", "ブダペスト", "フナフティ", "プノンペン", "プライア", "ブラザビル", "ブラジリア", "ブラチスラバ", "プラハ", "フリータウン", "プリシュティナ", "ブリッジタウン", "ブリュッセル", "プレトリア", "ベイルート", "ベオグラード", "ペキン", "ヘルシンキ", "ベルモパン", "ベルリン", "ベルン", "ポートオブスペイン", "ポートビラ", "ポートモレスビー", "ポートルイス", "ボゴタ", "ポドゴリツァ", "ホニアラ", "ポルトープランス", "ポルトノボ", "マジュロ", "マスカット", "マセル", "マドリード", "マナーマ", "マナグア", "マニラ", "マプト", "マラボ", "マルキョク", "マレ", "ミンスク", "ムババーネ", "メキシコシティ", "モガディシュ", "モスクワ", "モナコ", "モロニ", "モンテビデオ", "モンロビア", "ヤウンデ", "ヤムスクロ", "ヤレン", "ラパス", "ラバト", "リーブルビル", "リガ", "リスボン", "リマ", "リヤド", "リュブリャナ", "リロングウェ", "ルアンダ", "ルクセンブルク", "ルサカ", "レイキャビク", "ローマ", "ロゾー", "ロメ", "ロンドン", "ワガドゥグー", "ワシントンディーシー", "ワルシャワ", "ンジャメナ"]
}

def get_base_char(w, pos="head"):
    """文字を抽出して大文字化する（接続比較の土台）"""
    if not w: return ""
    w_clean = w.replace("ー", "").replace("・", "").replace(" ", "").replace("　", "")
    char = w_clean[0] if pos == "head" else w_clean[-1]
    return SMALL_TO_LARGE.get(char, char)

@app.route('/')
def index():
    return render_template('index.html', countries=DATA_STORE["countries"], capitals=DATA_STORE["capitals"])

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    ignore_voiced = d.get('ignore_voiced', False)
    category = d.get('category', 'both')
    word_configs = d.get('word_configs', {})
    shift = int(d.get('shift_count', 0))
    is_gyukou = d.get('is_gyukou', False)
    target_len = int(d.get('fixed_len_val', 3))
    
    start_char = d.get('start_char', "")
    must_chars = [c for c in d.get('must_char', "")]
    use_increasing = d.get('use_increasing', False)
    use_total_chars = d.get('use_total_chars', False)
    total_chars_val = int(d.get('total_chars_val', 15))

    # 検索用プールのフィルタリング
    base_pool = DATA_STORE["countries"] if category == "countries" else DATA_STORE["capitals"] if category == "capitals" else list(set(DATA_STORE["countries"] + DATA_STORE["capitals"]))
    pool = [w for w in base_pool if word_configs.get(w) != 2]
    must_words = [w for w, v in word_configs.items() if v == 1]

    results = []

    def solve(path):
        if len(results) >= 10000: return
        cur_len = len(path)
        
        # 指定語数に到達
        if cur_len == target_len:
            cur_txt = "".join(path)
            if use_total_chars and len(cur_txt) != total_chars_val: return
            
            # 条件判定用テキスト
            comp_txt = cur_txt.translate(VOICE_MAP) if ignore_voiced else cur_txt
            comp_must_chars = [c.translate(VOICE_MAP) if ignore_voiced else c for c in must_chars]
            
            if not all(mc in comp_txt for mc in comp_must_chars): return
            if not all(mw in path for mw in must_words): return
            results.append(list(path))
            return

        last_w = path[-1]
        # 前の単語の基準文字位置を決定
        base_pos = "head" if (is_gyukou and cur_len % 2 == 0) else "tail"
        base_c = get_base_char(last_w, base_pos)
        
        # 清音化設定に応じた比較用文字の生成
        search_c = base_c.translate(VOICE_MAP) if ignore_voiced else base_c
        
        # 環状リストからインデックスを取得（必ずCHARS_CIRCLE内にある文字で計算）
        idx_char = base_c if base_c in CHARS_CIRCLE else base_c.translate(VOICE_MAP)
        if idx_char not in CHARS_CIRCLE: return
        
        # ずらし適用後のターゲット文字（清音化設定を反映）
        target_c = CHARS_CIRCLE[(CHARS_CIRCLE.index(idx_char) + shift) % 81]
        if ignore_voiced: target_c = target_c.translate(VOICE_MAP)

        for next_w in pool:
            if next_w in path: continue
            if use_increasing and len(next_w) <= len(last_w): continue
            
            # 次の単語の基準文字位置を決定
            next_pos = "tail" if (is_gyukou and cur_len % 2 != 0) else "head"
            next_c = get_base_char(next_w, next_pos)
            
            # 比較
            comp_next = next_c.translate(VOICE_MAP) if ignore_voiced else next_c
            if comp_next == target_c:
                solve(path + [next_w])

    # 探索開始
    sw = d.get('start_word', "").strip()
    starts = [sw] if (sw and sw in pool) else pool
    for w in starts:
        if not sw and start_char:
            head_c = get_base_char(w, "head")
            comp_head = head_c.translate(VOICE_MAP) if ignore_voiced else head_c
            comp_start = start_char.translate(VOICE_MAP) if ignore_voiced else start_char
            if comp_head != comp_start: continue
        solve([w])

    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
