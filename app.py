import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from urllib.parse import quote
from models import User, Qualification, Synergy, SynergyRequirement

# データベース接続設定
DATABASE_URL = "sqlite:///app.db"

def get_engine():
    return create_engine(DATABASE_URL)

engine = get_engine()

def get_db_session():
    return Session(engine)

# ページ設定
st.set_page_config(page_title="Skill Radar Dashboard", layout="wide")

@st.dialog("資格の追加審査フロー")
def request_qualification_dialog():
    st.markdown("当データベースにない資格でも、ビジネス市場価値が高いものは運営の審査を経て追加・スコア化されます。")
    st.markdown("1. 下の決済ボタン(Stripe)から審査・登録料（500円）をお支払いください。決済画面の入力欄に「希望する資格名」をご記入いただきます。")
    st.markdown("2. 運営チーム（AI含む）が市場価値を調査し、Tierとスコアを決定の上、データベースに追加します。")
    st.markdown("3. 登録完了後、決済時にご入力いただいたメールアドレス宛に結果をご連絡いたします。（※万が一、審査基準を満たさず追加見送りとなった場合は全額返金いたします）")
    st.link_button("Stripeで決済してリクエストする", "https://buy.stripe.com/test_link", type="primary")


st.title("🛡️ 資格スコア & シナジー可視化ダッシュボード")
st.markdown("あなたが取得した資格を組み合わせて、**総スコア**と**称号（シナジー）**を獲得しましょう！")
st.caption("※当ダッシュボードはアフィリエイトプログラムによる収益化を行っており、一部のリンクにはプロモーション（PR）が含まれます。")

# 1. データの読み込み
with get_db_session() as session:
    # ユーザーシミュレーション
    user = session.query(User).filter_by(username="test_user").first()
    if not user:
        st.error("test_user が見つかりませんでした。`seed.py` を実行して初期データを作成してください。")
        st.stop()
        
    st.sidebar.markdown(f"**ログイン中**: 👤 {user.username}")
    st.sidebar.markdown("---")
    
    # 資格マスターとシナジーマスターの取得
    all_qualifications = session.query(Qualification).all()
    all_synergies = session.query(Synergy).all()
    
    # ここで先にシナジーのリレーションを読み込んでおく（DetachedInstanceError対策）
    for syn in all_synergies:
        _ = syn.requirements
    
    # 資格選択用の辞書作成（カテゴリごと、かつTier順で探しやすくする）
    all_qualifications.sort(key=lambda q: (q.category, q.tier, q.name))
    qual_options = {q.name: q for q in all_qualifications}
    
    # 初期状態として選択済み資格のセットを session_state に保存する
    if "selected_quals_set" not in st.session_state:
        st.session_state.selected_quals_set = set()

    # チェックボックス操作時のコールバック関数
    def toggle_qual(qual_name):
        # 現在の session_state の checkbox 状態を取得
        is_checked = st.session_state[f"chk_{qual_name}"]
        if is_checked:
            st.session_state.selected_quals_set.add(qual_name)
        else:
            st.session_state.selected_quals_set.discard(qual_name)

    # 選択解除時の関数
    def remove_qual(qual_name):
        st.session_state.selected_quals_set.discard(qual_name)

    st.sidebar.header("🎯 選択中の資格リスト")
    
    # 選択されている資格がある場合はバッジ風（ボタン）で表示し、クリックで解除可能にする
    if st.session_state.selected_quals_set:
        for q_name in sorted(st.session_state.selected_quals_set):
            st.sidebar.button(f"❌ {q_name}", key=f"rm_{q_name}", on_click=remove_qual, args=(q_name,), help="クリックで選択を解除")
    else:
        st.sidebar.info("取得済みの資格がまだありません。下のリストから探して追加しましょう！")

    st.sidebar.markdown("---")
    
    # 検索機能とカテゴリタブを配置
    st.sidebar.subheader("🔍 資格を探す・追加する")
    search_query = st.sidebar.text_input("資格名で検索...", placeholder="例: ITパスポート")

    # 検索クエリが存在する場合は、検索結果のリストだけを表示
    if search_query:
        st.sidebar.markdown("**検索結果**")
        results = [q for q_name, q in qual_options.items() if search_query.lower() in q_name.lower()]
        if not results:
            st.sidebar.write("一致する資格がありません")
        else:
            for q in results:
                st.sidebar.checkbox(
                    q.name,
                    value=(q.name in st.session_state.selected_quals_set),
                    key=f"chk_{q.name}",
                    on_change=toggle_qual,
                    args=(q.name,)
                )
    # 検索クエリがない場合は、カテゴリごとにタブ分けして一覧表示
    else:
        # カテゴリの一意なリストを取得
        categories = []
        for q in all_qualifications:
            if q.category not in categories:
                categories.append(q.category)
                
        # st.tabs を使用
        tabs = st.sidebar.tabs(categories)
        for i, cat in enumerate(categories):
            with tabs[i]:
                # 各カテゴリに属する資格をリスト表示
                for q in all_qualifications:
                    if q.category == cat:
                        st.checkbox(
                            q.name,
                            value=(q.name in st.session_state.selected_quals_set),
                            key=f"chk_{q.name}",
                            on_change=toggle_qual,
                            args=(q.name,)
                        )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("💳 資格の追加審査をリクエストする"):
        request_qualification_dialog()

    # 計算など後続処理のために選択された資格のリストを再構築
    selected_quals = [qual_options[name] for name in st.session_state.selected_quals_set if name in qual_options]
    selected_qual_ids = [q.id for q in selected_quals]
    selected_categories = [q.category for q in selected_quals]

