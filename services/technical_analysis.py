import pandas as pd
import ta

class TechnicalAnalysis:
    def __init__(self):
        pass
    
    def calculate_indicators(self, df):
        df_copy = df.copy()
        df_copy = ta.add_all_ta_features(
            df_copy,
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume",
            fillna=True
        )
        
        latest = df_copy.iloc[-1]
        
        result = {
            'price': {
                'current': float(latest['close']),
                'open': float(latest['open']),
                'high': float(latest['high']),
                'low': float(latest['low']),
                'change': float(latest['close'] - df_copy.iloc[-2]['close'] if len(df_copy) > 1 else 0),
                'change_percent': float((latest['close'] - df_copy.iloc[-2]['close']) / df_copy.iloc[-2]['close'] * 100 if len(df_copy) > 1 else 0)
            },
            'moving_average': {
                'ma5': float(latest['trend_sma_fast']),
                'ma10': float(latest['trend_sma_mid']),
                'ma20': float(latest['trend_sma_slow']),
                'ma60': float(df_copy['close'].rolling(window=60).mean().iloc[-1]),
                'ma120': float(df_copy['close'].rolling(window=120).mean().iloc[-1])
            },
            'momentum': {
                'rsi': float(latest['momentum_rsi']),
                'macd': float(latest['trend_macd']),
                'macd_signal': float(latest['trend_macd_signal']),
                'macd_hist': float(latest['trend_macd_hist']),
                'kdj_k': float(latest['momentum_stoch']),
                'kdj_d': float(latest['momentum_stoch_signal']),
                'kdj_j': float(latest['momentum_stoch_kdj']),
                'cci': float(latest['trend_cci']),
                'wr': float(latest['momentum_wr']),
                'roc': float(latest['momentum_roc'])
            },
            'volatility': {
                'atr': float(latest['volatility_atr']),
                'bb_upper': float(latest['volatility_bbh']),
                'bb_middle': float(latest['volatility_bbm']),
                'bb_lower': float(latest['volatility_bbl']),
                'bb_width': float(latest['volatility_bbw'])
            },
            'volume': {
                'current_volume': float(latest['volume']),
                'ma5_volume': float(df_copy['volume'].rolling(window=5).mean().iloc[-1]),
                'ma10_volume': float(df_copy['volume'].rolling(window=10).mean().iloc[-1])
            },
            'signal': self.generate_signal(latest, df_copy)
        }
        
        return result
    
    def generate_signal(self, latest, df):
        signals = []
        
        if latest['momentum_rsi'] > 70:
            signals.append('RSI超买，可能回调')
        elif latest['momentum_rsi'] < 30:
            signals.append('RSI超卖，可能反弹')
        
        if latest['trend_macd'] > latest['trend_macd_signal']:
            signals.append('MACD金叉，看涨信号')
        else:
            signals.append('MACD死叉，看跌信号')
        
        if latest['close'] > latest['trend_sma_fast'] and latest['trend_sma_fast'] > latest['trend_sma_slow']:
            signals.append('均线多头排列')
        elif latest['close'] < latest['trend_sma_fast'] and latest['trend_sma_fast'] < latest['trend_sma_slow']:
            signals.append('均线空头排列')
        
        if latest['close'] > latest['volatility_bbh']:
            signals.append('股价突破布林带上轨')
        elif latest['close'] < latest['volatility_bbl']:
            signals.append('股价跌破布林带下轨')
        
        if len(signals) == 0:
            signals.append('暂无明显信号')
        
        return signals