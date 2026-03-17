import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from urllib.parse import quote
from supabase import create_client, Client
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import json
import io
import datetime
import hashlib
import os
import base64
from models import User, Qualification, Synergy, SynergyRequirement

# ----- AIチャット画面の勝手なリンク変換を防ぐためのURL復号関数 -----
def get_url(b64_str):
    return base64.b64decode(b64_str).decode('utf-8')

# データベース接続設定
DATABASE_URL = "sqlite:///app.db"

def get_engine():
    return create_engine(DATABASE_URL)

engine = get_engine()

def get_db_session():
    return Session(engine)

# ページ設定
st.set_page_config(page_title="Skill Radar Dashboard", layout="wide")

# ----- 資格の「出現確率（レア度）」辞書 -----
rarity_map = {
    "CBAP (ビジネスアナリシス・プロフェッショナル)": 69000,
    "メンタルヘルス・マネジメント検定 I種": 5750,
    "経営学検定 中級・上級": 4600,
    "中小企業診断士": 2300,
    "PMP (プロジェクトマネジメントプロフェッショナル)": 1725,
    "ビジネスマネジャー検定": 1533,
    "Google アナリティクス個人認定資格 (GAIQ)": 1380,
    "キャリアコンサルタント": 1047,
    "MBA (経営学修士)": 690,
    "メンタルヘルス・マネジメント検定 II種": 276,
    "秘書検定 2級": 19,
    "USCPA (米国公認会計士)": 5750,
    "CFP (サーティファイド・ファイナンシャル・プランナー)": 2760,
    "証券アナリスト": 2308,
    "公認会計士": 1941,
    "ビジネス会計検定 2級": 1725,
    "FP技能士1級": 1061,
    "税理士": 844,
    "日商簿記1級": 690,
    "AFP": 431,
    "FP技能士2級": 57,
    "日商簿記2級": 27,
    "FP技能士3級": 34,
    "日商簿記3級": 11,
    "弁理士": 5750,
    "司法書士": 3000,
    "弁護士": 1506,
    "社会保険労務士": 1486,
    "行政書士": 1303,
    "知的財産管理技能検定 2級": 1150,
    "ビジネス実務法務検定 2級": 345,
    "ビジネス実務法務検定 3級": 138,
    "第二種衛生管理者": 69,
    "第一種衛生管理者": 46,
    "Salesforce 認定テクニカルアーキテクト": 460000,
    "CCIE": 46000,
    "Oracle Master Platinum": 23000,
    "統計検定 準1級": 17250,
    "Google Cloud Professional Cloud Architect": 13800,
    "CISA (公認情報システム監査人)": 11500,
    "AWS Certified Solutions Architect - Professional": 8625,
    "E資格 (ディープラーニング)": 8625,
    "ITストラテジスト": 6900,
    "Python3エンジニア認定データ分析実践試験": 4600,
    "データサイエンティスト検定 (リテラシーレベル)": 3450,
    "情報処理安全確保支援士 (登録セキスペ)": 3136,
    "CCNP": 2300,
    "統計検定 3級": 2300,
    "Oracle Master Gold": 1725,
    "Salesforce 認定アドミニストレーター": 1725,
    "データベーススペシャリスト": 1533,
    "ネットワークスペシャリスト": 1380,
    "AWS Certified Solutions Architect - Associate": 1380,
    "G検定 (ジェネラリスト検定)": 690,
    "AWS Certified Cloud Practitioner": 690,
    "CCNA": 460,
    "Oracle Master Silver": 460,
    "応用情報技術者": 230,
    "Oracle Master Bronze": 230,
    "基本情報技術者": 57,
    "ITパスポート": 46,
    "TOEFL iBT 100点以上": 2300,
    "HSK 5級 (中国語)": 1725,
    "英検1級": 1380,
    "TOEIC 900点以上": 460,
    "英検準1級": 230,
    "TOEIC 800点以上": 172,
    "TOEIC 700点以上": 69,
    "TOEIC 600点以上": 27,
    "電験一種 (第一種電気主任技術者)": 11500,
    "電験二種 (第二種電気主任技術者)": 1971,
    "電気通信主任技術者": 862,
    "エネルギー管理士": 766,
    "工事担任者 (総合通信)": 460,
    "危険物取扱者 甲種": 276,
    "電験三種 (第三種電気主任技術者)": 197,
    "第一種電気工事士": 115,
    "第二種電気工事士": 19,
    "危険物取扱者 乙種4類": 13,
    "ボイラー技士 (特級)": 5750,
    "機械保全技能士 (特級)": 4600,
    "QC検定1級": 6900,
    "自主保全士 (1級)": 1380,
    "公害防止管理者 (大気1種/水質1種)": 862,
    "技術士 (機械部門/金属部門/経営工学部門等)": 690,
    "QC検定2級": 383,
    "機械保全技能士 (1級)": 276,
    "1級ボイラー技士": 230,
    "QC検定3級": 138,
    "2級ボイラー技士": 46,
    "測量士": 460,
    "1級電気工事施工管理技士": 345,
    "1級建築施工管理技士": 197,
    "一級建築士": 186,
    "1級土木施工管理技士": 172,
    "二級建築士": 88,
    "測量士補": 57,
    "2級施工管理技士 (各種)": 38,
    "不動産鑑定士": 8117,
    "認定ファシリティマネジャー": 4600,
    "マンション管理士": 1971,
    "管理業務主任者": 690,
    "建築物環境衛生管理技術者 (ビル管理士)": 627,
    "消防設備士 (甲種4類)": 230,
    "宅地建物取引士": 57
}

