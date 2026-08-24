import baostock as bs
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import quote

class DataFetcher:
    def __init__(self):
        self.bs = bs
        self.stock_list_cache = None
    
    def _login_baostock(self):
        try:
            self.bs.logout()
        except:
            pass
        try:
            self.bs.login()
            print("baostock login success")
            return True
        except Exception as e:
            print(f"baostock login failed: {e}")
            return False
    
    def _get_stock_list_baostock(self):
        stocks = []
        if not self._login_baostock():
            return stocks
            
        try:
            rs = self.bs.query_stock_basic()
            while rs.next():
                row = rs.get_row_data()
                stock_code = row[0]
                stock_name = row[1]
                
                valid = False
                if stock_code.startswith('sh.6'):
                    code_num = stock_code[3:]
                    if len(code_num) == 6 and code_num.isdigit():
                        first_two = code_num[:2]
                        if first_two in ['60', '68']:
                            valid = True
                elif stock_code.startswith('sz.'):
                    code_num = stock_code[3:]
                    if len(code_num) == 6 and code_num.isdigit():
                        first_two = code_num[:2]
                        if first_two in ['00', '30']:
                            valid = True
                
                if valid:
                    stocks.append({
                        'code': stock_code,
                        'name': stock_name
                    })
            print(f"baostock获取股票列表成功，共 {len(stocks)} 只股票")
            return stocks
        except Exception as e:
            print(f"baostock获取股票列表失败: {e}")
            return []
    
    def _get_stock_list_eastmoney(self):
        stocks = []
        try:
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f27,f28,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            for item in data['data']['diff']:
                stock_code = item['f12']
                stock_name = item['f14']
                market = item['f13']
                
                bs_code = f"sh.{stock_code}" if market == 1 else f"sz.{stock_code}"
                stocks.append({
                    'code': bs_code,
                    'name': stock_name
                })
            
            print(f"eastmoney获取股票列表成功，共 {len(stocks)} 只股票")
            return stocks
        except Exception as e:
            print(f"eastmoney获取股票列表失败: {e}")
            return []
    
    def get_stock_list(self):
        if self.stock_list_cache is not None:
            return self.stock_list_cache
        
        stocks = self._get_stock_list_eastmoney()
        if not stocks:
            stocks = self._get_stock_list_baostock()
        
        self.stock_list_cache = stocks
        return stocks
    
    def _get_history_data_baostock(self, stock_code, start_date, end_date):
        if not self._login_baostock():
            return None
            
        try:
            rs = self.bs.query_history_k_data_plus(
                stock_code,
                "date,open,high,low,close,volume,amount",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="2"
            )
            
            print(f"baostock查询 {stock_code} 数据: error_code={rs.error_code}, error_msg={rs.error_msg}")
            
            if rs.error_code != '0':
                print(f"baostock查询失败: {rs.error_msg}")
                return None
            
            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                print(f"baostock未获取到 {stock_code} 的数据")
                return None
            
            df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'])
            df[['open', 'high', 'low', 'close', 'volume', 'amount']] = df[['open', 'high', 'low', 'close', 'volume', 'amount']].astype(float)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            print(f"baostock获取 {stock_code} 数据成功，共 {len(df)} 条")
            return df
        except Exception as e:
            print(f"baostock获取历史数据失败 ({stock_code}): {e}")
            return None
    
    def _get_history_data_eastmoney(self, stock_code, start_date, end_date):
        try:
            if stock_code.startswith('sh.'):
                market = 1
                code = stock_code[3:]
            else:
                market = 0
                code = stock_code[3:]
            
            url = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={market}.{code}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=2&beg={start_date.replace('-', '')}&end={end_date.replace('-', '')}"
            
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data['data'] is None:
                print(f"eastmoney未获取到 {stock_code} 的数据")
                return None
            
            klines = data['data']['klines']
            if not klines:
                print(f"eastmoney未获取到 {stock_code} 的数据")
                return None
            
            rows = []
            for kline in klines:
                parts = kline.split(',')
                rows.append({
                    'date': parts[0],
                    'open': float(parts[1]),
                    'close': float(parts[2]),
                    'high': float(parts[3]),
                    'low': float(parts[4]),
                    'volume': float(parts[5]),
                    'amount': float(parts[6]) if len(parts) > 6 else 0
                })
            
            df = pd.DataFrame(rows)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            print(f"eastmoney获取 {stock_code} 数据成功，共 {len(df)} 条")
            return df
        except Exception as e:
            print(f"eastmoney获取历史数据失败 ({stock_code}): {e}")
            return None
    
    def get_history_data(self, stock_code, start_date, end_date):
        df = self._get_history_data_eastmoney(stock_code, start_date, end_date)
        if df is None:
            df = self._get_history_data_baostock(stock_code, start_date, end_date)
        return df
    
    def get_realtime_data(self, stock_code):
        today = datetime.now().strftime('%Y-%m-%d')
        df = self.get_history_data(stock_code, today, today)
        if df is not None and len(df) > 0:
            return df.iloc[-1].to_dict()
        return None
    
    def close(self):
        self.bs.logout()