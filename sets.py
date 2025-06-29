import streamlit as st
from PIL import Image
import os

st.set_page_config(layout="wide")
st.title("图片选择展示网站")
left_col, right_col = st.columns([1, 3])
with left_col:
    # 左侧区域分为上下两部分
   st.header("🛠️ 控制面板")
    st.subheader("UMAP Plot")
    col1, col2 = st.columns(2)
with col1:
    feature1 = st.sidebar.selectbox("Gene", ["ACTA2","CD3D", "CD3E","CD4","CD8A", "CD14","CD68","CD79A","CLEC10A","COL1A1","CSF3R","DCN","FAP","FOXP3","IGHG1","IGKC","JCHAIN","KRT8","KRT18","KRT19","NKG7","TPSB2","VWF","EPCAM"])
with col2:
feature2 = st.sidebar.selectbox("Major cell type",["ACTA2"])   
submit = st.sidebar.button("GO")
  
    st.markdown("---")
    
    # 下部：分析选项
    st.subheader("Violin Plot")
col3, col4 = st.columns(2)
with col3:
    feature3 = st.sidebar.selectbox("Gene",  ["ACTA2", "CD3D", "CD8A", "CD68", "EPCAM", "VWF"])
with col4:
feature4 = st.sidebar.selectbox("meta information", ["ACTA2", "CD3D"])
    
 if submit:
    image_path = f"images/{feature1}.png" or f"images/{feature2}.png"

    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption=f"{feature1}" or f"{feature2}", use_container_width=True)
    else:
        st.warning("找不到对应的图片，请确认参数组合和文件名是否一致。")