# ----- 戦闘力の巨大数値フォーマット関数 -----
def format_combat_power(num):
    if num >= 1e18:
        return f"{num / 1e18:.2f} Qi"
    elif num >= 1e15:
        return f"{num / 1e15:.2f} Qa"
    elif num >= 1e12:
        return f"{num / 1e12:.2f} T"
    elif num >= 1e9:
        return f"{num / 1e9:.2f} B"
    elif num >= 1e6:
        return f"{num / 1e6:.2f} M"
    elif num >= 1e3:
        return f"{num / 1e3:.2f} K"
    else:
        return f"{num:,}"

# ----- バッジのランク判定関数 -----
def get_badge_info(combat_power):
    if combat_power <= 5000:
        return "🪵 木 (Wood)"
    elif combat_power <= 50000:
        return "🥉 銅 (Bronze)"
    elif combat_power <= 500000:
        return "⚙️ 鉄 (Iron)"
    elif combat_power <= 5000000:
        return "🏗️ 鋼 (Steel)"
    elif combat_power <= 50000000:
        return "✈️ チタン (Titanium)"
    elif combat_power <= 100000000:
        return "💍 プラチナ (Platinum)"
    else:
        return "💎 ダイヤ (Diamond)"

# ----- テキスト中央配置用ヘルパー関数 -----
def draw_centered_text(draw, y, text, font, fill, canvas_width=600):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (canvas_width - text_width) / 2
    draw.text((x, y), text, fill=fill, font=font)

# ----- デジタル証明書 生成関数（スマホ最適化 600x320） -----
def generate_badge_image(combat_power, qual_count, synergy_count, badge_name, user_email):
    img = Image.new('RGB', (600, 320), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("NotoSansJP-Regular.ttf", 46)
        font_medium = ImageFont.truetype("NotoSansJP-Regular.ttf", 22)
        font_small = ImageFont.truetype("NotoSansJP-Regular.ttf", 14)
    except IOError:
        font_paths = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        ]
        font_large = font_medium = font_small = ImageFont.load_default()
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font_large = ImageFont.truetype(path, 46)
                    font_medium = ImageFont.truetype(path, 22)
                    font_small = ImageFont.truetype(path, 14)
                    break
                except:
                    continue

    draw.rectangle([(15, 15), (585, 305)], outline=(56, 189, 248), width=3)
    
    rank_clean = badge_name.split(" ")[-1].replace("(", "").replace(")", "").upper()
    stats_text = f"LICENSES: {qual_count}   |   SYNERGIES: {synergy_count}"
    display_cp = f"{format_combat_power(combat_power)} pt"

    draw_centered_text(draw, 35, "Skill Radar Official Certificate", font_small, (148, 163, 184), 600)
    draw_centered_text(draw, 80, f"RANK : {rank_clean}", font_large, (250, 204, 21), 600)
    draw_centered_text(draw, 150, stats_text, font_medium, (248, 250, 252), 600)
    draw_centered_text(draw, 210, display_cp, font_large, (56, 189, 248), 600)
    
    date_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    raw_str = f"{user_email}-{combat_power}-{date_str}"
    serial_no = hashlib.sha256(raw_str.encode()).hexdigest()[:12].upper()
    
    draw.text((35, 255), f"Issued: {date_str}", fill=(148, 163, 184), font=font_small)
    draw.text((35, 275), f"Serial: SR-{serial_no}", fill=(148, 163, 184), font=font_small)
    
    stamp_box = [(450, 240), (560, 290)]
    draw.rectangle(stamp_box, outline=(56, 189, 248), width=2)
    bbox = draw.textbbox((0, 0), "VERIFIED", font=font_small)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((stamp_box[0][0]+stamp_box[1][0])/2 - tw/2, (stamp_box[0][1]+stamp_box[1][1])/2 - th/2 - 2), "VERIFIED", fill=(56, 189, 248), font=font_small)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ----- Gemini API 認証 -----
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def parse_receipt_with_gemini(image):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """
        あなたは厳格な経理アシスタントです。添付されたnoteの購入レシート画像（またはメールのスクリーンショット）を解析し、
        以下のJSONフォーマットのみを絶対に出力してください。Markdownの```jsonなどの装飾も不要です。

        {
            "is_valid_receipt": true または false (noteの300円のレシートとして有効か),
            "order_number": "抽出した注文番号（note-から始まる番号など。なければ空文字）",
            "price": 300 (数値で抽出)
        }
        """
        response = model.generate_content([prompt, image])
        result_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(result_text)
    except Exception as e:
        return {"is_valid_receipt": False, "error": str(e)}

