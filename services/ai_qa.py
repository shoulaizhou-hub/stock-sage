from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_fetcher import DataFetcher
from services.technical_analysis import TechnicalAnalysis
from services.fundamental_analysis import FundamentalAnalysis
from services.news_analysis import NewsAnalysis

class AIQA:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        self.api_key_valid = bool(api_key and api_key != 'your_api_key_here')
        
        if self.api_key_valid:
            try:
                self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key)
            except Exception as e:
                print(f"初始化OpenAI失败: {e}")
                self.api_key_valid = False
        
        self.data_fetcher = DataFetcher()
        self.tech_analysis = TechnicalAnalysis()
        self.fund_analysis = FundamentalAnalysis()
        self.news_analysis = NewsAnalysis()
    
    def _get_context(self, stock_code=None, user_preferences=None):
        context = ""
        
        if user_preferences:
            context += f"用户偏好:\n"
            context += f"风险承受能力: {user_preferences.get('risk_tolerance', '中等')}\n"
            context += f"偏好行业: {', '.join(user_preferences.get('preferred_sectors', [])) or '无'}\n"
            context += f"持有周期: {user_preferences.get('holding_period', '中等')}\n"
            context += f"资金规模: {user_preferences.get('capital_size', '中等')}\n\n"
        
        if stock_code:
            try:
                today = datetime.now().strftime('%Y-%m-%d')
                one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                df = self.data_fetcher.get_history_data(stock_code, one_month_ago, today)
                if df is not None and len(df) > 0:
                    latest = df.iloc[-1]
                    context += f"股票代码: {stock_code}\n"
                    context += f"最新价格: {latest['close']}\n"
                    context += f"今日开盘: {latest['open']}\n"
                    context += f"今日最高: {latest['high']}\n"
                    context += f"今日最低: {latest['low']}\n"
                
                indicators = self.tech_analysis.calculate_indicators(df) if df is not None else {}
                if indicators:
                    context += f"\n技术指标:\n"
                    context += f"RSI: {indicators.get('momentum', {}).get('rsi')}\n"
                    context += f"MACD: {indicators.get('momentum', {}).get('macd')}\n"
                    context += f"MA5: {indicators.get('moving_average', {}).get('ma5')}\n"
                    context += f"MA10: {indicators.get('moving_average', {}).get('ma10')}\n"
                    context += f"MA20: {indicators.get('moving_average', {}).get('ma20')}\n"
                
                fundamentals = self.fund_analysis.get_fundamental_data(stock_code)
                if fundamentals:
                    company = fundamentals.get('company', {})
                    if company:
                        context += f"\n基本面数据:\n"
                        context += f"公司名称: {company.get('name')}\n"
                        context += f"所属行业: {company.get('industry')}\n"
                        context += f"市盈率PE: {company.get('pe')}\n"
                        context += f"市净率PB: {company.get('pb')}\n"
                        context += f"每股收益EPS: {company.get('esp')}\n"
                
                news = self.news_analysis.get_stock_news(stock_code, 5)
                if news:
                    context += f"\n近期新闻:\n"
                    for item in news[:3]:
                        context += f"- {item['title']} ({item['sentiment']})\n"
            except Exception as e:
                context += f"获取股票数据时出错: {str(e)}\n"
        
        return context
    
    def ask(self, question, stock_code=None, user_preferences=None):
        if not self.api_key_valid:
            return "抱歉，AI问答功能需要配置有效的OpenAI API Key。请在.env文件中设置OPENAI_API_KEY后重新启动应用。"
        
        context = self._get_context(stock_code, user_preferences)
        
        prompt = PromptTemplate(
            input_variables=["question", "context"],
            template="你是一位专业的A股投资分析助手。请根据以下信息回答用户的问题。\n\n"
                     "用户偏好和股票相关数据:\n{context}\n\n"
                     "用户问题: {question}\n\n"
                     "请根据用户的风险承受能力、持有周期和资金规模给出个性化的分析和建议。"
                     "注意：你的回答仅供参考，不构成投资建议。"
        )
        
        try:
            chain = LLMChain(llm=self.llm, prompt=prompt)
            answer = chain.run(question=question, context=context)
            return answer
        except Exception as e:
            return f"AI回答失败: {str(e)}"
    
    def generate_report(self, stock_code, user_preferences=None):
        if not self.api_key_valid:
            return "抱歉，AI分析报告功能需要配置有效的OpenAI API Key。请在.env文件中设置OPENAI_API_KEY后重新启动应用。"
        
        report = ""
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            
            df = self.data_fetcher.get_history_data(stock_code, six_months_ago, today)
            if df is None or len(df) == 0:
                return "无法获取股票数据"
            
            indicators = self.tech_analysis.calculate_indicators(df)
            fundamentals = self.fund_analysis.get_fundamental_data(stock_code)
            news = self.news_analysis.get_stock_news(stock_code, 10)
            sentiment_summary = self.news_analysis.get_sentiment_summary(news)
            
            context = f"用户偏好:\n"
            context += f"风险承受能力: {user_preferences.get('risk_tolerance', '中等') if user_preferences else '中等'}\n"
            context += f"偏好行业: {', '.join(user_preferences.get('preferred_sectors', [])) if user_preferences else '无'}\n"
            context += f"持有周期: {user_preferences.get('holding_period', '中等') if user_preferences else '中等'}\n"
            context += f"资金规模: {user_preferences.get('capital_size', '中等') if user_preferences else '中等'}\n\n"
            
            context += f"股票代码: {stock_code}\n"
            context += f"最新价格: {indicators['price']['current']}\n"
            context += f"涨跌幅: {indicators['price']['change_percent']:.2f}%\n"
            context += f"\n技术指标:\n"
            context += f"RSI: {indicators['momentum']['rsi']:.2f}\n"
            context += f"MACD: {indicators['momentum']['macd']:.2f}\n"
            context += f"MA5: {indicators['moving_average']['ma5']:.2f}\n"
            context += f"MA10: {indicators['moving_average']['ma10']:.2f}\n"
            context += f"MA20: {indicators['moving_average']['ma20']:.2f}\n"
            context += f"\n技术信号: {', '.join(indicators['signal'])}\n"
            
            if fundamentals.get('company'):
                context += f"\n基本面:\n"
                context += f"公司名称: {fundamentals['company'].get('name')}\n"
                context += f"行业: {fundamentals['company'].get('industry')}\n"
                context += f"PE: {fundamentals['company'].get('pe')}\n"
                context += f"PB: {fundamentals['company'].get('pb')}\n"
            
            if fundamentals.get('profit'):
                context += f"ROE: {fundamentals['profit'].get('roe')}%\n"
                context += f"净利润率: {fundamentals['profit'].get('netProfitMargin')}%\n"
            
            context += f"\n舆情分析:\n"
            context += f"正面: {sentiment_summary['positive']}条\n"
            context += f"负面: {sentiment_summary['negative']}条\n"
            context += f"中性: {sentiment_summary['neutral']}条\n"
            context += f"舆情得分: {sentiment_summary['score']:.2f}\n"
            
            prompt = PromptTemplate(
                input_variables=["context"],
                template="请根据以下股票数据和用户偏好生成一份详细的投资分析报告。\n\n"
                         "数据:\n{context}\n\n"
                         "报告应包含以下部分：\n"
                         "1. 股票概况\n"
                         "2. 技术面分析（基于技术指标和信号）\n"
                         "3. 基本面分析（基于财务数据）\n"
                         "4. 舆情分析\n"
                         "5. 综合评价和个性化投资建议（根据用户风险承受能力和持有周期）\n\n"
                         "注意：你的回答仅供参考，不构成投资建议。"
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            report = chain.run(context=context)
        except Exception as e:
            report = f"生成报告失败: {str(e)}"
        
        return report