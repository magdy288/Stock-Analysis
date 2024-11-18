import streamlit as st
import yfinance as yf
from datetime import datetime
from tech import analysis_results

# st.set_page_config('Stock Analysis')
st.title('1- Technical Analysis')


symbol = st.text_input('Add a Stock Symbol', 'TSLA')
# df = yf.download(symbol, interval='1h', period='1mo')

df = yf.download(symbol, interval='1h', period='1mo')

analysis_result = analysis_results(symbol)


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