# ----- Supabase 認証 -----
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Supabase初期化エラー: {e}")
    st.stop()

st.sidebar.header("ユーザー認証")

if "user" not in st.session_state:
    st.session_state.user = None
if "is_premium" not in st.session_state:
    st.session_state.is_premium = False

# ログイン状態の確認とプレミアム判定
if st.session_state.user is None:
    tab1, tab2 = st.sidebar.tabs(["ログイン", "新規登録"])
    
    with tab1:
        login_email = st.text_input("メールアドレス", key="login_email")
        login_password = st.text_input("パスワード", type="password", key="login_password")
        
        if st.button("ログイン"):
            if login_email and login_password:
                try:
                    response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                    st.session_state.user = response.user
                    
                    res = supabase.table('used_receipts').select("*").eq('user_email', response.user.email).execute()
                    if len(res.data) > 0:
                        st.session_state.is_premium = True
                        
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"ログインエラー: メールアドレスかパスワードが違います。")
            else:
                st.sidebar.warning("メールアドレスとパスワードを入力してください。")
                
    with tab2:
        signup_email = st.text_input("メールアドレス", key="signup_email")
        signup_password = st.text_input("パスワード", type="password", key="signup_password")
        if st.button("新規登録"):
            if signup_email and signup_password:
                try:
                    response = supabase.auth.sign_up({"email": signup_email, "password": signup_password})
                    st.session_state.user = response.user
                    
                    res = supabase.table('used_receipts').select("*").eq('user_email', response.user.email).execute()
                    if len(res.data) > 0:
                        st.session_state.is_premium = True

                    st.sidebar.success("サインアップ成功！")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"サインアップエラー: {e}")
            else:
                st.sidebar.warning("メールアドレスとパスワードを入力してください。")
    st.sidebar.markdown("---")
