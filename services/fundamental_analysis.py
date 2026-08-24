import pandas as pd
import requests
from datetime import datetime
from services.data_fetcher import DataFetcher

class FundamentalAnalysis:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.bs = self.data_fetcher.bs
    
    def _get_stock_company_eastmoney(self, stock_code):
        try:
            if stock_code.startswith('sh.'):
                market = 1
                code = stock_code[3:]
            else:
                market = 0
                code = stock_code[3:]
            
            url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={market}.{code}&fields=f57,f58,f116,f117,f46,f47,f48,f56"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data['data'] is None:
                return None
            
            d = data['data']
            return {
                'code': d.get('f57', ''),
                'name': d.get('f58', ''),
                'industry': d.get('f116', ''),
                'area': d.get('f117', ''),
                'pe': float(d.get('f56', 0)) if d.get('f56') else None,
                'esp': float(d.get('f46', 0)) / 100 if d.get('f46') else None,
                'pb': float(d.get('f47', 0)) / 100 if d.get('f47') else None,
                'bvps': float(d.get('f48', 0)) / 100 if d.get('f48') else None,
                'outstanding': None,
                'totals': None,
                'totalAssets': None,
                'liquidAssets': None,
                'fixedAssets': None,
                'reserved': None,
                'reservedPerShare': None,
                'timeToMarket': ''
            }
        except Exception as e:
            print(f"eastmoney获取公司信息失败: {e}")
            return None
    
    def _get_stock_company_baostock(self, stock_code):
        try:
            rs = self.bs.query_stock_company(code=stock_code)
            if rs.error_code == '0' and rs.next():
                company_info = rs.get_row_data()
                return {
                    'code': company_info[0],
                    'name': company_info[1],
                    'industry': company_info[2],
                    'area': company_info[3],
                    'pe': float(company_info[4]) if company_info[4] else None,
                    'outstanding': float(company_info[5]) if company_info[5] else None,
                    'totals': float(company_info[6]) if company_info[6] else None,
                    'totalAssets': float(company_info[7]) if company_info[7] else None,
                    'liquidAssets': float(company_info[8]) if company_info[8] else None,
                    'fixedAssets': float(company_info[9]) if company_info[9] else None,
                    'reserved': float(company_info[10]) if company_info[10] else None,
                    'reservedPerShare': float(company_info[11]) if company_info[11] else None,
                    'esp': float(company_info[12]) if company_info[12] else None,
                    'bvps': float(company_info[13]) if company_info[13] else None,
                    'pb': float(company_info[14]) if company_info[14] else None,
                    'timeToMarket': company_info[15]
                }
        except Exception as e:
            print(f"baostock获取公司信息失败: {e}")
        return None
    
    def _get_profit_data_eastmoney(self, stock_code):
        try:
            if stock_code.startswith('sh.'):
                market = 1
                code = stock_code[3:]
            else:
                market = 0
                code = stock_code[3:]
            
            url = f"http://push2.eastmoney.com/api/qt/stock/finance/get?secid={market}.{code}&type=0"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data['data'] is None or not data['data']['profit']:
                return None
            
            profit = data['data']['profit'][-1]
            return {
                'roe': float(profit.get('F92', 0)) if profit.get('F92') else None,
                'netProfitMargin': float(profit.get('F87', 0)) if profit.get('F87') else None,
                'grossProfitMargin': float(profit.get('F85', 0)) if profit.get('F85') else None,
                'netProfit': float(profit.get('F44', 0)) if profit.get('F44') else None,
                'eps': float(profit.get('F16', 0)) if profit.get('F16') else None,
                'revenue': float(profit.get('F14', 0)) if profit.get('F14') else None
            }
        except Exception as e:
            print(f"eastmoney获取盈利数据失败: {e}")
            return None
    
    def _get_profit_data_baostock(self, stock_code):
        current_year = datetime.now().year
        for year in range(current_year, current_year - 3, -1):
            for quarter in [4, 3, 2, 1]:
                try:
                    rs = self.bs.query_profit_data(code=stock_code, year=year, quarter=quarter)
                    profit_list = []
                    while rs.next():
                        profit_list.append(rs.get_row_data())
                    
                    if profit_list:
                        profit_df = pd.DataFrame(profit_list, columns=['code', 'pubDate', 'statDate', 'roeAvg', 'npMargin', 'gpMargin', 'netProfit', 'eps', 'businessIncome', 'bips'])
                        profit_data = profit_df.iloc[0]
                        return {
                            'roe': float(profit_data['roeAvg']) if profit_data['roeAvg'] else None,
                            'netProfitMargin': float(profit_data['npMargin']) if profit_data['npMargin'] else None,
                            'grossProfitMargin': float(profit_data['gpMargin']) if profit_data['gpMargin'] else None,
                            'netProfit': float(profit_data['netProfit']) if profit_data['netProfit'] else None,
                            'eps': float(profit_data['eps']) if profit_data['eps'] else None,
                            'revenue': float(profit_data['businessIncome']) if profit_data['businessIncome'] else None
                        }
                except Exception as e:
                    continue
        return None
    
    def _get_dupont_data_eastmoney(self, stock_code):
        try:
            if stock_code.startswith('sh.'):
                market = 1
                code = stock_code[3:]
            else:
                market = 0
                code = stock_code[3:]
            
            url = f"http://push2.eastmoney.com/api/qt/stock/finance/get?secid={market}.{code}&type=4"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data['data'] is None or not data['data']['dupont']:
                return None
            
            dupont = data['data']['dupont'][-1]
            return {
                'roe': float(dupont.get('F107', 0)) if dupont.get('F107') else None,
                'assetTurnover': float(dupont.get('F108', 0)) if dupont.get('F108') else None,
                'equityMultiplier': float(dupont.get('F109', 0)) if dupont.get('F109') else None,
                'netProfitRate': float(dupont.get('F110', 0)) if dupont.get('F110') else None
            }
        except Exception as e:
            print(f"eastmoney获取杜邦数据失败: {e}")
            return None
    
    def _get_dupont_data_baostock(self, stock_code):
        current_year = datetime.now().year
        for year in range(current_year, current_year - 3, -1):
            for quarter in [4, 3, 2, 1]:
                try:
                    rs = self.bs.query_dupont_data(code=stock_code, year=year, quarter=quarter)
                    dupont_list = []
                    while rs.next():
                        dupont_list.append(rs.get_row_data())
                    
                    if dupont_list:
                        dupont_df = pd.DataFrame(dupont_list, columns=['code', 'pubDate', 'statDate', 'dupontROE', 'dupontAssetTurn', 'dupontEquityMulti', 'dupontNetProfitRate', 'dupontTotalAssets'])
                        dupont_data = dupont_df.iloc[0]
                        return {
                            'roe': float(dupont_data['dupontROE']) if dupont_data['dupontROE'] else None,
                            'assetTurnover': float(dupont_data['dupontAssetTurn']) if dupont_data['dupontAssetTurn'] else None,
                            'equityMultiplier': float(dupont_data['dupontEquityMulti']) if dupont_data['dupontEquityMulti'] else None,
                            'netProfitRate': float(dupont_data['dupontNetProfitRate']) if dupont_data['dupontNetProfitRate'] else None
                        }
                except Exception as e:
                    continue
        return None
    
    def _get_cash_flow_data_eastmoney(self, stock_code):
        try:
            if stock_code.startswith('sh.'):
                market = 1
                code = stock_code[3:]
            else:
                market = 0
                code = stock_code[3:]
            
            url = f"http://push2.eastmoney.com/api/qt/stock/finance/get?secid={market}.{code}&type=2"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data['data'] is None or not data['data']['cashflow']:
                return None
            
            cash = data['data']['cashflow'][-1]
            return {
                'cashFromSales': float(cash.get('F116', 0)) if cash.get('F116') else None,
                'returnRate': float(cash.get('F117', 0)) if cash.get('F117') else None,
                'cashFromNetProfit': float(cash.get('F118', 0)) if cash.get('F118') else None
            }
        except Exception as e:
            print(f"eastmoney获取现金流数据失败: {e}")
            return None
    
    def _get_cash_flow_data_baostock(self, stock_code):
        current_year = datetime.now().year
        for year in range(current_year, current_year - 3, -1):
            for quarter in [4, 3, 2, 1]:
                try:
                    rs = self.bs.query_cash_flow_data(code=stock_code, year=year, quarter=quarter)
                    cash_list = []
                    while rs.next():
                        cash_list.append(rs.get_row_data())
                    
                    if cash_list:
                        cash_df = pd.DataFrame(cash_list, columns=['code', 'pubDate', 'statDate', 'cfSales', 'rateOfReturn', 'cfNp', 'cashEquivNetInc', 'cashReinvest', 'cfDebtPaying'])
                        cash_data = cash_df.iloc[0]
                        return {
                            'cashFromSales': float(cash_data['cfSales']) if cash_data['cfSales'] else None,
                            'returnRate': float(cash_data['rateOfReturn']) if cash_data['rateOfReturn'] else None,
                            'cashFromNetProfit': float(cash_data['cfNp']) if cash_data['cfNp'] else None
                        }
                except Exception as e:
                    continue
        return None
    
    def get_fundamental_data(self, stock_code):
        result = {}
        
        company_data = self._get_stock_company_eastmoney(stock_code)
        if not company_data:
            company_data = self._get_stock_company_baostock(stock_code)
        if company_data:
            result['company'] = company_data
        
        profit_data = self._get_profit_data_eastmoney(stock_code)
        if not profit_data:
            profit_data = self._get_profit_data_baostock(stock_code)
        if profit_data:
            result['profit'] = profit_data
        
        dupont_data = self._get_dupont_data_eastmoney(stock_code)
        if not dupont_data:
            dupont_data = self._get_dupont_data_baostock(stock_code)
        if dupont_data:
            result['dupont'] = dupont_data
        
        cash_data = self._get_cash_flow_data_eastmoney(stock_code)
        if not cash_data:
            cash_data = self._get_cash_flow_data_baostock(stock_code)
        if cash_data:
            result['cash_flow'] = cash_data
        
        return result