# 2. スコア計算とシナジー判定ロジック
base_score_total = sum(q.base_score for q in selected_quals)
bonus_score_total = 0
active_titles = []

# シナジーの判定
for syn in all_synergies:
    requirements = syn.requirements

    if not requirements:
        continue
    
    # 対象のシナジーが要求する条件の判定
    synergy_achieved = True
    
    categories_available = list(selected_categories) # 重複消費制御用（必要な場合）
    
    # AND条件としてすべてのRequirementを満たすかチェック
    for req in requirements:
        req_met = False
        
        if req.required_qualification_id:
            # 特定の資格IDを要求する場合
            if req.required_qualification_id in selected_qual_ids:
                req_met = True
        elif req.required_category:
            # 特定のカテゴリを要求する場合
            if req.required_category in categories_available:
                req_met = True
                # 同カテゴリの資格を複数回使い回せるか（今回は簡易的に消費フラグにしない仕様）
        
        if not req_met:
            synergy_achieved = False
            break
            
    if synergy_achieved:
        bonus_score_total += syn.bonus_score
        active_titles.append(syn.title_name)

# 最終スコア
total_score = base_score_total + bonus_score_total
current_title = ", ".join(active_titles) if active_titles else "ルーキー"

# 3. ダッシュボードへのスコア表示
col1, col2, col3 = st.columns(3)
col1.metric("🌟 総合スコア", f"{total_score} pt", f"(基本: {base_score_total} + ボーナス: {bonus_score_total})")
col2.metric("👑 現在の称号", current_title)
col3.metric("🎓 選択資格数", f"{len(selected_quals)} 個")

# X (Twitter) で結果をシェアするボタン
tweet_text = f"私のビジネス戦闘力は {total_score} pt！称号【{current_title}】を獲得しました！🛡️\n異分野の資格を掛け合わせて、自分の市場価値を測ろう！\n#資格レーダー #スキルスコア"
intent_url = f"https://twitter.com/intent/tweet?text={quote(tweet_text)}"
st.link_button("𝕏 で結果をシェアする", intent_url, type="primary")

st.markdown("---")

# 4. レーダーチャートの描画と選択リスト表示
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📊 スキルカテゴリ別 レーダーチャート")
    if selected_quals:
        # カテゴリごとにスコアを集計し、全カテゴリ（9軸）を表示枠に含める
        category_scores_dict = {}
        for q in all_qualifications: 
            if q.category not in category_scores_dict:
                 category_scores_dict[q.category] = 0
                 
        for q in selected_quals:
            category_scores_dict[q.category] += q.base_score
            
        # Plotly用データフレーム作成
        df_radar = pd.DataFrame(dict(
            category=list(category_scores_dict.keys()),
            score=list(category_scores_dict.values())
        ))
        
        fig = px.line_polar(
            df_radar, 
            r='score', 
            theta='category', 
            line_close=True,
            markers=True,
            template="plotly_dark"
        )
        fig.update_traces(fill='toself')
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(100, df_radar['score'].max() + 20)])),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20)
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
            st.success("🎉 **発動中のシナジー**\n\n" + "\n".join([f"- **{t}**" for t in active_titles]))
    else:
        st.write("選択された資格がありません。")

st.markdown("---")

# 5. アフィリエイトレコメンド機能（次の目標）
st.subheader("🎯 次の目標（おすすめの資格）")

reach_synergies = []