else:
    st.sidebar.write(f"ログイン中: {st.session_state.user.email}")
    if st.session_state.is_premium:
        st.sidebar.success("👑 プレミアム会員")
        
    if st.sidebar.button("ログアウト"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state.user = None
        st.session_state.is_premium = False
        st.rerun()
    st.sidebar.markdown("---")

st.title("🛡️ 資格スコア & シナジー可視化ダッシュボード")
st.markdown("あなたが取得した資格を組み合わせて、**潜在戦闘力（レア度）**と**称号（シナジー）**を獲得しましょう！")
st.caption("※当ダッシュボードはアフィリエイトプログラムによる収益化を行っており、一部のリンクにはプロモーション（PR）が含まれます。")

# note記事URLの安全な取得（Base64による自動リンク化防止）
note_url_1 = get_url("aHR0cHM6Ly9ub3RlLmNvbS9ib2xkX3NuYWtlNzM3MS9uL25jY2EzN2NjODI0YWU=")
note_url_2 = get_url("aHR0cHM6Ly9ub3RlLmNvbS9ib2xkX3NuYWtlNzM3MS9uL243NjVhMWM2Zjk3M2U/YXBwX2xhdW5jaD1mYWxzZQ==")

# ----- 👑 プレミアム機能解放セクション -----
if not st.session_state.is_premium:
    with st.expander("👑 プレミアム機能の解放（称号・戦闘力ランキング・公式デジタルバッジの発行）", expanded=True):
        st.markdown(
            f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef;">
                <p style="font-weight: bold; color: #333; margin-bottom: 10px;">【プレミアム機能の解放手順】</p>
                <ol style="margin-bottom: 0;">
                    <li style="margin-bottom: 10px;">以下の<strong>いずれか</strong>のnote記事（300円）を購入します。<br>
                        👉 <a href="{note_url_1}" target="_blank" style="color: #0056b3; font-weight: bold; text-decoration: underline;">【悩み解決×網羅性】もうキャリアで迷わない。「資格の掛け算」で潜在戦闘力を可視化するレーダー</a><br>
                        👉 <a href="{note_url_2}" target="_blank" style="color: #0056b3; font-weight: bold; text-decoration: underline;">【完全実録】田舎生まれ田舎育ちの凡人が、上場企業の執行役員になれた「資格の掛け算」の法則</a>
                    </li>
                    <li style="margin-bottom: 10px;">購入完了画面、または届いたメールのスクリーンショットを撮影します。</li>
                    <li>下の枠に画像をアップロードしてください。AIが自動判定し、即座にアカウントをアップグレードします！</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader("📸 noteのレシート画像をアップロード", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされた画像", use_container_width=True)

            if st.button("AIでレシートを判定して解放する！", type="primary"):
                if st.session_state.user is None:
                    st.error("⚠️ 先にサイドバーからログイン（または無料登録）を完了させてください。")
                else:
                    with st.spinner("🤖 AIがレシートを解析しています...（数秒かかります）"):
                        receipt_data = parse_receipt_with_gemini(image)

                        if receipt_data.get("is_valid_receipt") and str(receipt_data.get("price")) == "300":
                            order_num = receipt_data.get("order_number")

                            if not order_num:
                                st.error("❌ 注文番号が読み取れませんでした。鮮明な画像をアップロードしてください。")
                            else:
                                res = supabase.table('used_receipts').select("*").eq('order_number', order_num).execute()

                                if len(res.data) > 0:
                                    st.error("⚠️ この注文番号のレシートは、すでに使用されています。")
                                else:
                                    supabase.table('used_receipts').insert({
                                        "order_number": order_num,
                                        "user_email": st.session_state.user.email
                                    }).execute()

                                    st.session_state.is_premium = True
                                    st.balloons()
                                    st.success("✅ レシートが承認されました！あなたのアカウントはプレミアム会員にアップグレードされました！")
                                    st.rerun()
                        else:
                            st.error("❌ 有効なnoteのレシート（300円）が確認できませんでした。")
                            st.info("💡 何度試してもエラーになってしまう場合は、お手数ですが公式XのDMにレシート画像をお送りください。運営が手動で解放いたします！")
    st.markdown("---")

# 1. データの読み込み
with get_db_session() as session:
    user = session.query(User).filter_by(username="test_user").first()
    if not user:
        st.error("test_user が見つかりませんでした。`seed.py` を実行してください。")
        st.stop()
        
    all_qualifications = session.query(Qualification).all()
    all_synergies = session.query(Synergy).all()
    
    for q in all_qualifications:
        if q.category == "不動産・施設管理":
            q.category = "不動産管理"
        if "技術士" in q.name:
            q.category = "建築・土木"
            
    for syn in all_synergies:
        for req in syn.requirements:
            if req.required_category == "不動産・施設管理":
                req.required_category = "不動産管理"
    
    all_qualifications.sort(key=lambda q: (q.category, q.tier, q.name))
    qual_options = {q.name: q for q in all_qualifications}
    
    if "selected_quals_set" not in st.session_state:
        st.session_state.selected_quals_set = set()

    def toggle_qual(qual_name):
        is_checked = st.session_state[f"chk_{qual_name}"]
        if is_checked:
            st.session_state.selected_quals_set.add(qual_name)
        else:
            st.session_state.selected_quals_set.discard(qual_name)

    def remove_qual(qual_name):
        st.session_state.selected_quals_set.discard(qual_name)

    st.sidebar.header("🎯 選択中の資格リスト")
    
    if st.session_state.selected_quals_set:
        for q_name in sorted(st.session_state.selected_quals_set):
            st.sidebar.button(f"❌ {q_name}", key=f"rm_{q_name}", on_click=remove_qual, args=(q_name,), help="クリックで選択を解除")
    else:
        st.sidebar.info("取得済みの資格がまだありません。下のリストから探しましょう！")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 資格を探す・追加する")
    
    if not st.session_state.is_premium:
        if len(st.session_state.selected_quals_set) >= 1:
            st.sidebar.warning("🔒 2つ目以上の資格登録・シナジー解析はプレミアム限定です。")
        else:
            st.sidebar.info("💡 無料版では資格を1つだけ登録できます。")

    search_query = st.sidebar.text_input("資格名で検索...", placeholder="例: ITパスポート")

    if search_query:
        st.sidebar.markdown("**検索結果**")
        results = [q for q_name, q in qual_options.items() if search_query.lower() in q_name.lower()]
        if not results:
            st.sidebar.write("一致する資格がありません")
        else:
            for q in results:
                disable_checkbox = (not st.session_state.is_premium) and (len(st.session_state.selected_quals_set) >= 1) and (q.name not in st.session_state.selected_quals_set)
                st.sidebar.checkbox(
                    q.name,
                    value=(q.name in st.session_state.selected_quals_set),
                    key=f"chk_{q.name}",
                    on_change=toggle_qual,
                    args=(q.name,),
                    disabled=disable_checkbox
                )
    else:
        categories = []
        for q in all_qualifications:
            if q.category not in categories:
                categories.append(q.category)
                
        selected_category = st.sidebar.selectbox("📂 カテゴリで絞り込む", categories)
        st.sidebar.markdown(f"**【{selected_category}】の資格一覧**")
        
        for q in all_qualifications:
            if q.category == selected_category:
                disable_checkbox = (not st.session_state.is_premium) and (len(st.session_state.selected_quals_set) >= 1) and (q.name not in st.session_state.selected_quals_set)
                st.sidebar.checkbox(
                    q.name,
                    value=(q.name in st.session_state.selected_quals_set),
                    key=f"chk_{q.name}",
                    on_change=toggle_qual,
                    args=(q.name,),
                    disabled=disable_checkbox
                )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 リストにない資格の追加リクエストは、公式X(Twitter)のDM等でいつでもお待ちしています！")

    selected_quals = [qual_options[name] for name in st.session_state.selected_quals_set if name in qual_options]
    selected_qual_ids = [q.id for q in selected_quals]
    selected_categories = [q.category for q in selected_quals]

# 2. 基礎スコア・シナジー・潜在戦闘力（レア度）の計算
base_score_total = sum(q.base_score for q in selected_quals)
bonus_score_total = 0
active_titles = []

for syn in all_synergies:
    requirements = syn.requirements
    if not requirements:
        continue
    
    synergy_achieved = True
    categories_available = list(selected_categories)
    
    for req in requirements:
        req_met = False
        if req.required_qualification_id and req.required_qualification_id in selected_qual_ids:
            req_met = True
        elif req.required_category and req.required_category in categories_available:
            req_met = True
        
        if not req_met:
            synergy_achieved = False
            break
            
    if synergy_achieved:
        bonus_score_total += syn.bonus_score
        active_titles.append(syn.title_name)

category_rarity_sums = {}
for q in selected_quals:
    cat = q.category
    r_score = rarity_map.get(q.name, 50) 
    if cat not in category_rarity_sums:
        category_rarity_sums[cat] = 0
    category_rarity_sums[cat] += r_score

combat_power = 1 if category_rarity_sums else 0
for r_sum in category_rarity_sums.values():
    combat_power *= r_sum

total_score = base_score_total + bonus_score_total
current_title = ", ".join(active_titles) if active_titles else "ルーキー"

# プレミアム制御・バッジ判定
if st.session_state.is_premium:
    badge_name = get_badge_info(combat_power)
    display_title = current_title
    display_total_score = f"{total_score} pt"
    display_bonus_detail = f"(基本: {base_score_total} + ボーナス: {bonus_score_total})"
    display_combat_power = f"{format_combat_power(combat_power)}"
    tweet_text = f"私の潜在戦闘力は『 {display_combat_power} 』！！\n最高レアリティ【{badge_name}】を獲得しました！🛡️\n\n称号：{display_title}\n異分野スキルの掛け合わせで、自分の市場価値を測ろう！\n#資格レーダー #戦闘力測定 #資格は登録した"
else:
    badge_name = "🔒 プレミアム限定"
    display_title = "🔒 プレミアム限定"
    display_total_score = f"{base_score_total} pt + 🔒"
    display_bonus_detail = f"(基本: {base_score_total} + ボーナス: 🔒プレミアム限定)"
    display_combat_power = "🔒 測定不能"
    tweet_text = f"私の潜在戦闘力（レア度）は 🔒 測定不能！\n異分野の資格を掛け合わせて、自分の本当の市場価値を測ろう！\n#資格レーダー #戦闘力測定 #スキルスコア #資格は登録した"

# 3. ダッシュボードへのスコア表示
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌟 総合スコア", display_total_score, display_bonus_detail)
col2.metric("👑 現在の称号", display_title)
col3.metric("🔥 潜在戦闘力", display_combat_power, badge_name if st.session_state.is_premium else "限界突破！？")
col4.metric("🎓 選択資格数", f"{len(selected_quals)} 個")

# Xへのシェアリンク安全取得
twitter_base = get_url("aHR0cHM6Ly90d2l0dGVyLmNvbS9pbnRlbnQvdHdlZXQ/dGV4dD0=")
intent_url = twitter_base + quote(tweet_text)
st.link_button("𝕏 で戦闘力をシェアする（画像添付がおすすめ！）", intent_url, type="primary")

st.markdown("---")

# ----- 📜 デジタル証明書（バッジ画像）発行セクション -----
st.subheader("📜 公式デジタルバッジ（証明書）の発行")
st.write("あなたの戦闘力と称号を証明する、偽造防止シリアルナンバー入りの公式デジタルバッジ画像を生成します。生成した画像をダウンロードして、上のボタンから𝕏に添付してシェアしましょう！")

if st.session_state.is_premium:
    if st.button("✨ バッジ画像を生成する", type="primary"):
        with st.spinner("証明書を生成中..."):
            img_bytes = generate_badge_image(
                combat_power, 
                len(selected_quals), 
                len(active_titles), 
                badge_name, 
                st.session_state.user.email
            )
            st.image(img_bytes, caption="あなたの公式デジタルバッジ（長押し、または右クリックでも保存できます）")
            st.download_button(
                label="📥 画像をダウンロード",
                data=img_bytes,
                file_name=f"skill_radar_badge_{combat_power}.png",
                mime="image/png"
            )
else:
    st.info("🔒 プレミアム機能を開放すると、あなたの戦闘力とレアリティを証明する「シリアルナンバー入り・デジタルバッジ画像」を発行できるようになります！")

st.markdown("---")

# 4. レーダーチャートの描画と選択リスト表示
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📊 スキルカテゴリ別 レーダーチャート")
    if selected_quals:
        category_scores_dict = {}
        for q in all_qualifications: 
            if q.category not in category_scores_dict:
                 category_scores_dict[q.category] = 0
                 
        for q in selected_quals:
            category_scores_dict[q.category] += q.base_score
            
        df_radar = pd.DataFrame(dict(
            category=list(category_scores_dict.keys()),
            score=list(category_scores_dict.values())
        ))
        
        fig = px.line_polar(
            df_radar, r='score', theta='category', line_close=True, markers=True, template="plotly_dark"
        )
        fig.update_traces(fill='toself')
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(100, df_radar['score'].max() + 20)])),
            showlegend=False, margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👈 サイドバーから資格を選択すると、レーダーチャートが表示されます。")

