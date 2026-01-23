import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import altair as alt
import requests
import xml.etree.ElementTree as ET

# --- CONFIGURATION ---
st.set_page_config(page_title="Paulo Moura Dashboard", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stTextInput > div > div > input { color: #333; }
    h3 { margin-top: 2rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.5rem; font-family: 'Arial', sans-serif; color: #333; }
    h5 { color: #666; font-weight: 500; font-size: 0.9rem; margin-bottom: 0.5rem; }
    .stProgress > div > div > div > div { background-color: #87CEFA; }
    
    div.stButton > button {
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #d6d6d6;
    }
    div.stButton > button:hover {
        border-color: #31333F;
        color: #31333F;
    }
    
    a.news-link { text-decoration: none; color: #1f77b4; font-weight: 600; font-size: 0.90rem; display: block; margin-bottom: 2px;}
    a.news-link:hover { text-decoration: underline; color: #004085; }
    .news-meta { color: #888; font-size: 0.75rem; margin-bottom: 12px; display: block; border-bottom: 1px solid #eee; padding-bottom: 8px;}
    
    .fallback-btn {
        display: inline-block;
        padding: 10px 20px;
        background-color: #4169E1;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin-top: 10px;
    }
    
    .welcome-container { text-align: center; margin-top: 50px; color: #666; }
    
    /* MOAT CARDS STYLING */
    .moat-container {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .moat-card {
        flex: 1;
        min-width: 140px;
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .moat-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .moat-value { font-size: 1.1rem; font-weight: 700; color: #333; }
    .moat-good { border-top: 4px solid #28a745; }
    .moat-avg { border-top: 4px solid #ffc107; }
    .moat-bad { border-top: 4px solid #dc3545; }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def safe_get(data_dict, key, default=0):
    val = data_dict.get(key)
    return val if val is not None else default

def find_line(df, terms):
    try:
        if df is None or df.empty: return None
        for idx in df.index:
            if any(t in str(idx).lower() for t in terms):
                return df.loc[idx].sort_index()
    except: pass
    return None

def align_annual_data(dict_series):
    try:
        df_final = pd.DataFrame()
        for name, series in dict_series.items():
            if series is not None and not series.empty:
                series_year = series.groupby(series.index.year).sum()
                df_temp = pd.DataFrame({name: series_year})
                if df_final.empty: df_final = df_temp
                else: df_final = df_final.join(df_temp, how='outer')
        return df_final
    except: return pd.DataFrame()

def calculate_cagr(start_val, end_val, years):
    try:
        if start_val <= 0 or end_val <= 0: return 0
        return (end_val / start_val) ** (1 / years) - 1
    except: return 0

def format_large_number(num):
    if num is None: return "N/A"
    num = abs(num)
    if num >= 1_000_000_000: return f"${num/1_000_000_000:.1f}B"
    elif num >= 1_000_000: return f"${num/1_000_000:.1f}M"
    elif num >= 1_000: return f"${num/1_000:.0f}K"
    else: return f"${num:.0f}"

# --- SMART TRAFFIC LIGHT LOGIC ---
def get_metric_status(value, is_reit, metric_type):
    if value is None: return None, "off"
    
    if metric_type == 'payout':
        # Now based on FCF for everyone
        limit_good = 90 if is_reit else 75 
        limit_bad = 100 if is_reit else 90
        if value < limit_good: return "Safe", "normal"
        elif value > limit_bad: return "High", "inverse"
        else: return "OK", "off"

    elif metric_type == 'net_debt_ebitda':
        limit_good = 6.0 if is_reit else 3.0
        limit_bad = 7.5 if is_reit else 4.5
        if value < limit_good: return "Safe", "normal"
        elif value > limit_bad: return "High Debt", "inverse"
        else: return "Elevated", "off"

    elif metric_type == 'int_cov':
        limit_bad = 1.5
        limit_good = 3.0
        if value > limit_good: return "Safe", "normal"
        elif value < limit_bad: return "Critical", "inverse"
        else: return "Tight", "off"

    elif metric_type == 'roe' or metric_type == 'roic' or metric_type == 'profit_margin':
        limit_good = 12 if metric_type == 'roe' else 8
        limit_bad = 5
        if metric_type == 'profit_margin': limit_good = 10
        if value > limit_good: return "Good", "normal"
        elif value < limit_bad: return "Low", "inverse"
        else: return "Average", "off"

    elif metric_type == 'chowder':
        limit_good = 8 if is_reit else 12
        if value > limit_good: return "Attractive", "normal"
        else: return "Low Growth", "off"
        
    elif metric_type == 'gross_margin':
        if value > 40: return "High", "normal"
        elif value < 20: return "Low", "inverse"
        else: return "Average", "off"

    elif metric_type == 'beta':
        if value < 0.8: return "Defensive", "normal"
        elif value > 1.3: return "Volatile", "inverse"
        else: return "Market", "off"
    
    elif metric_type == 'moat_score':
        if value >= 3: return "Wide Moat", "normal"
        elif value == 2: return "Narrow Moat", "off"
        else: return "No Moat", "inverse"

    return None, "off"

# --- SMART SEARCH ---
def search_symbol(query):
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        if 'quotes' in data and len(data['quotes']) > 0:
            return data['quotes'][0]['symbol']
    except: pass
    return query.upper()

# --- GOOGLE NEWS ---
def get_google_news(ticker):
    try:
        url = f"https://news.google.com/rss/search?q={ticker}+stock+finance&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=4) 
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            news_list = []
            for item in root.findall('./channel/item')[:5]: 
                title = item.find('title').text if item.find('title') is not None else "No Title"
                link = item.find('link').text if item.find('link') is not None else "#"
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                if len(pub_date) > 16: pub_date = pub_date[:16]
                news_list.append({'title': title, 'link': link, 'date': pub_date})
            return news_list
    except: return []
    return []

# --- CHARTING ---
def create_altair_chart(data, bar_color, value_format='$.2f', y_title=''):
    try:
        if data is None or data.empty: return None
        df_chart = pd.DataFrame()
        if hasattr(data.index, 'strftime'): years = data.index.strftime('%Y')
        else: years = data.index.astype(str)

        if isinstance(data, pd.Series):
             df_chart = pd.DataFrame({'Year': years, 'Value': data.values})
        elif isinstance(data, pd.DataFrame):
             df_chart = data.copy()
             df_chart['Year'] = years
             if 'Value' not in df_chart.columns: df_chart['Value'] = df_chart.iloc[:, 0]

        df_chart = df_chart.dropna()
        if not df_chart.empty: df_chart = df_chart.sort_values('Year').tail(10)

        chart = alt.Chart(df_chart).mark_bar(
            width=30, color=bar_color, stroke='black', strokeWidth=0
        ).encode(
            x=alt.X('Year', axis=alt.Axis(title='', labelAngle=0), scale=alt.Scale(padding=0.3)),
            y=alt.Y('Value', axis=alt.Axis(title=y_title, format=value_format, grid=True, gridColor='#f0f0f0')),
            tooltip=['Year', alt.Tooltip('Value', format=value_format)]
        ).properties(height=220)
        return chart
    except: return None

def create_line_chart(data, line_color, value_format='$.2f'):
    try:
        if data is None or data.empty: return None
        df_chart = pd.DataFrame()
        if hasattr(data.index, 'strftime'): years = data.index.strftime('%Y')
        else: years = data.index.astype(str)

        if isinstance(data, pd.Series):
             df_chart = pd.DataFrame({'Year': years, 'Value': data.values})
        elif isinstance(data, pd.DataFrame):
             df_chart = data.copy()
             df_chart['Year'] = years
             if 'Value' not in df_chart.columns: df_chart['Value'] = df_chart.iloc[:, 0]

        df_chart = df_chart.dropna()
        if not df_chart.empty: df_chart = df_chart.sort_values('Year').tail(10)

        line = alt.Chart(df_chart).mark_line(color=line_color, strokeWidth=3).encode(
            x=alt.X('Year', axis=alt.Axis(title='', labelAngle=0)),
            y=alt.Y('Value', axis=alt.Axis(title='', format=value_format, grid=True, gridColor='#f0f0f0')),
             tooltip=['Year', alt.Tooltip('Value', format=value_format)]
        )
        points = alt.Chart(df_chart).mark_circle(size=80, color=line_color, opacity=1).encode(
            x='Year', y='Value', tooltip=['Year', alt.Tooltip('Value', format=value_format)]
        )
        return (line + points).properties(height=220)
    except: return None

def create_grouped_bar_chart(df_aligned, colors=None):
    try:
        if df_aligned is None or df_aligned.empty: return None
        df_chart = df_aligned.sort_index().tail(10).reset_index()
        df_chart.rename(columns={'index': 'Year'}, inplace=True)
        df_chart['Year'] = df_chart['Year'].astype(str)
        df_long = df_chart.melt('Year', var_name='Metric', value_name='Value')
        
        domain = df_long['Metric'].unique().tolist()
        range_colors = ['#4682B4', '#FFA07A', '#32CD32'][:len(domain)] 
        if colors and isinstance(colors, dict):
            range_colors = [colors.get(m, '#888888') for m in domain]

        chart = alt.Chart(df_long).mark_bar(strokeWidth=0).encode(
            x=alt.X('Year:O', axis=alt.Axis(title='', labelAngle=0), scale=alt.Scale(padding=0.3)),
            y=alt.Y('Value:Q', axis=alt.Axis(title='Value ($)', format='$.2s', grid=True, gridColor='#f0f0f0')),
            color=alt.Color('Metric:N', scale=alt.Scale(domain=domain, range=range_colors), legend=alt.Legend(title="", orient="bottom")),
            xOffset='Metric:N', 
            tooltip=['Year', 'Metric', alt.Tooltip('Value', format='$.2s')]
        ).properties(height=280)
        return chart
    except: return None

def create_insider_chart(transactions):
    try:
        if transactions is None or transactions.empty: return None
        df = transactions.reset_index()
        date_col = None
        for col in df.columns:
            if 'date' in str(col).lower(): date_col = col; break
        if not date_col: return None
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        if 'Shares' in df.columns:
             chart = alt.Chart(df).mark_circle(size=80, opacity=0.7, stroke='black', strokeWidth=1).encode(
                 x=alt.X(f'{date_col}:T', axis=alt.Axis(title='Date', format='%Y-%m')),
                 y=alt.Y('Shares:Q', axis=alt.Axis(title='Shares Traded (Log Scale)'), scale=alt.Scale(type='symlog', constant=100)),
                 color=alt.condition(alt.datum.Shares > 0, alt.value("#2ca02c"), alt.value("#d62728")),
                 tooltip=[alt.Tooltip(f'{date_col}', title='Date', format='%Y-%m-%d'), alt.Tooltip('Shares', format=','), alt.Tooltip('Text', title='Desc')]
             ).properties(height=250, title="Insider Transactions (Scatter)")
             rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='black', strokeDash=[3,3]).encode(y='y')
             return chart + rule
    except: return None
    return None

# --- UI INPUT ---
st.title("📊 Paulo Moura Dashboard")
col_input, col_btn = st.columns([4, 1]) 
with col_input:
    search_input = st.text_input("Ticker or Company Name", value="").strip()
with col_btn:
    st.write("") 
    st.write("") 
    search = st.button("🔍 Search") 

# --- MAIN LOGIC ---
if not search_input:
    st.markdown("<div class='welcome-container'><h3>👋 Welcome!</h3><p>Enter a stock ticker (e.g., <b>O</b>, <b>AAPL</b>) or company name to start analyzing.</p></div>", unsafe_allow_html=True)

if search_input:
    ticker = search_input.upper()
    if " " in ticker or len(ticker) > 5:
        with st.spinner(f"Searching for '{search_input}'..."):
            found_ticker = search_symbol(search_input)
            if found_ticker: ticker = found_ticker

    stock = yf.Ticker(ticker)
    
    try:
        hist_check = stock.history(period="1d")
        if hist_check.empty:
            st.error(f"Could not find data for '{search_input}' (Tried ticker: {ticker}).")
            st.stop()
    except:
        st.error("Connection Error."); st.stop()

    with st.spinner(f'Analyzing {ticker}...'):
        # 1. Fetch Data
        info = stock.info
        financials = stock.financials
        cashflow = stock.cashflow
        balance = stock.balance_sheet
        divs = stock.dividends
        
        # 2. Process Data
        h_net_income = find_line(cashflow, ['net income'])
        if h_net_income is None: h_net_income = find_line(financials, ['net income'])
        h_depr = find_line(cashflow, ['depreciation'])
        if h_depr is None: h_depr = find_line(financials, ['depreciation'])
        h_capex = find_line(cashflow, ['capital expenditure', 'purchase of ppe', 'property'])
        h_shares = find_line(balance, ['share issued'])
        if h_shares is None: h_shares = find_line(financials, ['basic average shares'])
        h_ocf = find_line(cashflow, ['operating cash flow', 'total cash from operating activities'])

        df_calc = align_annual_data({'NI': h_net_income, 'DEPR': h_depr, 'CAPEX': h_capex, 'SHARES': h_shares, 'OCF': h_ocf})
        series_affo_share = None
        fcf_payout_ratio = None
        
        # REIT & DIVIDEND Detection
        is_reit = False
        sector = info.get('sector', '').lower()
        industry = info.get('industry', '').lower()
        if 'reit' in sector or 'reit' in industry or 'real estate' in sector: is_reit = True
        
        has_dividends = False
        div_yield_check = safe_get(info, 'dividendRate')
        if div_yield_check and div_yield_check > 0: has_dividends = True
        if not divs.empty and divs.sum() > 0: has_dividends = True

        if not df_calc.empty:
            for col in ['NI', 'DEPR', 'CAPEX', 'OCF']: 
                if col not in df_calc.columns: df_calc[col] = 0
            
            # --- UNIVERSAL CASH METRIC (FCF or AFFO) ---
            if is_reit:
                # For REITs, OCF is often the best proxy for AFFO available freely
                if df_calc['OCF'].sum() != 0:
                    df_calc['Cash_Metric'] = df_calc['OCF']
                else:
                    df_calc['Cash_Metric'] = df_calc['NI'].fillna(0) + df_calc['DEPR'].fillna(0)
            else:
                # For Normal Stocks, FCF = OCF + CAPEX (Capex is negative)
                df_calc['Cash_Metric'] = df_calc['OCF'].fillna(0) + df_calc['CAPEX'].fillna(0)

            if 'SHARES' in df_calc.columns:
                df_calc['SHARES'] = df_calc['SHARES'].replace(0, 1)
                df_calc['Cash_Per_Share'] = df_calc['Cash_Metric'] / df_calc['SHARES']
                series_affo_share = df_calc['Cash_Per_Share']

        h_divs_paid = find_line(cashflow, ['cash dividends paid', 'dividends paid'])
        h_fcf = find_line(cashflow, ['free cash flow'])
        hist_eps = find_line(financials, ['basic eps', 'diluted eps'])
        hist_debt = find_line(balance, ['total debt', 'long term debt'])
        
        # --- METRICS ---
        h_gross_profit = find_line(financials, ['gross profit'])
        h_revenue = find_line(financials, ['total revenue', 'operating revenue'])
        series_gross_margin = None
        if h_gross_profit is not None and h_revenue is not None:
            df_gm = align_annual_data({'GP': h_gross_profit, 'Rev': h_revenue})
            if not df_gm.empty: series_gross_margin = (df_gm['GP'] / df_gm['Rev']) * 100

        h_cash = find_line(balance, ['cash and cash equivalents', 'cash', 'cash & equivalents'])
        h_ebitda = find_line(financials, ['ebitda', 'normalized ebitda'])
        if h_ebitda is None and h_net_income is not None and h_depr is not None:
             h_ebitda = h_net_income + h_depr 
        
        nd_ebitda_val = 0
        if hist_debt is not None and h_cash is not None and h_ebitda is not None:
             last_debt = hist_debt.iloc[-1]
             last_cash = h_cash.iloc[-1]
             last_ebitda = h_ebitda.iloc[-1]
             if last_ebitda > 0:
                 nd_ebitda_val = (last_debt - last_cash) / last_ebitda

        h_ebit = find_line(financials, ['ebit', 'operating income'])
        h_int_exp = find_line(financials, ['interest expense', 'interest expense non operating'])
        int_cov_val = 0
        if h_ebit is not None and h_int_exp is not None:
             last_ebit = h_ebit.iloc[-1]
             last_int = abs(h_int_exp.iloc[-1])
             if last_int > 0: int_cov_val = last_ebit / last_int

        roic_val = 0
        roe_val = safe_get(info, 'returnOnEquity')*100
        is_neg_equity = False
        h_equity = find_line(balance, ['total stockholder equity', 'total equity'])
        if h_equity is not None:
            last_equity = h_equity.iloc[-1]
            if last_equity < 0: is_neg_equity = True
            
            if h_ebit is not None and hist_debt is not None:
                 invested_capital = last_equity + hist_debt.iloc[-1] - (h_cash.iloc[-1] if h_cash is not None else 0)
                 if invested_capital > 0: roic_val = (h_ebit.iloc[-1] / invested_capital) * 100

        pe_ratio = safe_get(info, 'trailingPE')
        beta_val = safe_get(info, 'beta')

        # --- MOAT CALCULATION ---
        moat_score = 0
        moat_data = [] # (Name, Value, Class)
        
        # 1. Efficiency
        if roic_val > 15: 
            moat_score += 1
            moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-good"))
        elif roic_val > 8:
            moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-avg"))
        else:
            moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-bad"))
            
        # 2. Pricing Power
        gm_val_last = series_gross_margin.iloc[-1] if series_gross_margin is not None else 0
        if gm_val_last > 40: 
            moat_score += 1
            moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-good"))
        elif gm_val_last > 20:
            moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-avg"))
        else:
            moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-bad"))
            
        # 3. Profitability
        pm_val_calc = safe_get(info, 'profitMargins') * 100
        if pm_val_calc > 15: 
            moat_score += 1
            moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-good"))
        elif pm_val_calc > 5:
            moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-avg"))
        else:
            moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-bad"))
        
        # 4. Scale
        mkt_cap = safe_get(info, 'marketCap')
        if mkt_cap > 100_000_000_000: 
            moat_score += 1
            moat_data.append(("Scale", "Mega Cap", "moat-good"))
        elif mkt_cap > 10_000_000_000:
            moat_data.append(("Scale", "Large Cap", "moat-avg"))
        else:
            moat_data.append(("Scale", "Mid/Small", "moat-avg"))

        # --- INSIDER ---
        insider_label = "Neutral"
        insider_val_str = "N/A"
        insider_delta_display = "No recent data"
        insider_tx = None
        net_val_insider = 0
        try:
            insider_tx = stock.insider_transactions
            if insider_tx is not None and not insider_tx.empty:
                recent = insider_tx.head(20) 
                buy_count = 0
                sell_count = 0
                if 'Value' in recent.columns and 'Shares' in recent.columns:
                    for index, row in recent.iterrows():
                        val = row['Value']
                        if pd.isna(val): val = 0
                        is_buy = False
                        if row['Shares'] > 0: is_buy = True
                        if 'Text' in recent.columns:
                            txt = str(row['Text']).lower()
                            if 'sale' in txt: is_buy = False
                            elif 'purchase' in txt: is_buy = True
                        
                        if is_buy:
                            net_val_insider += val
                            buy_count += 1
                        else:
                            net_val_insider -= val 
                            sell_count += 1
                
                if net_val_insider > 0:
                    insider_label = "Net Buying"
                    insider_val_str = format_large_number(net_val_insider)
                elif net_val_insider < 0:
                    insider_label = "Net Selling"
                    insider_val_str = format_large_number(net_val_insider).replace("-", "") 
                else:
                    insider_label = "Neutral"
                    insider_val_str = "$0"
                insider_delta_display = f"{buy_count} Buys vs {sell_count} Sells"
        except: pass

        # --- DIVIDENDS & PAYOUT ---
        cagr_3, cagr_5 = 0, 0
        annual_divs = pd.Series()
        series_divs_history = None
        
        if has_dividends and not divs.empty:
            annual_divs = divs.resample('YE').sum()
            series_divs_history = annual_divs
            
            clean_divs = annual_divs.copy()
            if len(clean_divs) > 2:
                if clean_divs.iloc[-1] < (clean_divs.iloc[-2] * 0.7): clean_divs = clean_divs[:-1]
            
            if len(clean_divs) >= 4: cagr_3 = calculate_cagr(clean_divs.iloc[-4], clean_divs.iloc[-1], 3) * 100
            if len(clean_divs) >= 6: cagr_5 = calculate_cagr(clean_divs.iloc[-6], clean_divs.iloc[-1], 5) * 100
            
            # --- SUPER ROBUST PAYOUT CALCULATION (MANUAL CONSTRUCTION) ---
            # Try to build TTM FCF manually from quarterly cashflow
            try:
                # 1. Fetch Quarterly Cashflow
                q_cashflow = stock.quarterly_cashflow
                if q_cashflow is not None and not q_cashflow.empty:
                    # Get OCF line
                    line_ocf = find_line(q_cashflow, ['operating cash flow', 'total cash from operating activities'])
                    # Get Capex line
                    line_capex = find_line(q_cashflow, ['capital expenditure', 'purchase of ppe'])
                    
                    if line_ocf is not None:
                        # Sum last 4 quarters
                        ttm_ocf = line_ocf.iloc[:4].sum()
                        
                        ttm_capex = 0
                        if line_capex is not None:
                            ttm_capex = line_capex.iloc[:4].sum() # Capex is usually negative
                        
                        # FCF = OCF + Capex (if capex is negative)
                        manual_ttm_fcf = ttm_ocf + ttm_capex
                        
                        # Get Dividends Paid TTM
                        # Estimate via rate * shares (most accurate for forward looking)
                        div_rate = safe_get(info, 'dividendRate')
                        shares = safe_get(info, 'sharesOutstanding')
                        
                        if manual_ttm_fcf > 0 and div_rate > 0 and shares > 0:
                            total_div_est = div_rate * shares
                            fcf_payout_ratio = (total_div_est / manual_ttm_fcf) * 100
            except: pass

            # Fallback 2: Info TTM (if manual failed)
            if fcf_payout_ratio is None:
                try:
                    ttm_fcf = safe_get(info, 'freeCashFlow')
                    div_rate = safe_get(info, 'dividendRate')
                    shares = safe_get(info, 'sharesOutstanding')
                    if ttm_fcf > 0 and div_rate > 0 and shares > 0:
                        total_div_est = div_rate * shares
                        fcf_payout_ratio = (total_div_est / ttm_fcf) * 100
                except: pass

        series_yield_history = None
        hist_price = stock.history(period="10y")
        if has_dividends and not hist_price.empty and not divs.empty:
            avg_price_yr = hist_price['Close'].resample('YE').mean()
            sum_div_yr = divs.resample('YE').sum()
            df_yield_calc = pd.DataFrame({'Price': avg_price_yr, 'Divs': sum_div_yr}).dropna()
            df_yield_calc = df_yield_calc[df_yield_calc['Price'] > 0]
            if not df_yield_calc.empty:
                series_yield_history = (df_yield_calc['Divs'] / df_yield_calc['Price']) * 100

        news_items = get_google_news(ticker)

        # --- DASHBOARD LAYOUT ---
        st.header(f"{info.get('longName', ticker)}")
        st.caption(f"Symbol: {ticker} | Sector: {info.get('sector', 'N/A')} | Industry: {info.get('industry', 'N/A')}")
        with st.expander("Business Description", expanded=False):
            st.write(info.get('longBusinessSummary', 'Description not available.'))
        st.divider()

        # METRICS ROW
        price_curr = safe_get(info, 'currentPrice')
        div_rate_val = safe_get(info, 'dividendRate')
        div_yield_val = (div_rate_val / price_curr * 100) if (price_curr and price_curr > 0) else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Price", f"${price_curr}")
        
        # Variable to store final payout for summary
        final_payout_val = 0

        if has_dividends:
            final_payout_label = "Payout (FCF-TTM)"
            final_payout_help = "Dividends / Free Cash Flow (Trailing 12 Months). Shows the real cash safety."
            
            # Use calculated FCF Payout if valid, else fallback to GAAP
            if fcf_payout_ratio is not None and 0 < fcf_payout_ratio < 500:
                final_payout_val = fcf_payout_ratio
                if is_reit: final_payout_label = "Payout (Est. AFFO)"
            else:
                final_payout_val = safe_get(info, 'payoutRatio') * 100
                final_payout_label = "Payout (GAAP)"
                final_payout_help = "Earnings payout (Less reliable than FCF)."

            p_txt, p_col = get_metric_status(final_payout_val, is_reit, 'payout')
            
            m2.metric("Yield", f"{round(div_yield_val, 2)}%")
            m3.metric(final_payout_label, f"{round(final_payout_val, 1)}%", p_txt, delta_color=p_col, help=final_payout_help)
        else:
            mkt_cap = safe_get(info, 'marketCap')
            m2.metric("Market Cap", format_large_number(mkt_cap))
            pm_val = safe_get(info, 'profitMargins') * 100
            pm_txt, pm_col = get_metric_status(pm_val, is_reit, 'profit_margin')
            m3.metric("Profit Margin", f"{round(pm_val, 2)}%", pm_txt, delta_color=pm_col)

        # 52 WEEK
        h52 = safe_get(info, 'fiftyTwoWeekHigh')
        l52 = safe_get(info, 'fiftyTwoWeekLow')
        if h52 and l52 and price_curr:
            pct = max(0.0, min(1.0, (price_curr - l52) / (h52 - l52)))
            st.write("")
            st.markdown("**52-Week Range**", help="Where price is vs yearly Low/High. Left=Cheap? Right=Expensive?")
            st.progress(pct)
            cmin, cmax = st.columns(2)
            cmin.caption(f"Low: ${l52}")
            cmax.caption(f"High: ${h52}")

        st.divider()

        # I. PERFORMANCE
        st.markdown("### I. Financial Performance")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if is_reit:
                st.markdown("##### AFFO/Share Trend ($)", help="Adjusted Funds From Operations per Share. The 'EPS' equivalent for REITs. Rising is Good.")
                if series_affo_share is not None: st.altair_chart(create_altair_chart(series_affo_share, "#003366"), use_container_width=True)
                else: st.info("N/A")
            else:
                st.markdown("##### EPS Trend ($)", help="Accounting Earnings per Share. Rising is Ideal.")
                if hist_eps is not None: st.altair_chart(create_altair_chart(hist_eps, "#003366"), use_container_width=True)
                else: st.info("N/A")
        with c2: 
            metric_name = "Op. Cash Flow ($)" if is_reit else "FCF / Share ($)"
            st.markdown(f"##### {metric_name}", help="Real Cash Profit. Critical for dividend safety.")
            if series_affo_share is not None: st.altair_chart(create_altair_chart(series_affo_share, "#4169E1"), use_container_width=True)
            else: st.info("N/A")
        with c3: 
            st.markdown("##### Total FCF ($)", help="Total Free Cash Flow. Should be Positive and Growing.")
            if h_fcf is not None: st.altair_chart(create_altair_chart(h_fcf, "#708090", '$.2s'), use_container_width=True)
            else: st.info("N/A")
        st.divider()

        # II. STRUCTURE
        st.markdown("### II. Structure & Safety")
        h1, h2, h3 = st.columns(3)
        with h1: 
            st.markdown("##### Shares Outstanding", help="Dilution Check. Decreasing bars (Buybacks) = Ideal.")
            if h_shares is not None: st.altair_chart(create_altair_chart(h_shares, "#CC5500", '.2s'), use_container_width=True)
            else: st.info("N/A")
        with h2: 
            st.markdown("##### Total Debt ($)", help="Total Debt. Stable or Decreasing is Ideal.")
            if hist_debt is not None: st.altair_chart(create_altair_chart(hist_debt, "#800020", '$.2s'), use_container_width=True)
            else: st.info("N/A")
        with h3:
            st.markdown("##### Safety Scorecard")
            st.write("")
            col_s1, col_s2 = st.columns(2)
            
            debt_txt, debt_col = get_metric_status(nd_ebitda_val, is_reit, 'net_debt_ebitda')
            int_txt, int_col = get_metric_status(int_cov_val, is_reit, 'int_cov')
            beta_txt, beta_col = get_metric_status(beta_val, is_reit, 'beta')
            
            int_help = "EBIT / Interest Expense. Shows how easily a company can pay interest on its outstanding debt.\n\n• < 1.5x: DANGER (Zombie Company risk)\n• 1.5x - 3.0x: Caution\n• > 3.0x: Safe\n• > 10x: Rock Solid"

            with col_s1:
                st.metric("Net Debt/EBITDA", f"{round(nd_ebitda_val, 1)}x", debt_txt, delta_color=debt_col, help="Years to pay debt. Ideal: < 3x (< 6x for REITs).")
                st.metric("Interest Cov.", f"{round(int_cov_val, 1)}x", int_txt, delta_color=int_col, help=int_help)
            with col_s2:
                ins_col = "normal" if insider_label == "Net Buying" else "inverse" if insider_label == "Net Selling" else "off"
                st.metric("Insider Trend (6M)", insider_label, insider_delta_display, delta_color=ins_col, help=f"Total Value: {insider_val_str}")
                
                beta_fmt = f"{round(beta_val, 2)}" if beta_val else "N/A"
                st.metric("Beta", beta_fmt, beta_txt, delta_color=beta_col, help="Volatility. 1.0 = Market. < 0.8 = Defensive (Ideal for Safety).")

        st.divider()

        # III. VALUATION
        st.markdown("### III. Valuation & Quality")
        
        chowder_val = div_yield_val + cagr_5
        chow_txt, chow_col = get_metric_status(chowder_val, is_reit, 'chowder')
        
        roe_display = f"{round(roe_val, 2)}%"
        roe_txt, roe_col = get_metric_status(roe_val, is_reit, 'roe')
        if is_neg_equity:
            roe_display = "Neg. Equity"
            roe_txt = "Alert"
            roe_col = "off"

        roic_txt, roic_col = get_metric_status(roic_val, is_reit, 'roic')
        gm_val = series_gross_margin.iloc[-1] if series_gross_margin is not None else 0
        gm_txt, gm_col = get_metric_status(gm_val, is_reit, 'gross_margin')

        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            if has_dividends:
                st.markdown("##### Yield History (%)", help="High historical yield usually signals undervaluation (Buy Zone).")
                if series_yield_history is not None: st.altair_chart(create_line_chart(series_yield_history, "#008080", '.2f'), use_container_width=True)
                else: st.info("N/A")
            else:
                st.markdown("##### Annual Revenue History ($)", help="Top line growth is critical for non-dividend payers.")
                if h_revenue is not None: st.altair_chart(create_altair_chart(h_revenue, "#B8860B", '$.2s', "Total Revenue"), use_container_width=True)
                else: st.info("N/A")

        with r1_c2:
            st.markdown("##### Gross Margin Trend (%)", help="Pricing Power. Rising trend = Competitive Advantage. Ideal: > 40%.")
            if series_gross_margin is not None: 
                st.altair_chart(create_line_chart(series_gross_margin, "#DAA520", '.1f'), use_container_width=True)
            else: st.info("N/A")
            
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
             if has_dividends:
                 st.markdown("##### Annual Dividend History ($)", help="Staircase Pattern = Ideal.")
                 if series_divs_history is not None: st.altair_chart(create_line_chart(series_divs_history, "#228B22", '$.2f'), use_container_width=True)
                 else: st.info("N/A")
             else:
                 st.markdown("##### Net Income History ($)", help="Profit Growth over time.")
                 if h_net_income is not None: st.altair_chart(create_altair_chart(h_net_income, "#228B22", '$.2s'), use_container_width=True)
                 else: st.info("N/A")

        with r2_c2:
             st.markdown("##### Valuation & Growth Scorecard")
             st.write("")
             col_g1, col_g2, col_g3 = st.columns(3)
             with col_g1:
                 if has_dividends:
                     st.metric("Div CAGR (5y)", f"{round(cagr_5, 2)}%", help="5-Year Growth Rate.")
                     chowder_help = "Yield + 5y CAGR. Measures Total Return potential.\nIdeal:\n• General Stocks: > 12%\n• Utilities/REITs: > 8%"
                     st.metric("Chowder Rule", f"{round(chowder_val, 1)}", chow_txt, delta_color=chow_col, help=chowder_help)
                 else:
                     rev_growth = safe_get(info, 'revenueGrowth') * 100
                     st.metric("Rev Growth (YoY)", f"{round(rev_growth, 2)}%")
                     eps_growth = safe_get(info, 'earningsGrowth') * 100
                     st.metric("EPS Growth (YoY)", f"{round(eps_growth, 2)}%")

             with col_g2:
                 st.metric("ROE", roe_display, roe_txt, delta_color=roe_col, help="Return on Equity. If Neg. Equity, means buybacks > earnings.")
                 st.metric("ROIC", f"{round(roic_val, 2)}%", roic_txt, delta_color=roic_col, help="Return on Invested Capital. Ideal: > 10%.")
             with col_g3:
                 pe_fmt = "N/A"
                 if not is_reit:
                     pe_fmt = f"{round(pe_ratio, 1)}" if pe_ratio else "N/A"
                 st.metric("P/E Ratio", pe_fmt, help="Price vs Earnings. (Ignored for REITs).")
                 
                 p_fcf_display = "N/A"
                 if series_affo_share is not None and price_curr:
                     last_cash_per_share = series_affo_share.iloc[-1]
                     if last_cash_per_share > 0:
                         val_pfcf = price_curr / last_cash_per_share
                         p_fcf_display = f"{round(val_pfcf, 1)}"
                 
                 st.metric("P/FCF", p_fcf_display, help="Price vs Free Cash Flow per Share. Ideal: < 15.")
             
             st.write("")
             # VISUAL MOAT CARDS
             st.markdown("##### 🏰 Competitive Advantage (Moat)")
             
             moat_html = f"""
             <div class="moat-container">
                <div class="moat-card {moat_data[0][2]}"><div class="moat-label">{moat_data[0][0]}</div><div class="moat-value">{moat_data[0][1]}</div></div>
                <div class="moat-card {moat_data[1][2]}"><div class="moat-label">{moat_data[1][0]}</div><div class="moat-value">{moat_data[1][1]}</div></div>
                <div class="moat-card {moat_data[2][2]}"><div class="moat-label">{moat_data[2][0]}</div><div class="moat-value">{moat_data[2][1]}</div></div>
                <div class="moat-card {moat_data[3][2]}"><div class="moat-label">{moat_data[3][0]}</div><div class="moat-value">{moat_data[3][1]}</div></div>
             </div>
             """
             st.markdown(moat_html, unsafe_allow_html=True)

        st.divider()

        # IV. SAFETY (Conditional)
        st.markdown("### IV. Cash Flow & Solvency Analysis")
        df_div_safety = pd.DataFrame()
        df_debt_safety = pd.DataFrame()
        
        if h_divs_paid is not None and h_fcf is not None:
            df_div_safety = align_annual_data({'Free Cash Flow': h_fcf, 'Dividends Paid': h_divs_paid.abs()})
        if h_fcf is not None and hist_debt is not None:
            df_debt_safety = align_annual_data({'Free Cash Flow': h_fcf, 'Total Debt': hist_debt})

        if has_dividends:
            c_safe_1, c_safe_2 = st.columns(2)
            with c_safe_1:
                st.markdown("##### Dividend Safety (FCF vs Dividends)", help="Gray bar (Cash) should cover Green bar (Divs).")
                if not df_div_safety.empty:
                    st.altair_chart(create_grouped_bar_chart(df_div_safety, {'Free Cash Flow': '#2F4F4F', 'Dividends Paid': '#228B22'}), use_container_width=True)
                else: st.warning("No Data")
            with c_safe_2:
                st.markdown("##### Solvency (FCF vs Total Debt)", help="Visualizes Leverage. How many years of FCF to pay off Debt?")
                if not df_debt_safety.empty:
                    st.altair_chart(create_grouped_bar_chart(df_debt_safety, {'Free Cash Flow': '#2F4F4F', 'Total Debt': '#800000'}), use_container_width=True)
                else: st.warning("No Data")
        else:
            st.markdown("##### Solvency (FCF vs Total Debt)")
            if not df_debt_safety.empty:
                st.altair_chart(create_grouped_bar_chart(df_debt_safety, {'Free Cash Flow': '#2F4F4F', 'Total Debt': '#800000'}), use_container_width=True)
            else: st.warning("No Data")

        st.divider()

        # V. ANALYST
        st.markdown("### V. Analyst Estimates & News")
        target_price = safe_get(info, 'targetMeanPrice')
        recommendation = safe_get(info, 'recommendationKey', 'N/A').title()
        
        col_metrics, col_news = st.columns([1, 2])
        with col_metrics:
            st.markdown("##### Wall St. Consensus")
            if target_price and target_price > 0:
                upside_pot = ((target_price - price_curr) / price_curr) * 100
                st.metric("Avg Price Target", f"${round(target_price, 2)}", f"{round(upside_pot, 2)}%", help="Analyst Estimate.")
            else: st.metric("Avg Price Target", "N/A")
            st.metric("Consensus Rec.", recommendation)

        with col_news:
            st.markdown("##### Latest Headlines (Google News)")
            if news_items:
                for n in news_items:
                    st.markdown(f"<div class='news-item'><a href='{n['link']}' class='news-link' target='_blank'>• {n['title']}</a><span class='news-meta'>{n['date']}</span></div>", unsafe_allow_html=True)
            else:
                st.info("Live feed currently unavailable.")
                st.markdown(f"<a href='https://finance.yahoo.com/quote/{ticker}/news' target='_blank' class='fallback-btn'>Read Full News Coverage ➔</a>", unsafe_allow_html=True)

        # --- AUTO SUMMARY (PRO REPORT) ---
        st.write("")
        st.markdown("### 🤖 Automated Analysis")
        
        bull_points = []
        bear_points = []
        
        # 1. VALUATION (Smart P/E check)
        if pe_ratio:
            if not is_reit:
                if pe_ratio < 15: bull_points.append(f"**Value Territory:** P/E Ratio of {round(pe_ratio, 1)} suggests the stock is inexpensive.")
                elif pe_ratio > 50: bear_points.append(f"**Expensive Valuation:** P/E Ratio of {round(pe_ratio, 1)} is very high.")
        
        # 2. EFFICIENCY
        if roic_val > 15: bull_points.append(f"**High Capital Efficiency:** ROIC of {round(roic_val, 1)}% indicates strong management.")
        
        # 3. SENTIMENT
        if target_price and price_curr:
            upside = ((target_price - price_curr) / price_curr) * 100
            if upside > 15: bull_points.append(f"**Analyst Conviction:** Wall St. sees {round(upside, 1)}% upside potential.")
        
        # 4. DEBT
        d_limit = 6.0 if is_reit else 3.0
        if nd_ebitda_val < d_limit: bull_points.append(f"**Solid Balance Sheet:** Net Debt/EBITDA is safe at {round(nd_ebitda_val, 1)}x.")
        else: bear_points.append(f"**Leverage Risk:** Net Debt/EBITDA is elevated at {round(nd_ebitda_val, 1)}x.")
        
        # 5. DIVIDEND
        if has_dividends:
            p_limit = 90 if is_reit else 75
            
            # Use calculated final_payout_val
            if final_payout_val < p_limit: bull_points.append(f"**Safe Dividend:** Cash Payout Ratio is {round(final_payout_val, 1)}% (Well covered).")
            else: bear_points.append(f"**Dividend Pressure:** Cash Payout Ratio is {round(final_payout_val, 1)}% (High).")
            
            c_limit = 8 if is_reit else 12
            if (div_yield_val + cagr_5) > c_limit: bull_points.append(f"**Chowder Check Passed:** Attractive Yield + Growth combo.")
        
        # 6. INSIDER
        if net_val_insider > 0: bull_points.append("**Insider Confidence:** Management has been net buying recently.")
        
        sc1, sc2 = st.columns(2)
        with sc1:
            st.success("🟢 The Bull Case (Strengths)")
            for p in bull_points: st.markdown(f"- {p}")
            if not bull_points: st.write("None.")
            
        with sc2:
            st.error("🔴 The Bear Case (Risks)")
            for p in bear_points: st.markdown(f"- {p}")
            if not bear_points: st.write("None.")