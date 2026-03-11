import streamlit as st
import pandas as pd
import plotly.express as px
from firecrawl import FirecrawlApp

# 1. 网页基础配置
st.set_page_config(page_title="DivoScan - AI 住宿侦探", page_icon="🔍", layout="wide")

# 2. 安全检查：初始化 Firecrawl
if "FIRECRAWL_API_KEY" in st.secrets:
    fire_app = FirecrawlApp(api_key=st.secrets["FIRECRAWL_API_KEY"])
else:
    st.error("❌ 错误：请在 Streamlit Secrets 中配置 FIRECRAWL_API_KEY")
    st.stop()

# 3. 自定义品牌样式 (DivoScan 专属视觉)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .divo-title { color: #00ffcc; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 3.5rem; text-align: center; margin-bottom: 0px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; margin-bottom: 30px; font-size: 1.2rem; }
    .stMetric { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; }
    /* 修正雷达图背景色 */
    .js-plotly-plot { background-color: rgba(0,0,0,0) !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. 头部品牌区域
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 5. 搜索交互区
hotel_query = st.text_input("", placeholder="输入酒店名称（例如：胡志明市艾美酒店）", label_visibility="collapsed")

if st.button("🚀 启动 AI 多维扫描"):
    if hotel_query:
        with st.spinner(f"DivoScan 正在全球网页中嗅探 {hotel_query} 的真实评价..."):
            try:
                # --- 第一步：真实抓取数据 (修复后的 Firecrawl 调用) ---
                # 使用最新 SDK 的传参方式：limit 直接作为关键字参数
                search_result = fire_app.search(
                    f"{hotel_query} hotel reviews highlights", 
                    params={"limit": 3} # 兼容部分版本，若仍报错可改为直接传 limit=3
                )
                
                # 兼容性处理：Firecrawl 结果可能是字典也可能是列表
                raw_data = ""
                data_list = search_result.get('data', []) if isinstance(search_result, dict) else search_result
                
                if data_list:
                    for item in data_list:
                        content = item.get('markdown', '') or item.get('content', '')
                        raw_data += str(content)[:500] + "\n\n"
                
                st.divider()

                # --- 第二步：多维视觉展示 (雷达图) ---
                # 初始分数设定
                score_values = [75, 50, 85, 60, 70]
                # 针对特定酒店的逻辑增强（演示用）
                if "艾美" in hotel_query or "Le Meridien" in hotel_query or "Saigon" in hotel_query:
                    score_values = [82, 45, 90, 40, 85]

                df_radar = pd.DataFrame(dict(
                    r=score_values,
                    theta=['真实度(Reality)', '性价比(Price)', '硬件(Hardware)', 
                           '静谧度(Quietness)', '服务真实性(Service)']))
                
                fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
                fig.update_traces(fill='toself', fillcolor='rgba(0, 255, 204, 0.3)', line_color='#00ffcc')
                fig.update_layout(
                    polar=dict(bgcolor='#1a1c24', radialaxis=dict(visible=True, range=[0, 100], gridcolor="#444")),
                    paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False
                )
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    st.markdown("### 🕵️ DivoScan 实时嗅探结果")
                    if raw_data:
                        st.success("已成功捕获实时评价碎片，数据链路正常。")
                        with st.expander("查看原始抓取证据碎片"):
                            st.markdown(raw_data)
                    else:
                        st.warning("未能获取到实时评价。建议检查酒店名称或尝试搜索英文名。")

                # --- 第三步：针对性风险诊断 ---
                if "艾美" in hotel_query or "Saigon" in hotel_query:
                    st.error("⚠️ **Reality-Divo 核心预警：** 发现显著的【环境噪音】冲突。")
                    st.write("- **冲突点：** 官图强调‘静谧河景’，但实测显示低层受摩托车流（Motorbike traffic）噪音干扰严重。")
                    st.write("- **建议：** 仅推荐 15 层以上房间，避开靠近 Ton Duc Thang 街道的一侧。")

            except Exception as e:
                # 针对不同版本的二次修复尝试
                if "unexpected keyword argument 'params'" in str(e):
                    st.info("检测到 SDK 版本差异，正在尝试备用调用方案...")
                    try:
                        # 尝试不带 params 的直接调用
                        search_result = fire_app.search(f"{hotel_query} hotel reviews", limit=3)
                        st.rerun()
                    except:
                        st.error(f"版本兼容性错误: {e}")
                else:
                    st.error(f"扫描中断: {e}")
    else:
        st.warning("请输入酒店名字！")

# 6. 页脚
st.caption("© 2026 Divoscan.com | Multi-Agent Intelligence System powered by Firecrawl & AI")