with col_right:
    st.subheader("🧾 取得済みの資格一覧")
    if selected_quals:
        df_quals = pd.DataFrame([
            {"資格名": q.name, "カテゴリ": q.category, "Tier": f"Tier {q.tier}", "スコア": q.base_score}
            for q in selected_quals
        ])
        st.dataframe(df_quals, use_container_width=True, hide_index=True)
        
        if active_titles:
            st.success("🎉 **発動中のシナジー**\n\n" + "\n".join([f"- **{t if st.session_state.is_premium else '🔒 プレミアム限定'}**" for t in active_titles]))
    else:
        st.write("選択された資格がありません。")

st.markdown("---")

# 5. アフィリエイトレコメンド機能（次の目標）
st.subheader("🎯 次の目標（おすすめの資格）")

category_amazon_keyword = {
    "IT・データ": "IT 資格", "経営・ビジネス": "ビジネス 資格", "法務・労務・知財": "法務 労務 資格",
    "財務・金融": "財務 金融 資格", "語学・グローバル": "語学 英語 資格", "機械・電気": "機械 電気 資格",
    "機械・製造": "機械 資格", "建築・土木": "建築 土木 資格", "電気・通信・エネ": "電気 通信 資格",
    "安全・環境・品質": "安全衛生 品質 資格", "不動産管理": "不動産管理 資格"
}

