import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

# download data

def indicators(symbol):
    df = yf.download(symbol, interval='1h', period='1mo')
    
        # basic moving-averages
    for ma in [20,50,100,200]:
            df[f'{ma}_MA'] = df['Close'].rolling(window=ma).mean()
                
            # exponental-moving-averages
    for ema in [12,26,50,140]:
            df[f'{ema}_EMA'] = df['Close'].ewm(span=ema, adjust=False).mean()
        
    # macd
    df['MACD'] = df['12_EMA'] - df['26_EMA']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # rsi
    diff_price = df['Close'].diff()
    gain = (diff_price.where(diff_price > 0, 0)).rolling(window=14).mean()
    loss = (-diff_price.where(diff_price < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 -(100 / (1+rs))
        
        # bollinger-band
    df['20_MA_BB'] = df['Close'].rolling(window=20).mean()
    df['20_std'] = df['Close'].rolling(window=20).std()
    df['Upper_BB'] = df['20_MA_BB'] + (df['20_std'] * 2)
    df['Lower_BB'] = df['20_MA_BB'] - (df['20_std'] * 2)
        
        
        # stochastic
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['%K'] = (df['Close'] - low_14) / (high_14 - low_14) * 100
    df['%D'] = df['%K'].rolling(window=3).mean()
        
        # ATR
    df['true_range'] = np.maximum(df['High'] - df['Low'],
                                    np.maximum(abs(df['High'] - df['Close'].shift()),
                                                abs(df['Low'] - df['Close'].shift())))
    df['ATR'] = df['true_range'].rolling(window=14).mean()
        
        # OBV
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).cumsum()
        
        # support & resistance levels
    df['Support'] = df['Low'].rolling(window=20).min()
    df['Resistance'] = df['High'].rolling(window=20).max()

    ## define potential-breakout
    df['Potential_Breakout'] = np.where((df['Close'] > df['Resistance'].shift(1)),'Bullish Breakout Resistance',
                                            np.where((df['Close'] < df['Support'].shift(1)),'Bearish Breakdown Support',
                                                    'No Breakout'))
        
        ## define trend
    df['Trend'] = np.where((df['Close'] > df['200_MA']) & (df['50_MA'] > df['200_MA']), 'Bullish',
                            np.where((df['Close'] < df['200_MA']) & (df['50_MA'] < df['200_MA']), 'Bearish',
                                        'Neutral'))

        # volume-analysis
    df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Trend'] = np.where(df['Volume'] > df['Volume_MA_20'], 'Above-Average-Line', 'Below-Average-Line')

    return df

def fibbo(df):
    # fibunacci-levels
    low = float(df['Close'].min())
    high = float(df['Close'].max())
    dif = high - low
        
    fibonacci_levels = {
            '100%': high,
            '76.4%': low + (dif * 0.764),
            '61.8%': low + (dif * 0.618),
            '50%': low + (dif * 0.5),
            '38.2%': low + (dif * 0.382),
            '23.6%': low + (dif * 0.236),
            '0%': low
        }
    return fibonacci_levels

 ### Prepare the result
def analysis_results(symbol):
    df = indicators(symbol)
    
    latest = df.iloc[-1]
    analysis_result = {
            'Current_Price': latest['Close'],
            'Moving_Averages': {f'{ma}_MA': latest[f'{ma}_MA'] for ma in [20,50,100,200]},
            'Exponential_MA': {f'{ema}_EMA': latest[f'{ema}_EMA'] for ema in [12,26,50,140]},
            'RSI':latest['RSI'],
            
            'MACD': {
                'MACD': latest['MACD'],
                'MACD_signal': latest['MACD_signal'],
                'MACD_hist': latest['MACD_hist']
            },
            
            'Bollinger_Bands': {
                'Upper': latest['Upper_BB'],
                'Middle': latest['20_MA_BB'],
                'Lower': latest['Lower_BB']
            },
            
            'Stochastic': {
                '%K': latest['%K'],
                '%D': latest['%D']
            },
            
            'ATR': latest['ATR'],
            'OBV': latest['OBV'],
            
            'Fibonacci_Levels': fibbo(df),
            'Support_Resistance_line': {
                'Support': latest['Support'],
                'Resistance': latest['Resistance']
            },
            
            'potential_Breakout': latest['Potential_Breakout'],
            'Trend': latest['Trend'],
            
            'Volume-Trend': {
                'Current': latest['Volume'],
                'Vol_MA': latest['Volume_MA_20'],
                'Trend': latest['Volume_Trend']
            }
    }


    ### add signal_hints based on indicators-crossover
    analysis_result['Crossover_Indicators'] = {
            'Trend-ma': 'Bullish' if latest['Close'] > latest['200_MA'] else 'Bearish',
            'RSI-sig' : 'Overbought' if latest['RSI'] > 70 else ('Oversold' if latest['RSI'] < 30 else 'Neutral'),
            'MACD-sig': 'Bullish' if latest['MACD'] > latest['MACD_signal'] else 'Bearish',
            'Stochastic-sig': 'Overbought' if latest['%K'] > 80 else ('Oversold' if latest['%K'] < 20 else 'Neutral'),
            'Bollinger_Bands-sig': 'Overbought' if latest['Close'] > latest['Upper_BB'] else ('Oversold' if latest['Close'] < latest['Lower_BB'] else 'Neutral'),
            'Volume-level': 'High' if latest['Volume'] > latest['Volume_MA_20'] else 'Low'
        }
    return analysis_result

# analysis_result = pd.DataFrame(analysis_result)

# print(analysis_result)














