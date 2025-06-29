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
feature2 = st.sidebar.selectbox("Major cell type",["ACTA2"])
   submit = st.sidebar.button("GO")
   if submit:
    image_path = f"images/{feature1}.png" or f"images/{feature2}.png"

    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption=f"{feature1}", use_container_width=True)
    else:
        st.warning("找不到对应的图片，请确认参数组合和文件名是否一致。")
    st.markdown("---")
    
    # 下部：分析选项
    st.markdown("Violin Plot")
    feature3 = st.sidebar.selectbox("Gene",                            
feature4 = st.sidebar.selectbox("meta information",
    