reach_synergies = []
for syn in all_synergies:
    if syn.title_name in active_titles:
        continue
    requirements = syn.requirements
    if not requirements:
        continue
    met_count = 0
    missing_reqs = []
    for req in requirements:
        req_met = False
        if req.required_qualification_id and req.required_qualification_id in selected_qual_ids:
            req_met = True
        elif req.required_category and req.required_category in selected_categories:
            req_met = True
        if req_met:
            met_count += 1
        else:
            missing_reqs.append(req)
            
    if met_count > 0 and len(missing_reqs) > 0:
        reach_synergies.append((syn, missing_reqs))

amazon_search_base = get_url("aHR0cHM6Ly93d3cuYW1hem9uLmNvLmpwL3M/az0=")

if reach_synergies:
    for syn, missing_reqs in reach_synergies:
        first_missing = missing_reqs[0]
        display_syn_title = syn.title_name if st.session_state.is_premium else "🔒プレミアム限定"
        
        if first_missing.required_qualification_id:
            quali = next((q for q in all_qualifications if q.id == first_missing.required_qualification_id), None)
            missing_text = f"【{quali.name}】" if quali else "特定の資格"
            st.info(f"あと{missing_text}を取得すれば、称号『{display_syn_title} (+{syn.bonus_score}pt)』が発動します！")
            
            if quali:
                if quali.affiliate_link and quali.affiliate_link.startswith("http"):
                    st.link_button(f"👉 【PR】 {quali.name} のおすすめ講座をチェック", quali.affiliate_link)
                else:
                    amz_kw = quote(quali.name + " 資格 テキスト")
                    amazon_url = f"{amazon_search_base}{amz_kw}&tag=skillradar-22"
                    st.link_button(f"👉 【PR】 {quali.name} の公式テキスト・過去問を探す", amazon_url)

        elif first_missing.required_category:
            missing_text = f"【{first_missing.required_category}】領域の資格"
            st.info(f"あと{missing_text}を取得すれば、称号『{display_syn_title} (+{syn.bonus_score}pt)』が発動します！")
            
            recommended_qual = next((q for q in all_qualifications if q.category == first_missing.required_category and q.affiliate_link), None)
            if recommended_qual:
                st.write(f"おすすめ: **{recommended_qual.name}**")
                if recommended_qual.affiliate_link.startswith("http"):
                    st.link_button(f"👉 【PR】 {recommended_qual.name} のおすすめ講座をチェック", recommended_qual.affiliate_link)
            else:
                base_keyword = category_amazon_keyword.get(first_missing.required_category, first_missing.required_category.replace("・", " ") + " 資格")
                amz_kw_cat = quote(base_keyword + " テキスト")
                amazon_url = f"{amazon_search_base}{amz_kw_cat}&tag=skillradar-22"
                st.link_button(f"👉 【PR】 【{first_missing.required_category}】領域の資格テキストを探す", amazon_url)
