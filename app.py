import os
from flask import Flask, send_file, jsonify, request,render_template
import pandas as pd

def search_third_column(csv_file, col1_value, col2_value):
    # 读取CSV文件
    df = pd.read_csv(csv_file)
    
    # 匹配前两列的值，获取对应的第三列数据
    # 假设CSV的列名分别为'col1'、'col2'、'col3'，可根据实际列名修改
    result = df[(df['Gene'] == col1_value) & (df['Meta information'] == col2_value)]['image_path']
    
    # 处理结果
    if not result.empty:
        return result.values[0]  # 返回匹配到的第三列值
    else:
        return "未找到匹配的数据"

app = Flask(__name__)
# 配置 PDF 存储目录，这里使用当前目录下的 pdfs 文件夹
PDF_FOLDER = os.path.join(os.getcwd(), 'static/umap_figure')
os.makedirs(PDF_FOLDER, exist_ok=True)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/pdfs',methods={'POST'})
def serve_pdf():
    i3 = request.form.get('plotType')
    if i3 == 'umap':
        csv_path = "mapping.csv"  # 替换为你的CSV文件路径
    else:
        csv_path = "mapping-violin.csv" 
    input_col1 = request.form.get('gene')
    input_col2 = request.form.get('cellType')
    #i3 = request.form.get('plotType')
    print(input_col1,input_col2)
    third_col_value = search_third_column(csv_path, input_col1, input_col2)
    print(f"对应的第三列值为：{third_col_value}")
    
    return jsonify({'success':'success','type':i3,'pdfUrl':'static/'+third_col_value})
    
if __name__ == '__main__':
    app.run(debug=True)

