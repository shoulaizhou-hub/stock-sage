from flask import Flask, render_template, request, jsonify
import sys
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.data_fetcher import DataFetcher
from services.technical_analysis import TechnicalAnalysis
from services.fundamental_analysis import FundamentalAnalysis
from services.news_analysis import NewsAnalysis
from services.stock_screener import StockScreener
from services.ai_qa import AIQA

app = Flask(__name__)

data_fetcher = DataFetcher()
tech_analysis = TechnicalAnalysis()
fund_analysis = FundamentalAnalysis()
news_analysis = NewsAnalysis()
stock_screener = StockScreener()
ai_qa = AIQA()

USER_PREFERENCES = {
    'risk_tolerance': 'medium',
    'preferred_sectors': [],
    'holding_period': 'medium',
    'capital_size': 'medium'
}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test', methods=['GET'])
def test():
    print("收到测试请求")
    return jsonify({'message': 'Hello World'})


@app.route('/api/stock_list')
def get_stock_list():
    print("收到股票列表请求")
    stocks = data_fetcher.get_stock_list()
    return jsonify(stocks)


@app.route('/api/history_data', methods=['POST'])
def get_history_data():
    print("收到历史数据请求")
    data = request.json
    print(f"请求数据: {data}")
    stock_code = data.get('stock_code')
    today = datetime.now().strftime('%Y-%m-%d')
    start_date = data.get('start_date', '2024-01-01')
    end_date = data.get('end_date', today)
    
    print(f"查询股票: {stock_code}, 时间范围: {start_date} 到 {end_date}")
    
    df = data_fetcher.get_history_data(stock_code, start_date, end_date)
    if df is None:
        print(f"获取数据失败: {stock_code}")
        return jsonify({'error': '获取数据失败'}), 500
    
    result = df.to_dict('records')
    print(f"获取数据成功，共 {len(result)} 条")
    return jsonify(result)


@app.route('/api/technical_indicators', methods=['POST'])
def get_technical_indicators():
    print("收到技术指标请求")
    data = request.json
    print(f"请求数据: {data}")
    stock_code = data.get('stock_code')
    today = datetime.now().strftime('%Y-%m-%d')
    start_date = data.get('start_date', '2024-01-01')
    end_date = data.get('end_date', today)
    
    print(f"查询股票: {stock_code}, 时间范围: {start_date} 到 {end_date}")
    
    df = data_fetcher.get_history_data(stock_code, start_date, end_date)
    if df is None:
        print(f"获取数据失败: {stock_code}")
        return jsonify({'error': '获取数据失败'}), 500
    
    indicators = tech_analysis.calculate_indicators(df)
    print("技术指标计算成功")
    return jsonify(indicators)


@app.route('/api/fundamental_data', methods=['POST'])
def get_fundamental_data():
    print("收到基本面数据请求")
    data = request.json
    print(f"请求数据: {data}")
    stock_code = data.get('stock_code')
    
    fundamentals = fund_analysis.get_fundamental_data(stock_code)
    print("基本面数据获取成功")
    return jsonify(fundamentals)


@app.route('/api/news', methods=['POST'])
def get_news():
    print("收到新闻请求")
    data = request.json
    print(f"请求数据: {data}")
    stock_code = data.get('stock_code')
    count = data.get('count', 10)
    
    news = news_analysis.get_stock_news(stock_code, count)
    print(f"获取新闻成功，共 {len(news)} 条")
    return jsonify(news)


@app.route('/api/screen_stocks', methods=['POST'])
def screen_stocks():
    print("收到筛选请求")
    data = request.json
    print(f"请求数据: {data}")
    filters = data.get('filters', {})
    
    stocks = stock_screener.screen(filters)
    print(f"筛选完成，共 {len(stocks)} 只股票")
    return jsonify(stocks)


@app.route('/api/user_preferences', methods=['GET', 'POST'])
def user_preferences():
    global USER_PREFERENCES
    if request.method == 'GET':
        return jsonify(USER_PREFERENCES)
    elif request.method == 'POST':
        data = request.json
        USER_PREFERENCES.update(data)
        return jsonify({'success': True})


@app.route('/api/ai_question', methods=['POST'])
def ai_question():
    print("收到AI问答请求")
    data = request.json
    print(f"请求数据: {data}")
    question = data.get('question')
    stock_code = data.get('stock_code')
    
    answer = ai_qa.ask(question, stock_code, USER_PREFERENCES)
    return jsonify({'answer': answer})


@app.route('/api/analysis_report', methods=['POST'])
def get_analysis_report():
    print("收到分析报告请求")
    data = request.json
    print(f"请求数据: {data}")
    stock_code = data.get('stock_code')
    
    report = ai_qa.generate_report(stock_code, USER_PREFERENCES)
    return jsonify({'report': report})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)