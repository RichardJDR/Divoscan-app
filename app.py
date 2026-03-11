import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import time
import re

# 1. 页面配置：完全隐藏侧边栏，极简全屏体验
st.set_page_config(
    page_title="DivoScan - AI 住宿侦探", 
    page_icon="🕵️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 读取 Secrets (请确保 Streamlit 云端已配置 GOOGLE_API_KEY)
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# 3. 注入极致黑客视觉样式 (MiroFish 风格)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.8rem; text-align: center; padding-top: 60px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; font-size: 1.2rem; margin-bottom: 50px; }
    .report-box { background-color: #161b22; border-left: 5px solid #39FF14; padding: 25px; border-radius: 8px; line-height: 1.8; font-size: 1.1rem; color: #e5e7eb; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
    
    /* 搜索按钮 */
    .stButton>button { 
        width: 100%; background-color: #00ffcc; color: #0e1117; font-weight: bold; 
        border: none; height: 3.5rem; border-radius: 8px; font-size: 1.2rem; transition: 0.3s; 
    }
    .stButton>button:hover { background-color: #39FF14; box-shadow: 0 0 20px #39FF14; transform: translateY(-2px); }
    
    /* 输入框 */
    .stTextInput>div>div>input { 
        background-color: #1a1c24; color: white; border: 1px solid #333; 
        height: 3.5rem; font-size: 1.1rem; border-radius: 8px; text-align: center; 
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 品牌头部
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 5. 搜索区域 (全屏居中)
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    hotel_query = st.text_input("", placeholder="🔍 输入酒店名称（例如：新加坡金沙酒店 / 上海宝格丽）", label_visibility="collapsed")
    scan_clicked = st.button("🚀 启动深度扫描 (Gemini 2.0 Turbo)")

# 6. 核心逻辑执行
if scan_clicked:
    if not GOOGLE_API_KEY:
        st.error("密钥缺失：请在 Streamlit Cloud 的 Secrets 中填入 GOOGLE_API_KEY。")
    elif hotel_query:
        with st.status("Divo Agent 2.0 正在连接全球审计节点...", expanded=True) as status:
            st.write("📡 探测器正在穿透 OTA 数据迷雾...")
            time.sleep(0.8)
            
            try:
                # 配置最新的 Gemini 模型
                genai.configure(api_key=GOOGLE_API_KEY)
                
                # 直连 2.0 模型，跳过可能引起 404 的 models/ 前缀
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                st.write("🧠 Reality-Divo 正在跨维度提取真相...")
                
                prompt = f"""
                你是一个毒舌且专业的酒店审计专家 Reality-Divo，运行在 2.0 引擎。
                针对酒店 '{hotel_query}'，请直接给出犀利的排雷报告。

                必须严格按此格式开头评分：
                真实度:数字, 性价比:数字, 硬件:数字, 静谧度:数字, 服务:数字
                数字范围 0-100。
                
                点评要求：
                1. 语气直接且专业，避开所有官方公关话术。
                2. 重点扫描：隔音、空调老化、早餐排队、电梯效率、周边噪音。
                3. 如果数据不足，请根据该酒店档次和常见槽点给出预测性审计。
                """
                
                response = model.generate_content(prompt)
                full_report = response.text
                
                # 正则解析评分
                scores = re.findall(r"(\w+):(\d+)", full_report)
                if len(scores) >= 5:
                    score_map = {k: int(v) for k, v in scores}
                    r_values = [score_map.get(k, 50) for k in ['真实度', '性价比', '硬件', '静谧度', '服务']]
                else:
                    r_values = [75, 60, 80, 55, 70] 
                
                status.update(label="审计报告已就绪", state="complete", expanded=False)
                
                # 7. 结果展示 (并排布局)
                st.divider()
                col_left, col_right = st.columns([1, 1.3])
                
                with col_left:
                    # 强化雷达图视觉
                    df_score = pd.DataFrame(dict(r=r_values, theta=['真实度','性价比','硬件','静谧度','服务']))
                    fig = px.line_polar(df_score, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', fillcolor='rgba(57, 255, 20, 0.3)', line_color='#39FF14', line_width=4)
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', font_color='#00ffcc',
                        polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor='#333'),
                        angularaxis=dict(gridcolor='#333', tickfont=dict(size=14))),
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col_right:
                    st.markdown(f"### 🕵️ 现场审计报告: <span style='color:#00ffcc;'>{hotel_query}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='report-box'>{full_report}</div>", unsafe_allow_html=True)
                    st.write("")
                    st.caption("🔍 Divo 提示：本报告已整合 Gemini 2.0 实时推理数据。")

            except Exception as e:
                st.error(f"大脑执行异常: {str(e)}")
                st.info("💡 解决办法：请确保 requirements.txt 中包含 google-generativeai>=0.8.0")
    else:
        st.warning("🕵️ 请输入酒店名称。")

# 8. 页脚
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<div style='text-align:center; color:#4b5563; font-size:0.9rem;'>© 2026 Divoscan.com | Multi-Agent Security Protocol v2.7</div>", unsafe_allow_html=True)