# すでに発動しているシナジー以外からリーチ状態を探す
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
            
    # 条件を1つ以上満たしており、かつ足りない条件がある場合は「リーチ」とみなす
    # （※要件が2つ以上あるシナジーに対して「あと1つ」とするため、今回は単純化して「足りないものが存在し、かつ1つ以上は満たしている」とする）
    if met_count > 0 and len(missing_reqs) > 0:
        reach_synergies.append((syn, missing_reqs))

if reach_synergies:
    for syn, missing_reqs in reach_synergies:
        # とりあえず最初の足りない条件を表示メッセージに使う
        first_missing = missing_reqs[0]
        missing_text = ""
        
        if first_missing.required_qualification_id:
            # 資格名を取得
            quali = next((q for q in all_qualifications if q.id == first_missing.required_qualification_id), None)
            missing_text = f"【{quali.name}】" if quali else "特定の資格"
            st.info(f"💡 あと{missing_text}を取得すれば、称号『{syn.title_name} (+{syn.bonus_score}pt)』が発動します！")
            
            if quali:
                # パターンA: HTMLタグ型 (ASPバナー等)
                if quali.affiliate_link and quali.affiliate_link.startswith("<"):
                    st.markdown(quali.affiliate_link, unsafe_allow_html=True)
                # パターンB: URL型
                elif quali.affiliate_link and quali.affiliate_link.startswith("http"):
                    st.link_button(f"[PR] 👉 {quali.name} のおすすめ講座をチェック", quali.affiliate_link)
                # パターンC: 未登録 (Amazon検索URL自動生成)
                else:
                    amazon_url = f"https://www.amazon.co.jp/s?k={quote(quali.name)}+資格+テキスト"
                    st.link_button(f"[PR] 📚 {quali.name} の公式テキスト・過去問を探す", amazon_url)

        elif first_missing.required_category:
            missing_text = f"【{first_missing.required_category}】領域の資格"
            st.info(f"💡 あと{missing_text}を取得すれば、称号『{syn.title_name} (+{syn.bonus_score}pt)』が発動します！")
            
            # カテゴリ不足の場合 (Udemy検索URL自動生成)
            udemy_url = f"https://www.udemy.com/courses/search/?q={quote(first_missing.required_category)}+資格"
            st.link_button(f"[PR] 💻 【{first_missing.required_category}】領域のオンライン講座を探す", udemy_url)

else:
    st.write("さらに別のカテゴリの資格を取得して、新たなシナジーを見つけましょう！")

st.markdown("---")

# 6. バーチャルランキングボード（競争心を刺激）
st.subheader("🏆 全国ランキング (仮想)")

dummy_rivals = [
    {"ユーザー": "資格マニア太郎", "称号": "重厚長大DXマスター", "スコア": 280},
    {"ユーザー": "プラント神", "称号": "プラント・エネルギー戦略家", "スコア": 250},
    {"ユーザー": "ビジネスの鬼", "称号": "AI主導型・経営参謀", "スコア": 180},
    {"ユーザー": "データサイエンス職人", "称号": "データサイエンティスト", "スコア": 150},
    {"ユーザー": "駆け出しエンジニア", "称号": "DX推進アソシエイト", "スコア": 80},
    {"ユーザー": "ITパスポート親方", "称号": "ルーキー", "スコア": 20},
]

# 現在のユーザーを追加
ranking_data = dummy_rivals.copy()
ranking_data.append({
    "ユーザー": f"🟢 あなた ({user.username})",
    "称号": current_title,
    "スコア": total_score
})

# スコア順に降順ソート
ranking_data_sorted = sorted(ranking_data, key=lambda x: x["スコア"], reverse=True)

# DataFrame化して順位をインデックスにする
df_ranking = pd.DataFrame(ranking_data_sorted)
df_ranking.index = [f"{i+1}位" for i in range(len(df_ranking))]
df_ranking.index.name = "順位"

# 表として出力
st.dataframe(df_ranking, use_container_width=True)

# 実装の補足情報
with st.expander("🛠️ システムの仕組み (デバッグ情報)"):
    st.write("利用可能な全シナジー条件:")
    for syn in all_synergies:
        st.markdown(f"**{syn.title_name}** (+{syn.bonus_score}pt)")
        for req in syn.requirements:
            if req.required_qualification_id:
                quali = session.get(Qualification, req.required_qualification_id)
                st.write(f"- 必須資格: {quali.name}")
            elif req.required_category:
                st.write(f"- 必須カテゴリ: {req.required_category}")
