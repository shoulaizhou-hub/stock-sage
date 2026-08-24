import baostock as bs
import pandas as pd

bs.login()
print("Login success")

rs = bs.query_history_k_data_plus(
    'sh.600000',
    'date,open,high,low,close,volume,amount',
    start_date='2024-01-01',
    end_date='2026-07-12',
    frequency='d',
    adjustflag='2'
)

print(f"error_code: {rs.error_code}")
print(f"error_msg: {rs.error_msg}")

data_list = []
while rs.next():
    data_list.append(rs.get_row_data())

print(f"数据条数: {len(data_list)}")

if data_list:
    df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'])
    df[['open', 'high', 'low', 'close', 'volume', 'amount']] = df[['open', 'high', 'low', 'close', 'volume', 'amount']].astype(float)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    print(f"数据类型检查:")
    print(df.dtypes)
    print(f"最后5条数据:")
    print(df.tail())

bs.logout()