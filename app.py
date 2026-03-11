import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. 基础配置
st.set_page_config(page_title="DivoScan - 最终调试版", page_icon="🔍", layout="wide")

# 2. 读取 Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
FIRECRAWL_API_KEY = st.secrets.get("FIRECRAWL_API_KEY")

# 3. 自动探测：找出你账号下真正能用的模型
def get_real_model_name(api_key):
    try:
        # 直接通过 ListModels 接口查看权限
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(url)
        if res.status_code == 200:
            models = res.json().get('models', [])
            # 寻找支持生成内容且包含 '1.5-flash' 的模型全名
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []) and '1.5-flash' in m['name']:
                    return m['name'] # 可能是 "models/gemini-1.5-flash"
            # 如果没有 flash，退而求其次选第一个能用的
            if models:
                return models[0]['name']
        return None
    except:
        return None

# 初始化模型探测
real_model = get_real_model_name(GEMINI_API_KEY)

# 4. 侧边栏状态灯
with st.sidebar:
    st.header("⚙️ 系统自检")
    if real_model:
        st.success(f"✅ 成功连接！\n可用模型：{real_model}")
    else:
        st.error("❌ 无法探测到可用模型")
        st.info("提示：请确认是否使用了 'Create API key in NEW project' 生成的 Key。")

# 5. 主界面逻辑 (样式保持 DivoScan 酷黑风格)
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>DivoScan.com</h1>", unsafe_allow_html=True)
hotel_query = st.text_input("", placeholder="🔍 输入酒店名，查看 AI 侦探报告", label_visibility="collapsed")

if st.button("🚀 启动深度扫描"):
    if not real_model:
        st.error("当前 API Key 无模型访问权限，请更换 Key 后重试。")
    elif hotel_query:
        with st.spinner("Divo Agent 正在跨国抓取并分析数据..."):
            try:
                # --- Step 1: Firecrawl 数据抓取 ---
                scrape_url = "https://api.firecrawl.dev/v1/scrape"
                payload = {
                    "url": f"https://www.google.com/search?q={hotel_query}+reviews+tripadvisor",
                    "formats": ["markdown"]
                }
                headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}
                scrape_res = requests.post(scrape_url, json=payload, headers=headers)
                raw_data = scrape_res.json().get('data', {}).get('markdown', '')[:3000]

                # --- Step 2: 使用探测到的真实模型名进行调用 ---
                # 注意：探测到的名字通常自带 'models/' 前缀，直接拼入 URL
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/{real_model}:generateContent?key={GEMINI_API_KEY}"
                
                prompt = f"你是一个毒舌酒店专家。根据以下评价分析 {hotel_query}：\n{raw_data}\n\n给出3个避雷点和5维评分。中文回答。"
                gemini_res = requests.post(gemini_url, json={"contents": [{"parts": [{"text": prompt}]}]})
                
                if gemini_res.status_code == 200:
                    report = gemini_res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.divider()
                    st.markdown(f"### 🕵️ Divo 报告 ({real_model})\n{report}")
                else:
                    st.error(f"AI 调用失败: {gemini_res.text}")

            except Exception as e:
                st.error(f"链路故障: {e}")

st.caption("© 2026 Divoscan.com | Adaptive Intelligence")
