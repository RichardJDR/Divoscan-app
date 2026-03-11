import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import time
import re

# 1. 【品牌临门一脚】页面元数据定制
st.set_page_config(
    page_title="DivoScan | 滤镜背后的住宿真相", 
    page_icon="🕵️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 读取系统配置
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# 3. 注入极致黑客视觉样式 (Divo 2026 视觉语言)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.8rem; text-align: center; padding-top: 60px; letter-spacing: -2px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; font-size: 1.2rem; margin-bottom: 50px; opacity: 0.8; }
    .report-box { background-color: #161b22; border-left: 5px solid #39FF14; padding: 25px; border-radius: 8px; line-height: 1.8; font-size: 1.1rem; color: #e5e7eb; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    
    /* 搜索交互组件 */
    .stButton>button { width: 100%; background-color: #00ffcc; color: #0e1117; font-weight: bold; border: none; height: 3.5rem; border-radius: 8px; font-size: 1.2rem; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    .stButton>button:hover { background-color: #39FF14; box-shadow: 0 0 25px #39FF14; transform: scale(1.02); }
    .stTextInput>div>div>input { background-color: #1a1c24; color: white; border: 1px solid #333; height: 3.5rem; font-size: 1.1rem; border-radius: 8px; text-align: center; }
    
    /* 缓存提示标签 */
    .cache-hint { text-align: center; color: #4b5563; font-size: 0.8rem; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 4. 品牌头部展示
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>Deep-Audit Protocol v3.0 | 还原酒店滤镜下的真实形态</div>", unsafe_allow_html=True)

# 5. 【流量缓冲策略】核心审计逻辑
# ttl=3600 表示同一酒店的审计结果在 1 小时内会缓存在服务器，不重复调用 API
@st.cache_data(ttl=3600, show_spinner=False)
def get_cached_audit(query):
    if not GOOGLE_API_KEY:
        return "ERROR: AUTH_FAILED", None
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # 模型弹性链：优先 1.5 Flash (最稳)，备选 1.5 Pro
    candidate_models = ['gemini-1.5-flash', 'gemini-1.5-pro']
    
    prompt = f"""
    你是 DivoScan 首席审计官 Reality-Divo。
    任务：对酒店 '{query}' 进行多维排雷。
    
    必须以该格式开头回复：
    真实度:数字, 性价比:数字, 硬件:数字, 静谧度:数字, 服务:数字
    (数字范围0-100)
    
    要求：语气刻薄但专业，指出具体痛点，撕掉公关滤镜。
    """
    
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, model_name
        except Exception as e:
            if "429" in str(e) or "404" in str(e):
                continue
            return f"ERROR: {str(e)}", None
    return "OFFLINE: 侦探社由于配额限制暂时歇业，请稍后再试。", None

# 6. 交互界面布局
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    hotel_query = st.text_input("", placeholder="🔍 输入需要扫描的酒店名称（如：新加坡滨海湾金沙酒店）", label_visibility="collapsed")
    scan_clicked = st.button("🚀 启动深度多维审计")
    st.markdown("<div class='cache-hint'>* 相同酒店的审计结果将通过 Divo 缓存协议实时分发，以确保响应速度</div>", unsafe_allow_html=True)

# 7. 结果处理
if scan_clicked:
    if hotel_query:
        with st.status("Divo 协议启动中...", expanded=True) as status:
            st.write("📡 正在穿透 OTA 数据库加密层...")
            
            full_report, final_model = get_cached_audit(hotel_query)
            
            if full_report and not full_report.startswith("ERROR") and not full_report.startswith("OFFLINE"):
                # 解析评分
                scores = re.findall(r"(\w+):(\d+)", full_report)
                if len(scores) >= 5:
                    score_map = {k: int(v) for k, v in scores}
                    r_values = [score_map.get(k, 50) for k in ['真实度', '性价比', '硬件', '静谧度', '服务']]
                else:
                    r_values = [65, 65, 65, 65, 65]
                
                status.update(label=f"数据链路已建立 (引擎: {final_model})", state="complete", expanded=False)
                
                # 视觉呈现
                st.divider()
                col_left, col_right = st.columns([1, 1.3])
                
                with col_left:
                    df_score = pd.DataFrame(dict(r=r_values, theta=['真实度','性价比','硬件','静谧度','服务']))
                    fig = px.line_polar(df_score, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', fillcolor='rgba(0, 255, 204, 0.2)', line_color='#00ffcc', line_width=4)
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', font_color='#00ffcc',
                        polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor='#333'), angularaxis=dict(gridcolor='#333')),
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_right:
                    st.markdown(f"### 🕵️ 审计结果: <span style='color:#00ffcc;'>{hotel_query}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='report-box'>{full_report}</div>", unsafe_allow_html=True)
            else:
                st.error(full_report if full_report else "连接中断，请重试。")
    else:
        st.warning("🕵️ 审计官需要一个具体的目标名称。")

# 8. 页脚
st.markdown("<br><br><br><div style='text-align:center; color:#4b5563; font-size:0.9rem; letter-spacing:1px;'>PRODUCED BY DIVOSCAN LABS | © 2026</div>", unsafe_allow_html=True)
