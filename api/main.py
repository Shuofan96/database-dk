from flask import Flask, render_template
import os
from flask import request, send_file
from sqlalchemy import create_engine, inspect, text
import seaborn as sns
import io
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

app = Flask(__name__,
    template_folder='../templates',
    static_folder='../assets',
)

# 从环境变量读取数据库 URI
DATABASES = {
    'vgo_db_1': os.getenv('DATABASE_URL_VGO_DB_1'),
    'vgo_db_2': os.getenv('DATABASE_URL_VGO_DB_2'),
    'vgo_db_DSZ': os.getenv('DATABASE_URL_VGO_DB_DSZ')
}

class DynamicService:
    def __init__(self, db_name=None, table_name=None):
        self.table_name = table_name
        self.db_name = db_name
        self.engine = create_engine(DATABASES[self.db_name])

    # 获取表名
    def get_table_names(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    # 获取表数据
    def get_table_data(self, table_name):
        if not table_name:
            print("Invalid table name provided.")
            return []  # 返回空列表，表示没有数据

        with self.engine.connect() as connection:
            query = text(f"SELECT * FROM `{table_name}`")
            print(f"Executing query: {query}")  # 输出 SQL 查询以进行调试
            result = connection.execute(query)

            # 获取列名
            column_names = result.keys()

            # 将每一行数据转换为字典
            rows = [dict(zip(column_names, row)) for row in result]

            return rows

    # 按样品名称分组数据表
    def get_sample_names(self):
        table_names = self.get_table_names()
        sample_names = {}
        for table in table_names:
            prefix = '_'.join(table.split('_')[:2])  # 取得前两部分作为前缀
            if prefix not in sample_names:
                sample_names[prefix] = []
            sample_names[prefix].append(table)
        return sample_names

# 图表选择页面
@app.route('/select_plot/<table_name>')
def select_plot(table_name):
    db_name = request.args.get('db_name', 'vgo_db_1')  # 获取数据库名称
    service = DynamicService(db_name=db_name)
    rows = service.get_table_data(table_name)

    # 获取列名以供选择
    column_names = rows[0].keys() if rows else []

    return render_template('select_plot.html', table_name=table_name, column_names=column_names, db_name=db_name)

# 图表生成
@app.route('/generate_plot', methods=['POST'])
def generate_plot():
    table_name = request.form['table_name']
    x_column = request.form['x_column']
    y_column = request.form['y_column']
    plot_type = request.form['plot_type']
    db_name = request.form['db_name']

    service = DynamicService(db_name=db_name)
    rows = service.get_table_data(table_name)

    # 提取数据
    x_values = [row[x_column] for row in rows]
    y_values = [row[y_column] for row in rows]

    # 使用 seaborn 和 matplotlib 生成图表
    plt.figure(figsize=(10, 6))

    if plot_type == 'line':
        sns.lineplot(x=x_values, y=y_values)
        plt.title(f'Line Plot for {table_name} ({x_column} vs {y_column})')
    elif plot_type == 'bar':
        sns.barplot(x=x_values, y=y_values)
        plt.title(f'Bar Plot for {table_name} ({x_column} vs {y_column})')
    elif plot_type == 'scatter':
        sns.scatterplot(x=x_values, y=y_values)
        plt.title(f'Scatter Plot for {table_name} ({x_column} vs {y_column})')

    # 将生成的图表保存为内存中的字节流
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  # 将文件指针移动到文件开头

    return send_file(img, mimetype='image/png')

# 示例路由，展示数据表页面
@app.route('/table_list.html')
def show_tables():
    db_name = request.args.get('db_name', 'vgo_db_1')  # 获取数据库名称，默认为'vgo_db_1'
    service = DynamicService(db_name=db_name)
    sample_names = service.get_sample_names()
    return render_template('table_list.html', sample_names=sample_names, db_name=db_name)

@app.route('/data_list/<sample_name>')
def data_list(sample_name):
    db_name = request.args.get('db_name', 'vgo_db_1')  # 获取数据库名称，默认为'vgo_db_1'
    service = DynamicService(db_name=db_name)
    tables = [table for table in service.get_table_names() if table.startswith(sample_name)]
    return render_template('data_list.html', sample_name=sample_name, tables=tables, db_name=db_name)

@app.route('/table_list/table/<table_name>')
def show_table_data(table_name):
    db_name = request.args.get('db_name', 'vgo_db_1')  # 获取数据库名称，默认为'vgo_db_1'
    try:
        service = DynamicService(db_name=db_name)
        rows = service.get_table_data(table_name)
        column_names = rows[0].keys() if rows else []  # 如果有数据，获取列名
    except Exception as e:
        print(f"Error fetching data from table `{table_name}` in `{db_name}`: {e}")
        rows = []
        column_names = []

    return render_template('table_data.html', rows=rows, column_names=column_names, table_name=table_name,
                           db_name=db_name)

@app.route('/')
@app.route('/index.html')
def home_page():
    print("Home page accessed")  # 添加调试信息
    return render_template('index.html')

@app.route('/introduce.html')
def introduction_page():
    return render_template('introduce.html')

@app.route('/index_vgo.html')
def vgo_page():
    return render_template('index_vgo.html')

@app.route('/index_crude.html')
def crude_page():
    return "Crude Page"

@app.route('/login.html')
def login_page():
    return "Login Page"


# 本地运行时启用调试模式
#if __name__ == '__main__':
    # print(f"Database connections: {DATABASES}")  # 输出用于调试
#    app.run(debug=True, port=9802)
