import streamlit as st
from PIL import Image
import os
import sqlite3
import pandas as pd
import time
import hashlib

# 设置页面布局
st.set_page_config(
    layout="wide", 
    page_title="大规模基因数据库可视化平台",
    page_icon="🧬"
)

# 图片基础路径
BASE_IMAGE_PATH = "images"

# 创建或连接到基因数据库
@st.cache_resource
def init_database():
    conn = sqlite3.connect('genes.db', check_same_thread=False)
    c = conn.cursor()
    
    # 创建表（如果不存在）
    c.execute('''CREATE TABLE IF NOT EXISTS genes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  gene_name TEXT UNIQUE,
                  cell_group TEXT,
                  file_path TEXT,
                  last_accessed REAL)''')
    
    # 创建索引以加速搜索
    c.execute("CREATE INDEX IF NOT EXISTS idx_gene_name ON genes(gene_name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_cell_group ON genes(cell_group)")
    
    conn.commit()
    return conn

# 初始化数据库
conn = init_database()

# 函数：索引图片目录（只运行一次）
def index_image_directory():
    """索引图片目录到数据库"""
    if st.button("重新索引图片目录"):
        st.info("开始索引图片目录，这可能需要几分钟时间...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 清空现有数据
        c = conn.cursor()
        c.execute("DELETE FROM genes")
        conn.commit()
        
        # 遍历目录结构
        total_dirs = sum([len(dirs) for _, dirs, _ in os.walk(BASE_IMAGE_PATH)])
        processed_dirs = 0
        
        for root, dirs, files in os.walk(BASE_IMAGE_PATH):
            cell_group = os.path.basename(root)
            
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    gene_name = os.path.splitext(file)[0]
                    file_path = os.path.join(root, file)
                    
                    # 插入数据库
                    try:
                        c.execute("INSERT INTO genes (gene_name, cell_group, file_path) VALUES (?, ?, ?)",
                                  (gene_name, cell_group, file_path))
                    except sqlite3.IntegrityError:
                        # 忽略重复条目
                        pass
            
            processed_dirs += len(dirs)
            progress = min(1.0, processed_dirs / total_dirs)
            progress_bar.progress(progress)
            status_text.text(f"已处理: {processed_dirs}/{total_dirs} 个目录")
        
        conn.commit()
        st.success(f"索引完成！共索引 {c.execute('SELECT COUNT(*) FROM genes').fetchone()[0]} 个基因图片")
        return True
    return False

# 函数：分页获取基因列表
def get_genes_paginated(page=0, page_size=50, search_query=""):
    """分页获取基因列表"""
    c = conn.cursor()
    offset = page * page_size
    
    if search_query:
        query = f"""
        SELECT gene_name 
        FROM genes 
        WHERE gene_name LIKE ? 
        ORDER BY gene_name 
        LIMIT ? OFFSET ?
        """
        c.execute(query, (f"%{search_query}%", page_size, offset))
    else:
        query = f"""
        SELECT gene_name 
        FROM genes 
        ORDER BY gene_name 
        LIMIT ? OFFSET ?
        """
        c.execute(query, (page_size, offset))
    
    return [row[0] for row in c.fetchall()]

# 函数：获取细胞群列表
@st.cache_data(ttl=3600)
def get_cell_groups():
    """获取所有细胞群"""
    c = conn.cursor()
    c.execute("SELECT DISTINCT cell_group FROM genes ORDER BY cell_group")
    return [row[0] for row in c.fetchall()]

# 函数：获取基因数量
@st.cache_data(ttl=3600)
def get_gene_count():
    """获取基因总数"""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM genes")
    return c.fetchone()[0]

# 函数：获取图片路径
def get_image_path(cell_group, gene_name):
    """获取图片路径"""
    c = conn.cursor()
    c.execute("SELECT file_path FROM genes WHERE cell_group=? AND gene_name=?", (cell_group, gene_name))
    result = c.fetchone()
    return result[0] if result else None

# 函数：记录访问历史
def record_gene_access(gene_name):
    """记录基因访问历史"""
    c = conn.cursor()
    c.execute("UPDATE genes SET last_accessed=? WHERE gene_name=?", (time.time(), gene_name))
    conn.commit()

# 函数：获取最近访问的基因
def get_recent_genes(limit=5):
    """获取最近访问的基因"""
    c = conn.cursor()
    c.execute("SELECT gene_name FROM genes WHERE last_accessed IS NOT NULL ORDER BY last_accessed DESC LIMIT ?", (limit,))
    return [row[0] for row in c.fetchall()]

# 函数：获取热门基因
def get_popular_genes(limit=5):
    """获取热门基因（按访问次数）"""
    # 在实际应用中，可以添加访问计数列
    # 这里简化实现为最近访问的基因
    return get_recent_genes(limit)

# 应用标题
st.title("🧬 大规模基因数据库可视化平台")
st.caption("处理接近十万级基因数据的专业可视化工具")

# 检查是否需要索引
if not conn.execute("SELECT COUNT(*) FROM genes").fetchone()[0]:
    st.warning("基因数据库为空，请先索引图片目录")
    if index_image_directory():
        st.experimental_rerun()
else:
    # 获取基因总数
    total_genes = get_gene_count()
    st.sidebar.success(f"数据库已索引: **{total_genes:,}** 个基因")

# 创建左右两列布局
left_col, right_col = st.columns([1.2, 2.8])

with left_col:
    st.header("🔍 查询面板")
    
    # 细胞群选择
    cell_groups = get_cell_groups()
    selected_cell_group = st.selectbox(
        "选择细胞群", 
        cell_groups,
        index=0 if cell_groups else None,
        help="选择要分析的细胞群"
    )
    
    # 基因搜索
    search_query = st.text_input(
        "搜索基因", 
        "",
        key="gene_search",
        placeholder="输入基因名或部分名称",
        help="支持模糊搜索，输入部分基因名即可"
    )
    
    # 分页控制
    PAGE_SIZE = 25
    if 'gene_page' not in st.session_state:
        st.session_state.gene_page = 0
    
    # 获取当前页的基因
    genes = get_genes_paginated(
        st.session_state.gene_page, 
        PAGE_SIZE, 
        search_query
    )
    
    # 显示基因选择器
    if genes:
        selected_gene = st.selectbox(
            f"选择基因 (第 {st.session_state.gene_page + 1} 页)", 
            genes,
            index=0,
            help="从列表中选择一个基因"
        )
    else:
        st.warning("未找到匹配的基因")
        selected_gene = None
    
    # 分页导航
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("上一页", disabled=st.session_state.gene_page == 0):
            st.session_state.gene_page -= 1
            st.experimental_rerun()
    
    with col2:
        st.caption(f"第 {st.session_state.gene_page + 1} 页，共 {max(1, total_genes // PAGE_SIZE + 1)} 页")
    
    with col3:
        if st.button("下一页", disabled=len(genes) < PAGE_SIZE):
            st.session_state.gene_page += 1
            st.experimental_rerun()
    
    # 热门基因推荐
    st.subheader("🔥 热门基因")
    popular_genes = get_popular_genes(5)
    if popular_genes:
        cols = st.columns(len(popular_genes))
        for i, gene in enumerate(popular_genes):
            with cols[i]:
                if st.button(gene, key=f"popular_{gene}"):
                    selected_gene = gene
                    st.session_state.gene_search = gene
                    st.experimental_rerun()
    else:
        st.info("暂无热门基因数据")
    
    # 分析选项
    st.subheader("⚙️ 分析选项")
    analysis_type = st.radio(
        "选择分析类型",
        ["UMAP 可视化", "Violin 图", "热图", "点图"],
        horizontal=True
    )
    
    # 显示选项
    with st.expander("显示设置"):
        col4, col5 = st.columns(2)
        with col4:
            show_labels = st.checkbox("显示标签", value=True)
        with col5:
            color_scheme = st.selectbox("配色方案", ["Viridis", "Plasma", "Inferno", "Magma"])
    
    # 提交按钮
    submit = st.button("生成可视化", type="primary", use_container_width=True)

# 右侧结果展示区域
with right_col:
    st.header("📊 分析结果")
    
    if submit and selected_cell_group and selected_gene:
        # 获取图片路径
        image_path = get_image_path(selected_cell_group, selected_gene)
        
        if image_path:
            # 记录访问
            record_gene_access(selected_gene)
            
            try:
                # 显示加载状态
                with st.spinner(f"加载 {selected_gene} 在 {selected_cell_group} 中的表达..."):
                    img = Image.open(image_path)
                    st.image(img, caption=f"{selected_gene} 在 {selected_cell_group} 中的表达", use_container_width=True)
                    st.success("可视化加载完成")
                    
                    # 显示元数据
                    with st.expander("详细信息", expanded=True):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric("基因", selected_gene)
                            st.metric("细胞群", selected_cell_group)
                            st.metric("文件大小", f"{os.path.getsize(image_path) / 1024:.1f} KB")
                        
                        with col_info2:
                            st.metric("分析类型", analysis_type)
                            st.metric("数据库ID", hashlib.md5(f"{selected_cell_group}_{selected_gene}".encode()).hexdigest()[:8])
                            st.metric("最后访问", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    
                    # 相关基因分析
                    st.subheader("🧬 相关基因分析")
                    
                    # 模拟相关基因（实际应用中可以使用生物信息学算法）
                    cols = st.columns(4)
                    for i in range(12):
                        with cols[i % 4]:
                            st.metric(f"相关基因 {i+1}", f"GENE_{i+1000}", delta=f"{i*3.2:.1f}%")
            except Exception as e:
                st.error(f"图片加载失败: {str(e)}")
        else:
            st.error(f"找不到图片: {selected_gene} 在 {selected_cell_group}")
            st.info("可能的原因:")
            st.info("1. 该基因在所选细胞群中没有数据")
            st.info("2. 文件路径配置不正确")
            st.info("3. 数据库需要重新索引")
            
            if st.button("重新索引数据库", key="reindex"):
                if index_image_directory():
                    st.experimental_rerun()
    
    elif not submit:
        # 显示欢迎信息和统计
        st.info("👋 欢迎使用大规模基因数据库可视化平台")
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("总基因数", f"{total_genes:,}")
        with col_stats2:
            st.metric("细胞群数量", len(cell_groups))
        with col_stats3:
            st.metric("图片总数", f"{total_genes:,}")
        
        # 显示数据库使用指南
        with st.expander("使用指南", expanded=True):
            st.markdown("""
            ### 如何高效使用本平台
            
            1. **选择细胞群** - 从左侧面板选择一个细胞群类别
            2. **搜索基因** - 输入部分基因名进行搜索（支持模糊匹配）
            3. **分页浏览** - 使用上一页/下一页按钮浏览大量基因
            4. **生成可视化** - 点击"生成可视化"按钮查看结果
            
            ### 处理大规模数据的技巧：
            - 使用精确搜索减少结果集
            - 利用热门基因快速访问常用基因
            - 数据库会自动缓存最近访问的基因
            """)
        
        # 显示示例细胞群和基因
        if cell_groups and total_genes > 0:
            st.subheader("示例数据")
            
            # 随机获取一些基因展示
            sample_genes = conn.execute(
                "SELECT gene_name, cell_group FROM genes ORDER BY RANDOM() LIMIT 9"
            ).fetchall()
            
            cols = st.columns(3)
            for i, (gene, group) in enumerate(sample_genes):
                with cols[i % 3]:
                    with st.container():
                        st.caption(f"{group} / {gene}")
                        try:
                            img_path = get_image_path(group, gene)
                            if img_path and os.path.exists(img_path):
                                st.image(Image.open(img_path), use_column_width=True)
                            else:
                                st.warning("图片未找到")
                        except:
                            st.warning("图片加载失败")

# 添加自定义CSS
st.markdown("""
<style>
/* 主容器样式 */
[data-testid="stVerticalBlock"] {
    gap: 1.5rem;
}

/* 卡片样式 */
[data-testid="stExpander"] .streamlit-expanderContent {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border-left: 4px solid #3498db;
}

/* 指标样式 */
[data-testid="stMetric"] {
    background-color: #e8f4f8;
    border-radius: 8px;
    padding: 1rem;
    border-left: 3px solid #3498db;
    text-align: center;
}

/* 按钮样式 */
.stButton>button {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: background-color 0.3s;
    width: 100%;
}

.stButton>button:hover {
    background-color: #2980b9;
    color: white;
}

/* 分页按钮 */
div[data-testid="column"]:has(button:disabled) {
    opacity: 0.5;
}

/* 标题样式 */
h1, h2, h3, h4 {
    color: #2c3e50;
}

h3 {
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #ecf0f1;
}

/* 输入框样式 */
.stTextInput>div>div>input {
    border: 2px solid #3498db;
    border-radius: 4px;
}

/* 热门基因按钮 */
div[data-testid="column"] button {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
""", unsafe_allow_html=True)
