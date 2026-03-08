import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, User, Qualification, Synergy, SynergyRequirement

DATABASE_URL = "sqlite:///app.db"

def seed_database():
    # 既存のDBファイルがあれば削除（初期化のため）
    if os.path.exists("app.db"):
        os.remove("app.db")

    # DBエンジンとテーブルの作成
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # 3. 資格マスターデータの投入 (9カテゴリ)
        qualifications_data = [
            # 1. 経営・ビジネス
            {"name": "MBA (経営学修士)", "category": "経営・ビジネス", "tier": 1, "base_score": 95},
            {"name": "中小企業診断士", "category": "経営・ビジネス", "tier": 2, "base_score": 80},
            {"name": "PMP (プロジェクトマネジメントプロフェッショナル)", "category": "経営・ビジネス", "tier": 2, "base_score": 75},
            {"name": "CBAP (ビジネスアナリシス・プロフェッショナル)", "category": "経営・ビジネス", "tier": 2, "base_score": 75},
            {"name": "経営学検定 中級・上級", "category": "経営・ビジネス", "tier": 3, "base_score": 60},
            {"name": "Google アナリティクス個人認定資格 (GAIQ)", "category": "経営・ビジネス", "tier": 3, "base_score": 60},
            {"name": "ビジネスマネジャー検定", "category": "経営・ビジネス", "tier": 3, "base_score": 55},
            {"name": "キャリアコンサルタント", "category": "経営・ビジネス", "tier": 3, "base_score": 50},
            {"name": "メンタルヘルス・マネジメント検定 I種", "category": "経営・ビジネス", "tier": 3, "base_score": 45},
            {"name": "メンタルヘルス・マネジメント検定 II種", "category": "経営・ビジネス", "tier": 4, "base_score": 30},
            {"name": "秘書検定 2級", "category": "経営・ビジネス", "tier": 5, "base_score": 20},

            # 2. 財務・金融
            {"name": "公認会計士", "category": "財務・金融", "tier": 1, "base_score": 100},
            {"name": "税理士", "category": "財務・金融", "tier": 1, "base_score": 95},
            {"name": "USCPA (米国公認会計士)", "category": "財務・金融", "tier": 1, "base_score": 90},
            {"name": "証券アナリスト", "category": "財務・金融", "tier": 2, "base_score": 80},
            {"name": "日商簿記1級", "category": "財務・金融", "tier": 3, "base_score": 65},
            {"name": "FP技能士1級", "category": "財務・金融", "tier": 3, "base_score": 65},
            {"name": "CFP (サーティファイド・ファイナンシャル・プランナー)", "category": "財務・金融", "tier": 3, "base_score": 65},
            {"name": "日商簿記2級", "category": "財務・金融", "tier": 4, "base_score": 45},
            {"name": "FP技能士2級", "category": "財務・金融", "tier": 4, "base_score": 40},
            {"name": "AFP", "category": "財務・金融", "tier": 4, "base_score": 45},
            {"name": "ビジネス会計検定 2級", "category": "財務・金融", "tier": 4, "base_score": 40},
            {"name": "日商簿記3級", "category": "財務・金融", "tier": 5, "base_score": 25},
            {"name": "FP技能士3級", "category": "財務・金融", "tier": 5, "base_score": 25},

            # 3. 法務・労務・知財
            {"name": "弁護士", "category": "法務・労務・知財", "tier": 1, "base_score": 100},
            {"name": "弁理士", "category": "法務・労務・知財", "tier": 1, "base_score": 95},
            {"name": "司法書士", "category": "法務・労務・知財", "tier": 1, "base_score": 90},
            {"name": "社会保険労務士", "category": "法務・労務・知財", "tier": 2, "base_score": 80},
            {"name": "行政書士", "category": "法務・労務・知財", "tier": 3, "base_score": 65},
            {"name": "第一種衛生管理者", "category": "法務・労務・知財", "tier": 3, "base_score": 55},
            {"name": "ビジネス実務法務検定 2級", "category": "法務・労務・知財", "tier": 4, "base_score": 45},
            {"name": "知的財産管理技能検定 2級", "category": "法務・労務・知財", "tier": 4, "base_score": 45},
            {"name": "ビジネス実務法務検定 3級", "category": "法務・労務・知財", "tier": 5, "base_score": 25},
            {"name": "第二種衛生管理者", "category": "法務・労務・知財", "tier": 5, "base_score": 25},

            # 4. IT・データ
            {"name": "ITストラテジスト", "category": "IT・データ", "tier": 1, "base_score": 90},
            {"name": "情報処理安全確保支援士 (登録セキスペ)", "category": "IT・データ", "tier": 1, "base_score": 85},
            {"name": "ネットワークスペシャリスト", "category": "IT・データ", "tier": 1, "base_score": 85},
            {"name": "データベーススペシャリスト", "category": "IT・データ", "tier": 1, "base_score": 85},
            {"name": "AWS認定 ソリューションアーキテクト - プロフェッショナル", "category": "IT・データ", "tier": 1, "base_score": 85},
            {"name": "CCIE", "category": "IT・データ", "tier": 1, "base_score": 95},
            {"name": "Oracle Master Platinum", "category": "IT・データ", "tier": 1, "base_score": 95},
            {"name": "Salesforce 認定テクニカルアーキテクト", "category": "IT・データ", "tier": 1, "base_score": 95},
            {"name": "E資格 (ディープラーニング)", "category": "IT・データ", "tier": 2, "base_score": 75},
            {"name": "CCNP", "category": "IT・データ", "tier": 2, "base_score": 80},
            {"name": "Oracle Master Gold", "category": "IT・データ", "tier": 2, "base_score": 80},
            {"name": "Google Cloud Professional Cloud Architect", "category": "IT・データ", "tier": 2, "base_score": 80},
            {"name": "CISA (公認情報システム監査人)", "category": "IT・データ", "tier": 2, "base_score": 80},
            {"name": "応用情報技術者", "category": "IT・データ", "tier": 3, "base_score": 65},
            {"name": "統計検定 準1級", "category": "IT・データ", "tier": 3, "base_score": 65},
            {"name": "Python3エンジニア認定データ分析実践試験", "category": "IT・データ", "tier": 3, "base_score": 60},
            {"name": "CCNA", "category": "IT・データ", "tier": 3, "base_score": 65},
            {"name": "Oracle Master Silver", "category": "IT・データ", "tier": 3, "base_score": 65},
            {"name": "AWS Certified Solutions Architect - Associate", "category": "IT・データ", "tier": 3, "base_score": 65},
            {"name": "Salesforce 認定アドミニストレーター", "category": "IT・データ", "tier": 3, "base_score": 65},
            {"name": "基本情報技術者", "category": "IT・データ", "tier": 4, "base_score": 45},
            {"name": "G検定 (ジェネラリスト検定)", "category": "IT・データ", "tier": 4, "base_score": 45},
            {"name": "データサイエンティスト検定 (リテラシーレベル)", "category": "IT・データ", "tier": 4, "base_score": 40},
            {"name": "Oracle Master Bronze", "category": "IT・データ", "tier": 4, "base_score": 45},
            {"name": "AWS Certified Cloud Practitioner", "category": "IT・データ", "tier": 4, "base_score": 45},
            {"name": "ITパスポート", "category": "IT・データ", "tier": 5, "base_score": 20},
            {"name": "統計検定 3級", "category": "IT・データ", "tier": 5, "base_score": 25},

            # 5. 語学・グローバル
            {"name": "TOEIC 900点以上", "category": "語学・グローバル", "tier": 1, "base_score": 85},
            {"name": "英検1級", "category": "語学・グローバル", "tier": 1, "base_score": 85},
            {"name": "TOEFL iBT 100点以上", "category": "語学・グローバル", "tier": 2, "base_score": 80},
            {"name": "TOEIC 800点以上", "category": "語学・グローバル", "tier": 3, "base_score": 70},
            {"name": "英検準1級", "category": "語学・グローバル", "tier": 3, "base_score": 70},
            {"name": "TOEIC 700点以上", "category": "語学・グローバル", "tier": 4, "base_score": 60},
            {"name": "TOEIC 600点以上", "category": "語学・グローバル", "tier": 5, "base_score": 40},
            {"name": "HSK 5級 (中国語)", "category": "語学・グローバル", "tier": 5, "base_score": 50},

            # 6. 電気・通信・エネ
            {"name": "電験一種 (第一種電気主任技術者)", "category": "電気・通信・エネ", "tier": 1, "base_score": 95},
            {"name": "電験二種 (第二種電気主任技術者)", "category": "電気・通信・エネ", "tier": 2, "base_score": 85},
            {"name": "エネルギー管理士", "category": "電気・通信・エネ", "tier": 2, "base_score": 80},
            {"name": "電験三種 (第三種電気主任技術者)", "category": "電気・通信・エネ", "tier": 3, "base_score": 65},
            {"name": "電気通信主任技術者", "category": "電気・通信・エネ", "tier": 3, "base_score": 65},
            {"name": "第一種電気工事士", "category": "電気・通信・エネ", "tier": 4, "base_score": 45},
            {"name": "工事担任者 (総合通信)", "category": "電気・通信・エネ", "tier": 4, "base_score": 45},
            {"name": "第二種電気工事士", "category": "電気・通信・エネ", "tier": 5, "base_score": 25},
            {"name": "危険物取扱者 甲種", "category": "電気・通信・エネ", "tier": 5, "base_score": 40},
            {"name": "危険物取扱者 乙種4類", "category": "電気・通信・エネ", "tier": 5, "base_score": 20},

            # 7. 機械・製造
            {"name": "技術士 (機械部門/金属部門/経営工学部門等)", "category": "機械・製造", "tier": 1, "base_score": 95},
            {"name": "機械保全技能士 (特級)", "category": "機械・製造", "tier": 2, "base_score": 75},
            {"name": "QC検定1級", "category": "機械・製造", "tier": 2, "base_score": 75},
            {"name": "公害防止管理者 (大気1種/水質1種)", "category": "機械・製造", "tier": 3, "base_score": 65},
            {"name": "機械保全技能士 (1級)", "category": "機械・製造", "tier": 3, "base_score": 60},
            {"name": "自主保全士 (1級)", "category": "機械・製造", "tier": 3, "base_score": 55},
            {"name": "ボイラー技士 (特級)", "category": "機械・製造", "tier": 3, "base_score": 70},
            {"name": "QC検定2級", "category": "機械・製造", "tier": 4, "base_score": 45},
            {"name": "1級ボイラー技士", "category": "機械・製造", "tier": 4, "base_score": 45},
            {"name": "QC検定3級", "category": "機械・製造", "tier": 5, "base_score": 25},
            {"name": "2級ボイラー技士", "category": "機械・製造", "tier": 5, "base_score": 20},

            # 8. 建築・土木
            {"name": "一級建築士", "category": "建築・土木", "tier": 1, "base_score": 95},
            {"name": "1級建築施工管理技士", "category": "建築・土木", "tier": 2, "base_score": 80},
            {"name": "1級土木施工管理技士", "category": "建築・土木", "tier": 2, "base_score": 80},
            {"name": "1級電気工事施工管理技士", "category": "建築・土木", "tier": 2, "base_score": 80},
            {"name": "二級建築士", "category": "建築・土木", "tier": 3, "base_score": 70},
            {"name": "測量士", "category": "建築・土木", "tier": 3, "base_score": 60},
            {"name": "2級施工管理技士 (各種)", "category": "建築・土木", "tier": 4, "base_score": 45},
            {"name": "測量士補", "category": "建築・土木", "tier": 5, "base_score": 25},

            # 9. 不動産・施設管理
            {"name": "不動産鑑定士", "category": "不動産・施設管理", "tier": 1, "base_score": 95},
            {"name": "建築物環境衛生管理技術者 (ビル管理士)", "category": "不動産・施設管理", "tier": 3, "base_score": 65},
            {"name": "マンション管理士", "category": "不動産・施設管理", "tier": 3, "base_score": 65},
            {"name": "宅地建物取引士", "category": "不動産・施設管理", "tier": 4, "base_score": 60},
            {"name": "認定ファシリティマネジャー", "category": "不動産・施設管理", "tier": 4, "base_score": 55},
            {"name": "管理業務主任者", "category": "不動産・施設管理", "tier": 5, "base_score": 40},
            {"name": "消防設備士 (甲種4類)", "category": "不動産・施設管理", "tier": 5, "base_score": 35},,

        {'name': 'AWS Certified Machine Learning Engineer - Associate (MLA)', 'category': 'IT・データ', 'tier': 2, 'base_score': 85},

        {'name': 'AWS Certified SysOps Administrator - Associate (SOA)', 'category': 'IT・データ', 'tier': 2, 'base_score': 80},

        {'name': 'AWS Certified Solutions Architect - Professional', 'category': 'IT・データ', 'tier': 1, 'base_score': 90},

        {'name': 'SAP Certified Professional', 'category': 'IT・データ', 'tier': 1, 'base_score': 90},

        {'name': 'CISSP', 'category': 'IT・データ', 'tier': 1, 'base_score': 90},

        {'name': '貿易実務検定', 'category': '語学・グローバル', 'tier': 3, 'base_score': 60},

        {'name': '自動車運転免許', 'category': '不動産・施設管理', 'tier': 5, 'base_score': 30},,


        {'name': 'AWS Certified Solutions Architect - Professional', 'category': 'IT・データ', 'tier': 1, 'base_score': 95},


        {'name': 'SAP Certified Professional', 'category': 'IT・データ', 'tier': 1, 'base_score': 95},


        {'name': 'CISSP (情報セキュリティプロフェッショナル)', 'category': 'IT・データ', 'tier': 1, 'base_score': 95},


        {'name': 'AWS Certified Machine Learning Engineer - Associate', 'category': 'IT・データ', 'tier': 2, 'base_score': 85},


        {'name': 'AWS Certified SysOps Administrator - Associate', 'category': 'IT・データ', 'tier': 2, 'base_score': 80},


        {'name': '応用情報技術者 (AP)', 'category': 'IT・データ', 'tier': 3, 'base_score': 65},


        {'name': '第一種電気主任技術者 (電験一種)', 'category': '電気・通信・エネ', 'tier': 1, 'base_score': 100},


        {'name': '特級ボイラー技士', 'category': '機械・製造', 'tier': 1, 'base_score': 95},


        {'name': 'エネルギー管理士', 'category': '電気・通信・エネ', 'tier': 2, 'base_score': 85},


        {'name': 'USCPA (米国公認会計士)', 'category': '財務・金融', 'tier': 1, 'base_score': 95},


        {'name': 'PMP (Project Management Professional)', 'category': '経営・ビジネス', 'tier': 2, 'base_score': 85},


        {'name': '社会保険労務士', 'category': '法務・労務・知財', 'tier': 2, 'base_score': 80},


        {'name': '中小企業診断士', 'category': '経営・ビジネス', 'tier': 2, 'base_score': 80},


        {'name': '英検1級', 'category': '語学・グローバル', 'tier': 2, 'base_score': 80},


        {'name': 'TOEIC 800点以上', 'category': '語学・グローバル', 'tier': 3, 'base_score': 65},


        {'name': '貿易実務検定 (A級)', 'category': '語学・グローバル', 'tier': 3, 'base_score': 65},


        {'name': '日商簿記2級', 'category': '財務・金融', 'tier': 4, 'base_score': 50},


        {'name': '不動産鑑定士', 'category': '不動産・施設管理', 'tier': 1, 'base_score': 95},


        {'name': '宅地建物取引士', 'category': '不動産・施設管理', 'tier': 3, 'base_score': 65},


        ]
        
        qualifications = []
        for q_data in qualifications_data:
            q = Qualification(**q_data)
            session.add(q)
            qualifications.append(q)
            
        session.commit()
        
        # 特定の資格を取得（IDを参照するため）
        it_passport = session.query(Qualification).filter_by(name="ITパスポート").first()
        boki_3 = session.query(Qualification).filter_by(name="日商簿記3級").first()

        # 4. シナジーマスターと発動条件の投入
        
        synergies_data = [
            {
                "title_name": "重厚長大DXマスター",
                "bonus_score": 35,
                "description": "製造現場の深い理解と高度なITスキルを掛け合わせ、製造業のDXを牽引するエキスパート。",
                "req_categories": ["IT・データ", "機械・製造"]
            },
            {
                "title_name": "プラント・エネルギー戦略家",
                "bonus_score": 30,
                "description": "インフラ・エネルギー施設の専門知識と、事業採算を評価する財務スキルを併せ持つ戦略家。",
                "req_categories": ["財務・金融", "電気・通信・エネ"]
            },
            {
                "title_name": "AI主導型・経営参謀",
                "bonus_score": 30,
                "description": "経営課題をデータとテクノロジーで解決する、次世代のビジネスリーダー。",
                "req_categories": ["経営・ビジネス", "IT・データ"]
            },
            {
                "title_name": "グローバル・タフ・ネゴシエーター",
                "bonus_score": 30,
                "description": "国際的な法規や契約に精通し、多言語でタフな交渉をまとめ上げる国際法務スペシャリスト。",
                "req_categories": ["法務・労務・知財", "語学・グローバル"]
            },
            {
                "title_name": "次世代データセンター設計者",
                "bonus_score": 35,
                "description": "クラウドインフラの知識と、膨大な電力を制御する電気の専門知識を併せ持つ、現代のインフラ最強エンジニア。",
                "req_categories": ["IT・データ", "電気・通信・エネ"]
            },
            {
                "title_name": "工場EHS統括マネージャー",
                "bonus_score": 30,
                "description": "労働安全衛生（第一種衛生管理者など）と環境保全（公害防止など）を両立し、ゼロ災工場を実現する現場の要。",
                "req_categories": ["法務・労務・知財", "機械・製造"]
            },
            {
                "title_name": "データ駆動型・人事戦略家",
                "bonus_score": 30,
                "description": "組織心理や労務知識にデータサイエンスを掛け合わせ、科学的なピープルアナリティクスを実践するHRのプロ。",
                "req_categories": ["経営・ビジネス", "IT・データ", "法務・労務・知財"]
            },
            {
                "title_name": "フルスタック・ファシリティマスター",
                "bonus_score": 35,
                "description": "ビル管理から電気、ボイラー等の機械設備まで、あらゆる設備の保全を網羅した建物の絶対的守護神。",
                "req_categories": ["不動産・施設管理", "電気・通信・エネ", "機械・製造"]
            },
            {
                "title_name": "現場カイゼン推進リーダー",
                "bonus_score": 15,
                "description": "QCや保全の知識と基礎的なITツールを駆使し、自ら手を動かして現場の業務効率化（小集団活動・DX）を牽引する若きエース。",
                "req_categories": ["機械・製造", "IT・データ"]
            },
            {
                "title_name": "グローバル・プロジェクト総指揮",
                "bonus_score": 30,
                "description": "高度なマネジメント手法と語学力を駆使し、国境を越えたビッグプロジェクトを完遂に導くリーダー。",
                "req_categories": ["経営・ビジネス", "語学・グローバル"]
            }
        ]
        
        for syn_data in synergies_data:
            syn = Synergy(
                title_name=syn_data["title_name"],
                bonus_score=syn_data["bonus_score"],
                description=syn_data["description"]
            )
            session.add(syn)
            session.commit() # IDを取得
            
            for cat in syn_data["req_categories"]:
                req = SynergyRequirement(synergy_id=syn.id, required_category=cat)
                session.add(req)
        
        # 既存のDX推進アソシエイト (特定資格要求)
        if it_passport and boki_3:
            synergy_assoc = Synergy(
                title_name="DX推進アソシエイト", 
                bonus_score=15,
                description="ITリテラシーと財務の基礎知識を持ち、DX推進の実務をサポートする人材。"
            )
            session.add(synergy_assoc)
            session.commit()
            
            req_assoc_1 = SynergyRequirement(synergy_id=synergy_assoc.id, required_qualification_id=it_passport.id)
            req_assoc_2 = SynergyRequirement(synergy_id=synergy_assoc.id, required_qualification_id=boki_3.id)
            session.add_all([req_assoc_1, req_assoc_2])

        # 5. テスト用ユーザーの作成
        test_user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password_placeholder",
        )
        session.add(test_user)
        
        session.commit()
        print("Database seeding completed successfully with full master data!")

if __name__ == "__main__":
    seed_database()
