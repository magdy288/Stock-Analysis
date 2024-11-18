import streamlit as st
import yfinance as yf
from datetime import datetime
import numpy as np
# st.set_page_config('Stock Analysis')
st.title('1- Technical Analysis')


symbol = st.text_input('Add a Stock Symbol', 'TSLA')
# df = yf.download(symbol, interval='1h', period='1mo')

df = yf.download(symbol, interval='1h', period='1mo')

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

 ### Prepare the result
    
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
        
        'Fibonacci_Levels': fibonacci_levels,
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

##########################################################################################################


st.metric('Current Price:' ,analysis_result['Current_Price'])

col1, col2, col3 = st.columns(3)

col1.write('Moving Averages')
col1.write(analysis_result['Moving_Averages'], unsafe_allow_html=True)
col2.write('Exponential MA')
col2.write(analysis_result['Exponential_MA'], unsafe_allow_html=True)
col3.metric('RSI',analysis_result['RSI'], delta_color='normal')


col4, col5, col6 = st.columns(3)

with col4:
    st.write('MACD')
    st.write(analysis_result['MACD'])
    
with col5:
    st.write('Bollinger_Bands')
    st.write(analysis_result['Bollinger_Bands'])
    
with col6:
    st.write('Stochastic')
    st.write(analysis_result['Stochastic'])
    
st.metric('', 'ATR',delta=analysis_result['ATR'],delta_color="normal")
st.metric('', 'OBV',delta=analysis_result['OBV'],delta_color="normal")


col7, col8 = st.columns(2)

with col7:
    st.write('Fibonacci_Levels')
    st.write(analysis_result['Fibonacci_Levels'])
with col8:
    st.write('Support_Resistance_line')
    st.write(analysis_result['Support_Resistance_line'])
    st.metric('Potential Breakout',analysis_result['potential_Breakout'], delta_color='off')
    

st.write( 'Volume MA', analysis_result['Volume-Trend'])



st.write( 'Crossover Indicators Signals', analysis_result['Crossover_Indicators'])

#########################################################################################################################################
st.title('2- Fundamental Analysis')

# ticker = st.text_input('Add a Stock Name', 'TSLA')
stock = yf.Ticker(symbol)
info = stock.info

  
# data-processing
financials = stock.financials.infer_objects(copy=False)
balance_sheet = stock.balance_sheet.infer_objects(copy=False)
cash_flow = stock.cashflow.infer_objects(copy=False)
        
# fill missing-data
financials = financials.ffill()
balance_sheet = balance_sheet.ffill()
cash_flow = cash_flow.ffill()


ratios = {
        "P/E Ratio": info.get('trailingPE'),
        "Forward P/E": info.get('forwardPE'),
        "P/B Ratio": info.get('priceToBook'),
        "P/S Ratio": info.get('priceToSalesTrailing12Months'),
        "PEG Ratio": info.get('pegRatio'),
        "Debt to Equity": info.get('debtToEquity'),
        "Current Ratio": info.get('currentRatio'),
        "Quick Ratio": info.get('quickRatio'),
        "ROE": info.get('returnOnEquity'),
        "ROA": info.get('returnOnAssets'),
        "ROIC": info.get('returnOnCapital'),
        "Gross Margin": info.get('grossMargins'),
        "Operating Margin": info.get('operatingMargins'),
        "Net Profit Margin": info.get('profitMargins'),
        "Dividend Yield": info.get('dividendYield'),
        "Payout Ratio": info.get('payoutRatio'),
    }

revenue = financials.loc['Total Revenue']
net_income = financials.loc['Net Income']
revenue_growth = revenue.pct_change(periods=-1).iloc[0] if len(revenue) > 1 else None
net_income_growth = net_income.pct_change(periods=-1).iloc[0] if len(net_income) > 1 else None

growth_rates = {
            "Revenue Growth (YoY)": revenue_growth,
            "Net Income Growth (YoY)": net_income_growth,
        }


# Valuation
market_cap = info.get('marketCap')
enterprise_value = info.get('enterpriseValue')

valuation = {
    "Market Cap": market_cap,
    "Enterprise Value": enterprise_value,
    "EV/EBITDA": info.get('enterpriseToEbitda'),
    "EV/Revenue": info.get('enterpriseToRevenue'),
}

# Future Estimates
estimates = {
    "Next Year EPS Estimate": info.get('forwardEps'),
    "Next Year Revenue Estimate": info.get('revenueEstimates', {}).get('avg'),
    "Long-term Growth Rate": info.get('longTermPotentialGrowthRate'),
}


# Simple DCF Valuation (very basic)
free_cash_flow = cash_flow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cash_flow.index else None
wacc = 0.1  # Assumed Weighted Average Cost of Capital
growth_rate = info.get('longTermPotentialGrowthRate', 0.03)
    
def simple_dcf(fcf, growth_rate, wacc, years=5):
            if fcf is None or growth_rate is None:
                return None
            terminal_value = fcf * (1 + growth_rate) / (wacc - growth_rate)
            dcf_value = sum([fcf * (1 + growth_rate) ** i / (1 + wacc) ** i for i in range(1, years + 1)])
            dcf_value += terminal_value / (1 + wacc) ** years
            return dcf_value

dcf_value = simple_dcf(free_cash_flow, growth_rate, wacc)

# Prepare the results
analysis = {
    "Company Name": info.get('longName'),
    "Sector": info.get('sector'),
    "Industry": info.get('industry'),
    "Key Ratios": ratios,
    "Growth Rates": growth_rates,
    "Valuation Metrics": valuation,
    "Future Estimates": estimates,
    "Simple DCF Valuation": dcf_value,
    "Last Updated": datetime.fromtimestamp(info.get('lastFiscalYearEnd', 0)).strftime('%Y-%m-%d'),
    "Data Retrieval Date": datetime.now().strftime('%Y-%m-%d'),
}

# Add interpretations
interpretations = {
    "P/E Ratio": "High P/E might indicate overvaluation or high growth expectations" if ratios.get('P/E Ratio', 0) > 20 else "Low P/E might indicate undervaluation or low growth expectations",
    "Debt to Equity": "High leverage" if ratios.get('Debt to Equity', 0) > 2 else "Conservative capital structure",
    "ROE": "Strong returns" if ratios.get('ROE', 0) > 0.15 else "Potential profitability issues",
    "Revenue Growth": "Strong growth" if growth_rates.get('Revenue Growth (YoY)', 0) > 0.1 else "Slowing growth",
}



st.markdown('Financials Report')
st.dataframe(financials, use_container_width=True)

st.markdown('Balance Sheet')
st.dataframe(balance_sheet, use_container_width=True)

st.markdown('Cash Flow')
st.dataframe(cash_flow, use_container_width=True)


col9, col10= st.columns(2)

with col9:
    st.write('Ratio')
    st.dataframe(ratios)

with col10:
    st.write('Revenue')
    st.write(revenue)
    st.write('Net Income')
    st.write(net_income)


col11, col12 = st.columns(2)

col11.metric(' ','Revenue Growth',revenue_growth)
col12.metric(' ','Net Income Growth',net_income_growth)

col13, col14 = st.columns(2)

col13.write('Valuation')
col13.dataframe(valuation)

col14.write('Estimates')
col14.dataframe(estimates)


col15, col16, col17 = st.columns(3)

col15.metric(' ','Free Cash Flow',free_cash_flow)
col16.metric(' ','Growth Rate',growth_rate)
col17.metric(' ','DCF Value', dcf_value)

st.write('Final Interpretations')
st.dataframe(interpretations)


st.write(analysis)