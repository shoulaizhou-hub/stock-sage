import requests
from bs4 import BeautifulSoup
import jieba
from snownlp import SnowNLP
import re

class NewsAnalysis:
    def __init__(self):
        pass
    
    def get_stock_news(self, stock_code, count=10):
        news_list = []
        
        stock_code_clean = stock_code.replace('sh.', '').replace('sz.', '')
        
        try:
            url = f"https://guba.eastmoney.com/list,{stock_code_clean}.html"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('div', class_='articleh')[:count]
            
            for item in news_items:
                try:
                    title_tag = item.find('a')
                    if title_tag:
                        title = title_tag.get_text().strip()
                        href = 'https://guba.eastmoney.com' + title_tag['href']
                        
                        time_tag = item.find('span', class_='l5')
                        time_str = time_tag.get_text().strip() if time_tag else ''
                        
                        sentiment = self.analyze_sentiment(title)
                        
                        news_list.append({
                            'title': title,
                            'url': href,
                            'time': time_str,
                            'sentiment': sentiment,
                            'sentiment_score': self.get_sentiment_score(sentiment)
                        })
                except Exception as e:
                    continue
        except Exception as e:
            print(f"获取股吧新闻失败: {e}")
        
        try:
            url = f"https://news.baidu.com/ns?word={stock_code_clean}&tn=news&from=news&cl=2&rn={count}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('div', class_='result-op c-container xpath-log new-pmd')[:count]
            
            for item in news_items:
                try:
                    title_tag = item.find('h3', class_='news-title_1YtI1')
                    if title_tag:
                        title = title_tag.get_text().strip()
                        href = title_tag.find('a')['href']
                        
                        time_tag = item.find('span', class_='c-color-gray2 c-font-normal')
                        time_str = time_tag.get_text().strip() if time_tag else ''
                        
                        sentiment = self.analyze_sentiment(title)
                        
                        news_list.append({
                            'title': title,
                            'url': href,
                            'time': time_str,
                            'sentiment': sentiment,
                            'sentiment_score': self.get_sentiment_score(sentiment)
                        })
                except Exception as e:
                    continue
        except Exception as e:
            print(f"获取百度新闻失败: {e}")
        
        return news_list[:count]
    
    def analyze_sentiment(self, text):
        try:
            s = SnowNLP(text)
            score = s.sentiments
            if score > 0.6:
                return 'positive'
            elif score < 0.4:
                return 'negative'
            else:
                return 'neutral'
        except Exception as e:
            return 'neutral'
    
    def get_sentiment_score(self, sentiment):
        if sentiment == 'positive':
            return 1
        elif sentiment == 'negative':
            return -1
        else:
            return 0
    
    def get_sentiment_summary(self, news_list):
        if not news_list:
            return {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
        
        positive = sum(1 for n in news_list if n['sentiment'] == 'positive')
        negative = sum(1 for n in news_list if n['sentiment'] == 'negative')
        neutral = sum(1 for n in news_list if n['sentiment'] == 'neutral')
        
        return {
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'total': len(news_list),
            'score': (positive - negative) / len(news_list)
        }