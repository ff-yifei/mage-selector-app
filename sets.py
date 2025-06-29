import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from PIL import Image
import io

# 设置页面布局
st.set_page_config(
    page_title="生物数据可视化平台",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主标题样式 */
    .main-title {
        color: #2c3e50;
        text-align: center;
        padding: 0.5rem 0;
        border-bottom: 2px solid #3498db;
        margin-bottom: 2rem;
    }
    
    /* 图表容器样式 */
    .chart-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid #e0e0e0;
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div {
        background-color: white;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 页脚样式 */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #7f8c8d;
        margin-top: 2rem;
        border-top: 1px solid #ecf0f1;
    }
</style>
""", unsafe_allow_html=True)

# 生成模拟数据
def generate_data():
    # 生成基因表达数据
    genes = ['Gene' + str(i) for i in range(1, 21)]
    cell_types = ['T细胞', 'B细胞', '巨噬细胞', '树突细胞', 'NK细胞', '中性粒细胞']
    data = {
        'Gene': np.repeat(genes, len(cell_types)),
        'CellType': np.tile(cell_types, len(genes)),
        'Expression': np.random.exponential(1, len(genes)*len(cell_types))
    }
    df = pd.DataFrame(data)
    
    # 添加一些差异表达
    df.loc[df['Gene'] == 'Gene5', 'Expression'] *= 3
    df.loc[df['Gene'] == 'Gene10', 'Expression'] *= 0.3
    df.loc[df['CellType'] == '巨噬细胞', 'Expression'] *= 1.8
    
    # 生成UMAP数据
    np.random.seed(42)
    umap_data = pd.DataFrame({
        'UMAP1': np.random.normal(0, 1, 300),
        'UMAP2': np.random.normal(0, 1, 300),
        'CellType': np.random.choice(cell_types, 300),
        'Cluster': np.random.randint(1, 7, 300)
    })
    
    # 生成GO数据
    go_terms = [
        '免疫反应', '细胞增殖', 'DNA修复', '信号转导', 
        '代谢过程', '细胞凋亡', '蛋白质折叠', '细胞粘附'
    ]
    go_data = pd.DataFrame({
        'Term': go_terms,
        'PValue': -np.log10(np.random.uniform(0.001, 0.1, len(go_terms))),
        'Count': np.random.randint(5, 50, len(go_terms))
    })
    
    return df, umap_data, go_data

# 加载数据
expr_df, umap_df, go_df = generate_data()

# 标题
st.markdown("<h1 class='main-title'>生物数据可视化分析平台</h1>", unsafe_allow_html=True)

# 创建两列布局
col1, col2 = st.columns([1, 3])

with col1:
    st.sidebar.header("分析设置")
    
    # 图表类型选择
    chart_type = st.sidebar.radio(
        "选择图表类型:",
        ["UMAP Plot", "Violin Plot", "GO分析"],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # 根据选择的图表类型显示不同的选项
    if chart_type == "UMAP Plot":
        st.sidebar.subheader("UMAP参数设置")
        color_by = st.sidebar.selectbox(
            "着色依据:",
            ["CellType", "Cluster"],
            index=0
        )
        point_size = st.sidebar.slider("点大小:", 1, 10, 5)
        show_legend = st.sidebar.checkbox("显示图例", True)
        
    elif chart_type == "Violin Plot":
        st.sidebar.subheader("小提琴图参数设置")
        selected_gene = st.sidebar.selectbox(
            "选择基因:",
            expr_df['Gene'].unique(),
            index=4
        )
        selected_cell_types = st.sidebar.multiselect(
            "选择细胞类型:",
            expr_df['CellType'].unique(),
            default=['T细胞', 'B细胞', '巨噬细胞', 'NK细胞']
        )
        show_points = st.sidebar.checkbox("显示数据点", True)
        
    elif chart_type == "GO分析":
        st.sidebar.subheader("GO分析参数设置")
        top_n = st.sidebar.slider("显示条目数量:", 5, 20, 10)
        sort_by = st.sidebar.selectbox(
            "排序方式:",
            ["P值显著性", "基因数量"],
            index=0
        )
        color_scheme = st.sidebar.selectbox(
            "配色方案:",
            ["Viridis", "Plasma", "Inferno", "Magma", "Cividis"],
            index=0
        )
    
    st.sidebar.markdown("---")
    st.sidebar.info("使用说明: 选择图表类型后，在侧边栏设置参数，图表将自动更新。")

with col2:
    # 图表展示区域
    if chart_type == "UMAP Plot":
        st.subheader("UMAP降维可视化")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 创建UMAP图
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.scatterplot(
            data=umap_df,
            x='UMAP1',
            y='UMAP2',
            hue=color_by,
            palette='viridis',
            s=point_size*20,
            alpha=0.8,
            ax=ax
        )
        
        ax.set_title(f"UMAP降维 - 按{color_by}着色", fontsize=16)
        ax.set_xlabel("UMAP1", fontsize=12)
        ax.set_ylabel("UMAP2", fontsize=12)
        
        if not show_legend:
            ax.legend_.remove()
        else:
            ax.legend(title=color_by, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 添加数据表格
        with st.expander("查看原始数据"):
            st.dataframe(umap_df.head(10))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif chart_type == "Violin Plot":
        st.subheader("基因表达小提琴图")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 过滤数据
        filtered_df = expr_df[
            (expr_df['Gene'] == selected_gene) & 
            (expr_df['CellType'].isin(selected_cell_types))
        ]
        
        # 创建小提琴图
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.violinplot(
            data=filtered_df,
            x='CellType',
            y='Expression',
            palette='Set2',
            inner='quartile',
            ax=ax
        )
        
        if show_points:
            sns.swarmplot(
                data=filtered_df,
                x='CellType',
                y='Expression',
                color='black',
                alpha=0.5,
                size=4,
                ax=ax
            )
        
        ax.set_title(f"{selected_gene}在不同细胞类型中的表达", fontsize=16)
        ax.set_xlabel("细胞类型", fontsize=12)
        ax.set_ylabel("表达水平", fontsize=12)
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig)
        
        # 添加数据摘要
        col3, col4 = st.columns(2)
        with col3:
            st.metric("选择的基因", selected_gene)
        with col4:
            st.metric("分析的细胞类型数量", len(selected_cell_types))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif chart_type == "GO分析":
        st.subheader("基因本体(GO)富集分析")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 处理数据
        sorted_go = go_df.sort_values('PValue', ascending=False).head(top_n)
        if sort_by == "基因数量":
            sorted_go = go_df.sort_values('Count').head(top_n)
        
        # 创建条形图
        fig = px.bar(
            sorted_go,
            x='Count',
            y='Term',
            orientation='h',
            color='PValue',
            color_continuous_scale=color_scheme.lower(),
            title=f"Top {top_n} GO富集条目",
            labels={'Count': '基因数量', 'Term': 'GO条目', 'PValue': '-log10(P值)'},
            height=500
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            font=dict(size=12),
            coloraxis_colorbar=dict(title='-log10(P值)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 添加数据表格
        st.write("GO富集分析结果:")
        st.dataframe(sorted_go)
        
        st.markdown('</div>', unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>生物数据可视化分析平台 &copy; 2025 | 技术支持: 生物信息学团队</p>
    <p>数据更新时间: 2025-06-26</p>
</div>
""", unsafe_allow_html=True)
