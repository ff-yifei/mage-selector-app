import streamlit as st
from PIL import Image
import os

st.title("图片选择展示网站")
with left_col:
    # 左侧区域分为上下两部分
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("## 🛠️ 控制面板")
    st.markdown("UMAP Plot")
    feature1 = st.sidebar.selectbox("Gene", ["ACTA2","CD3D", "CD3E","CD4","CD8A", "CD14","CD68","CD79A","CLEC10A","COL1A1","CSF3R","DCN","FAP","FOXP3","IGHG1","IGKC","JCHAIN","KRT8","KRT18","KRT19","NKG7","TPSB2","VWF","EPCAM"])
feature2 = st.sidebar.selectbox("Major cell type",
   submit = st.sidebar.button("GO")
   if submit:
    image_path = f"images/{feature1}.png"
    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption=f"{feature1}", use_container_width=True)
    else:
        st.warning("找不到对应的图片，请确认参数组合和文件名是否一致。")
    st.markdown("---")
    
    # 下部：分析选项
    st.markdown("Violin Plot")
    
    # 图表类型选择
    chart_type = st.radio(
        "选择图表类型:",
        ["折线图", "柱状图", "饼图", "散点图"],
        index=0
    )
    
    # 指标选择
    metric = st.selectbox(
        "选择分析指标:",
        ["销售额", "利润", "销售数量"],
        index=0
    )
    
    # 添加按钮
    st.markdown("---")
    if st.button("应用筛选条件", use_container_width=True):
        st.success("筛选条件已应用!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 左侧下部：关键指标卡片
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("## 📈 关键指标")
    
    # 计算关键指标
    total_sales = sales_df['销售额'].sum()
    avg_profit = sales_df['利润'].mean()
    total_users = user_df['活跃用户'].sum()


# 左侧参数选择


feature3 = st.sidebar.selectbox("Gene",
                            
feature4 = st.sidebar.selectbox("meta information",                                
submit = st.sidebar.button("提交")

# 显示图片
if submit:
    image_path = f"images/{feature1}.png"
    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption=f"{feature1}", use_container_width=True)
    else:
        st.warning("找不到对应的图片，请确认参数组合和文件名是否一致。")
