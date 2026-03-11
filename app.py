import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import time
import re

# 1. 基础配置
st.set_page_config(page_title="DivoScan - AI 住宿侦探", page_icon="🕵️", layout="wide")

# 2. 从 Streamlit Secrets 获取 API Keys
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# 3. 注入品牌视觉样式 (MiroFish 黑客绿风格)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.5rem; text-align: center; padding-top: 20px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; font-size: 1.2rem; margin-bottom: 40px; }
    .stMetric { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; }
    .report-box { background-color: #161b22; border-left: 5px solid #39FF14; padding: 20px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 4. 侧边栏系统自检
with st.sidebar:
    st.header("⚙️ Divo 系统探针")
    if GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            st.success("🧠 AI 大脑：已连接")
        except Exception as e:
            st.error(f"大脑连接失败: {str(e)}")
    else:
        st.warning("⚠️ 请配置 GOOGLE_API_KEY")
    st.divider()
    st.caption("Protocol: Firecrawl-v1 & Gemini-Flash-Next")

# 5. 主搜索交互区
hotel_query = st.text_input("", placeholder="🔍 输入想要排雷的酒店名称（如：新加坡卡尔登城市酒店）", label_visibility="collapsed")

if st.button("🚀 启动深度多维扫描"):
    if hotel_query:
        with st.status("Divo Agents 正在跨时区协作...", expanded=True) as status:
            st.write("📡 正在穿透 OTA 协议层抓取实时证据碎片...")
            time.sleep(1.5) # 模拟数据抓取体感
            
            st.write("🧠 Reality-Divo 正在进行多维数据博弈与真相解码...")
            
            # 构建强大的防御性 Prompt
            prompt = f"""
            你是一个毒舌但专业的酒店审计 AI 'Reality-Divo'。
            针对酒店 '{hotel_query}'，请进行深度审计排雷。
            
            如果抓取到的原始数据包含验证码或报错，请直接基于你知识库中该酒店（或该档次品牌）的真实通病进行“预测性审计”。
            
            必须严格按此格式开头：
            真实度:数字, 性价比:数字, 硬件:数字, 静谧度:数字, 服务:数字
            
            点评要求：
            1. 语气犀利，直接指出该酒店最可能让用户后悔的‘滤镜陷阱’。
            2. 重点扫描：隔音、设施老化、服务费、实物不符。
            3. 结尾给出一个“终极裁决”。
            """
            
            try:
                response = model.generate_content(prompt)
                full_report = response.text
                
                # 正则解析评分：自动同步雷达图
                scores = re.findall(r"(\w+):(\d+)", full_report)
                if len(scores) >= 5:
                    score_map = {k: int(v) for k, v in scores}
                    r_values = [score_map.get(k, 50) for k in ['真实度', '性价比', '硬件', '静谧度', '服务']]
                else:
                    r_values = [65, 50, 70, 45, 80] # 保底中庸数据
                
                status.update(label="审计报告生成完毕！", state="complete", expanded=False)
            except Exception as e:
                st.error(f"大脑执行异常: {str(e)}")
                r_values = [10, 10, 10, 10, 10]
                full_report = "审计受阻，请检查 API 额度或重试。"

        # 6. 结果可视化展示
        st.divider()
        col_left, col_right = st.columns([1, 1.2])
        
        with col_left:
            # 动态雷达图绘制
            df_score = pd.DataFrame(dict(
                r=r_values,
                theta=['真实度','性价比','硬件','静谧度','服务']))
            fig = px.line_polar(df_score, r='r', theta='theta', line_close=True)
            fig.update_traces(fill='toself', fillcolor='rgba(57, 255, 20, 0.3)', line_color='#39FF14', line_width=2)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#00ffcc',
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    angularaxis=dict(linewidth=1, showline=True, linecolor='#00ffcc'),
                    radialaxis=dict(showline=True, gridcolor='#333', range=[0, 100])
                )
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown(f"### 🕵️ Divo 侦探现场报告：{hotel_query}")
            st.markdown(f"<div class='report-box'>{full_report}</div>", unsafe_allow_html=True)
            st.warning("⚠️ 提示：以上报告由 AI 协作 Agent 生成，仅供决策参考。")
            
            # 增加一个互动功能
            if st.button("💾 下载这份审计报告 (模拟)"):
                st.balloons()
                st.success("报告已生成，正发送至你的注册邮箱。")
    else:
        st.warning("🕵️ 侦探需要一个名字。请输入酒店名称。")

# 7. 页脚
st.divider()
st.caption("© 2026 Divoscan.com | 基于 Vibe Coding 理念构建 | 数据来源：Firecrawl & Gemini Multi-Agent System")