else:
    st.write("さらに別のカテゴリの資格を取得して、新たなシナジーを見つけましょう！")

st.markdown("---")

# 6. バーチャルランキングボード
st.subheader("🏆 全国戦闘力ランキング (仮想)")

dummy_rivals = [
    {"ユーザー": "資格マニア太郎", "称号": "重厚長大DXマスター", "戦闘力": 285400000},
    {"ユーザー": "プラント神", "称号": "プラント・エネルギー戦略家", "戦闘力": 15600000},
    {"ユーザー": "ビジネスの鬼", "称号": "AI主導型・経営参謀", "戦闘力": 8200000},
    {"ユーザー": "データサイエンス職人", "称号": "データサイエンティスト", "戦闘力": 520000},
    {"ユーザー": "駆け出しエンジニア", "称号": "DX推進アソシエイト", "戦闘力": 12800},
    {"ユーザー": "ITパスポート親方", "称号": "ルーキー", "戦闘力": 46},
]

ranking_data = dummy_rivals.copy()

if st.session_state.is_premium:
    ranking_data.append({
        "ユーザー": f"🟢 あなた",
        "称号": display_title,
        "戦闘力": combat_power
    })
    ranking_data_sorted = sorted(ranking_data, key=lambda x: x["戦闘力"], reverse=True)
    for r in ranking_data_sorted:
        r["戦闘力"] = f"{r['戦闘力']:,}"
        
    df_ranking = pd.DataFrame(ranking_data_sorted)
    df_ranking.index = [f"{i+1}位" for i in range(len(df_ranking))]
    df_ranking.index.name = "順位"
else:
    ranking_data_sorted = sorted(ranking_data, key=lambda x: x["戦闘力"], reverse=True)
    for i in range(len(ranking_data_sorted)):
        if i >= 3:
            ranking_data_sorted[i]["ユーザー"] = "🔒 プレミアム限定"
            ranking_data_sorted[i]["称号"] = "🔒"
            ranking_data_sorted[i]["戦闘力"] = "🔒"
        else:
            ranking_data_sorted[i]["戦闘力"] = f"{ranking_data_sorted[i]['戦闘力']:,}"
            
    df_ranking = pd.DataFrame(ranking_data_sorted)
    df_ranking.index = [f"{i+1}位" for i in range(len(df_ranking))]
    df_ranking.index.name = "順位"
    
    user_row = pd.DataFrame({
        "ユーザー": ["🟢 あなた"],
        "称号": ["🔒 プレミアム限定"],
        "戦闘力": ["🔒"]
    }, index=["???位"])
    df_ranking = pd.concat([df_ranking, user_row])

st.dataframe(df_ranking, use_container_width=True)
st.caption("Amazonのアソシエイトとして、当メディアは適格販売により収入を得ています。")

# キャリア相談セクション
st.markdown("---")
st.subheader("🚀 診断結果を活かしてキャリアの可能性を探る")

neuro_dive_url = get_url("aHR0cHM6Ly9weC5hOC5uZXQvc3Z0L2VqcD9hOG1hdD00QVpEODcrNEFTUkxVKzQ3R1MrSFZGS1k=")
neuro_dive_html = f'''
<div style="text-align: center; margin: 20px 0; padding: 15px; background-color: #f0f7ff; border: 1px solid #cce5ff; border-radius: 8px;">
    <p style="font-weight: bold; color: #004085; margin-bottom: 10px; font-size: 16px;">
        ＼ AIやデータサイエンス領域で、さらに市場価値を高めるなら ／
    </p>
    <div style="font-size: 18px; font-weight: bold;">
        <a href="{neuro_dive_url}" target="_blank" rel="nofollow" style="color: #0056b3; text-decoration: underline;">AIやデータサイエンスが学べるIT特化の就労移行支援【Neuro Dive】</a>
    </div>
</div>
'''
st.markdown(neuro_dive_html, unsafe_allow_html=True)

# 📚 おすすめ書籍セクション
st.markdown("---")
st.subheader("📚 キャリア戦略を深める必読書")
book_html = '''
<div style="padding: 20px; background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; margin-bottom: 20px;">
    <p style="font-weight: bold; color: #333; margin-bottom: 10px; font-size: 16px;">
        ＼ 当アプリのコンセプト「100万分の1の希少人材」の理論を深く学ぶなら ／
    </p>
    <p style="font-size: 14px; color: #555; margin-bottom: 0px;">
        note記事や本ダッシュボードで解説している「スキルの掛け算」によるキャリア戦略の根幹となる、藤原和博氏の名著です。これからの時代を生き抜くための人生戦略が詰まっています。
    </p>
</div>
'''
st.markdown(book_html, unsafe_allow_html=True)

