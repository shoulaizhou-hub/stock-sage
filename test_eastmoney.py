import requests

stock_code = 'sh.600000'
market = 1
code = stock_code[3:]

print("测试公司信息接口...")
url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={market}.{code}&fields=f57,f58,f116,f117,f46,f47,f48,f56"
response = requests.get(url, timeout=30)
data = response.json()
print(f"状态码: {response.status_code}")
print(f"数据: {data}")

print("\n测试财务数据接口...")
url = f"http://push2.eastmoney.com/api/qt/stock/finance/get?secid={market}.{code}&type=0"
response = requests.get(url, timeout=30)
data = response.json()
print(f"状态码: {response.status_code}")
if data['data']:
    print(f"盈利数据长度: {len(data['data'].get('profit', []))}")
    if data['data'].get('profit'):
        print(f"最新盈利数据: {data['data']['profit'][-1]}")