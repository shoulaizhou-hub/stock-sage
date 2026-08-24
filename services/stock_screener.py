import pandas as pd
from datetime import datetime, timedelta
from services.data_fetcher import DataFetcher

class StockScreener:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.stock_list_cache = None
        self.max_stocks_to_scan = 200
    
    def screen(self, filters):
        stocks = []
        
        try:
            if self.stock_list_cache is None:
                self.stock_list_cache = []
                stock_list = self.data_fetcher.get_stock_list()
                
                for stock in stock_list:
                    stock_code = stock['code']
                    stock_name = stock['name']
                    
                    try:
                        fund_data = self.data_fetcher.bs.query_stock_company(code=stock_code)
                        pe = None
                        pb = None
                        if fund_data.error_code == '0' and fund_data.next():
                            row = fund_data.get_row_data()
                            pe = float(row[4]) if row[4] else None
                            pb = float(row[14]) if row[14] else None
                    except:
                        pe = None
                        pb = None
                    
                    self.stock_list_cache.append({
                        'code': stock_code,
                        'name': stock_name,
                        'pe': pe,
                        'pb': pb
                    })
            
            today = datetime.now().strftime('%Y-%m-%d')
            one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            scanned_count = 0
            for stock in self.stock_list_cache:
                if scanned_count >= self.max_stocks_to_scan:
                    break
                
                stock_code = stock['code']
                stock_name = stock['name']
                pe = stock['pe']
                pb = stock['pb']
                
                if 'pe_min' in filters and pe is not None and pe < filters['pe_min']:
                    continue
                if 'pe_max' in filters and pe is not None and pe > filters['pe_max']:
                    continue
                if 'pb_min' in filters and pb is not None and pb < filters['pb_min']:
                    continue
                if 'pb_max' in filters and pb is not None and pb > filters['pb_max']:
                    continue
                
                try:
                    scanned_count += 1
                    
                    df = self.data_fetcher.get_history_data(stock_code, one_month_ago, today)
                    
                    if df is None or len(df) < 20:
                        continue
                    
                    current_price = df.iloc[-1]['close']
                    
                    if 'price_min' in filters and current_price < filters['price_min']:
                        continue
                    if 'price_max' in filters and current_price > filters['price_max']:
                        continue
                    
                    avg_volume = df['volume'].mean()
                    if 'volume_min' in filters and avg_volume < filters['volume_min']:
                        continue
                    
                    ma5 = df['close'].rolling(window=5).mean().iloc[-1]
                    ma10 = df['close'].rolling(window=10).mean().iloc[-1]
                    ma20 = df['close'].rolling(window=20).mean().iloc[-1]
                    
                    if 'ma5_above_ma10' in filters and filters['ma5_above_ma10'] and ma5 <= ma10:
                        continue
                    if 'ma5_below_ma10' in filters and filters['ma5_below_ma10'] and ma5 >= ma10:
                        continue
                    if 'ma10_above_ma20' in filters and filters['ma10_above_ma20'] and ma10 <= ma20:
                        continue
                    
                    stocks.append({
                        'code': stock_code,
                        'name': stock_name,
                        'price': float(current_price),
                        'pe': pe,
                        'pb': pb,
                        'ma5': float(ma5),
                        'ma10': float(ma10),
                        'ma20': float(ma20),
                        'avg_volume': float(avg_volume)
                    })
                except Exception as e:
                    continue
            
            stocks.sort(key=lambda x: x['price'])
        except Exception as e:
            print(f"筛选股票失败: {e}")
        
        return stocks[:50]