amazon_book_url = get_url("aHR0cHM6Ly93d3cuYW1hem9uLmNvLmpwL2RwLzQ0NzgxMDk0Nlg/dGFnPXNraWxscmFkYXItMjI=")
st.link_button("👉 【PR】 藤原和博『100万人に1人の存在になる方法』をAmazonでチェック", amazon_book_url, type="primary")

# 🔥 資格スクエア バナーセクション
st.markdown("---")
st.subheader("🎓 難関資格の学習を最短で突破するなら")

sq_link = get_url("aHR0cHM6Ly9weC5hOC5uZXQvc3Z0L2VqcD9hOG1hdD00QVpCTzUrOVFPRE1RKzM3M0MrNkI3MEg=")
sq_img1 = get_url("aHR0cHM6Ly93d3cyOS5hOC5uZXQvc3Z0L2JndD9haWQ9MjYwMzA4OTQ5NTg5JndpZD0wMDMmZW5vPTAxJm1pZD1zMDAwMDAwMTQ5MTYwMDEwNjAwMDAmbWM9MQ==")
sq_img2 = get_url("aHR0cHM6Ly93d3cxNy5hOC5uZXQvMC5naWY/YThtYXQ9NEFaQk81KzlRT0RNUSszNzJDKzZCNzBI")

shikaku_square_html = f'''
<div style="text-align: center; margin: 20px 0;">
    <p style="font-size: 14px; color: #555; margin-bottom: 10px;">＼ 法律・会計系の難関資格に挑戦して戦闘力を引き上げる ／</p>
    <a href="{sq_link}" rel="nofollow" target="_blank">
    <img border="0" width="300" height="250" alt="" src="{sq_img1}"></a>
    <img border="0" width="1" height="1" src="{sq_img2}" alt="">
</div>
'''
st.markdown(shikaku_square_html, unsafe_allow_html=True)

# 🔥 PCアフィリエイトセクション
st.markdown("---")
st.subheader("💻 学習・開発環境のアップデート")
st.write("DX推進や学習効率を最大化する、推奨PCブランドをチェック。")

hp_link = get_url("aHR0cHM6Ly9jbGljay5saW5rc3luZXJneS5jb20vZnMtYmluL2NsaWNrP2lkPXl3NTdITGd6cEJ3Jm9mZmVyaWQ9MjUyOTI2Ljc2MSZ0eXBlPTQmc3ViaWQ9MA==")
hp_img1 = get_url("aHR0cHM6Ly9qcC5leHQuaHAuY29tL2NvbnRlbnQvZGFtL2pwLWV4dC1ocC1jb20vanAvamEvZWMvZGlyZWN0cGx1cy9hZmZfYmFubmVyL1dlZWtlbmRfMjM0eDYwLmpwZw==")
hp_img2 = get_url("aHR0cHM6Ly9hZC5saW5rc3luZXJneS5jb20vZnMtYmluL3Nob3c/aWQ9eXc1N0hMZ3pwQncmYmlkcz0yNTI5MjYuNzYxJnR5cGU9NCZzdWJpZD0w")

dell_link = get_url("aHR0cHM6Ly9jbGljay5saW5rc3luZXJneS5jb20vZnMtYmluL2NsaWNrP2lkPXl3NTdITGd6cEJ3Jm9mZmVyaWQ9MzkyNTAuMTAwMDAxMjMmdHlwZT00JnN1YmlkPTA=")
dell_img1 = get_url("aHR0cHM6Ly9pLmRlbGwuY29tL2ltYWdlcy9qcC9iYW5uZXJzL2Jhbm5lcnNfbC9jYW1wYWlnbjFfNDAweDEwMC5naWY=")
dell_img2 = get_url("aHR0cHM6Ly9hZC5saW5rc3luZXJneS5jb20vZnMtYmluL3Nob3c/aWQ9eXc1N0hMZ3pwQncmYmlkcz0zOTI1MC4xMDAwMDEyMyZ0eXBlPTQmc3ViaWQ9MA==")

pc_banners_html = f'''
<div style="display: flex; flex-wrap: wrap; justify-content: space-evenly; align-items: center; gap: 20px; margin: 20px 0;">
    <div style="text-align: center;">
        <a href="{hp_link}" target="_blank">
            <IMG alt="HP Directplus -HP公式オンラインストア-" border="0" src="{hp_img1}">
        </a>
        <IMG border="0" width="1" height="1" src="{hp_img2}">
    </div>
    <div style="text-align: center;">
        <a href="{dell_link}" target="_blank">
            <IMG alt="デル株式会社" border="0" src="{dell_img1}">
        </a>
        <IMG border="0" width="1" height="1" src="{dell_img2}">
    </div>
</div>
'''
st.markdown(pc_banners_html, unsafe_allow_html=True)

st.caption("※当メディアはアフィリエイトプログラムにより適格販売から収入を得ています。")