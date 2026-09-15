import streamlit as st
import google.generativeai as genai
import json

# --- ページの設定 ---
st.set_page_config(page_title="ぬいモチーフ・ジェネレーター", page_icon="✂️", layout="centered")

st.title("✂️ ぬいモチーフ・ジェネレーター")
st.caption("条件を選ぶと、ぬいぐるみ本体のモチーフ案と似合う衣装案を提案します")

# --- SecretsからAPIキーを取得 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

# --- 入力フォーム ---
st.subheader("条件を選択してください")

col1, col2 = st.columns(2)

with col1:
    size_opt = st.radio("サイズ", ["10cm", "15cm", "20cm", "30cm", "その他"])
    if size_opt == "その他":
        size_val = st.text_input("サイズを直接入力", placeholder="例: 25cm")
    else:
        size_val = size_opt

    skin_opt = st.radio("肌色", ["普通肌", "白肌", "灰色肌", "褐色肌", "ダーク肌", "その他"])
    if skin_opt == "その他":
        skin_val = st.text_input("肌色を直接入力", placeholder="例: 青肌")
    else:
        skin_val = skin_opt

    gender_val = st.radio("性別イメージ", ["女の子", "男の子", "無性・中性", "自由"])

with col2:
    motif_val = st.radio("モチーフ系統", ["動物", "人外・幻想", "フード・自然", "職業・キャラ", "おまかせ"])

    color_opt = st.radio("色の指定", ["指定なし", "モノトーン", "パステル", "ビビッド", "ダーク・シック", "アース系", "ゴールド・シルバー", "その他"])
    if color_opt == "その他":
        color_val = st.text_input("色を直接入力", placeholder="例: 臙脂色メイン")
    else:
        color_val = color_opt

    count_val = st.radio("提案数", [3, 5], horizontal=True)

note_val = st.text_input("追加の要望（任意）", placeholder="例: ゆめかわ系、クラシック系など")

# --- アイデア生成処理 ---
if st.button("✨ アイデアを出す", type="primary", use_container_width=True):
    if not api_key:
        st.error("APIキーが設定されていません。StreamlitのSecrets設定を確認してください。")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3.6-flash")

            prompt = f"""
あなたは推しぬい(棉花娃娃/無属性オリジナルぬいぐるみ)のデザイナーです。以下の条件に合うモチーフ案を{count_val}個、日本語で考えてください。

条件:
- サイズ: {size_val}
- 肌色: {skin_val}
- 性別: {gender_val}
- モチーフ系統: {motif_val}
- 色の指定: {color_val}
{f"- 追加の要望: {note_val}" if note_val else ""}

このぬいぐるみは着せ替え前提で、何も着せていない裸のボディの状態を想定しています。
descriptionには衣装・服・アクセサリーの話は一切含めず、肌の質感、目の色や形、耳・角・尻尾・羽などのパーツ、髪(ある場合)、ボディの配色や雰囲気だけを描写してください。

次のJSON配列だけを出力してください。前置き、説明、コードブロックの記号(```)は一切つけないでください。
[
  {{
    "emoji": "絵文字2〜3個を×で繋いだ組み合わせ",
    "title": "モチーフ名(10文字程度)",
    "description": "肌・パーツ・配色・雰囲気を含む3〜4文の詳細説明(衣装への言及はしない)",
    "outfits": ["似合う衣装案A", "似合う衣装案B", "似合う衣装案C"]
  }}
]
"""
            with st.spinner("AIがアイデアを考案中..."):
                response = model.generate_content(prompt)
                cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
                ideas = json.loads(cleaned_text)

            st.success("アイデアが生成されました！")
            st.divider()

            for i, idea in enumerate(ideas, 1):
                st.markdown(f"### {idea['emoji']} 案{i}：{idea['title']}")
                st.write(idea['description'])
                
                st.markdown("**【似合う衣装案】**")
                for outfit in idea.get('outfits', []):
                    st.markdown(f"- {outfit}")
                
                st.divider()

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
