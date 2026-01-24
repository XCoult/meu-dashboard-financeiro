import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import altair as alt
import requests
import xml.etree.ElementTree as ET
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Paulo Moura Dashboard", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'pt'
if 'search_term' not in st.session_state:
    st.session_state.search_term = ''

# --- TRANSLATIONS (PT / EN / FR) ---
LANG = {
    "pt": {
        "title": "Paulo Moura Dashboard",
        "search_label": "Pesquisar Ativo",
        "search_placeholder": "Ex: AAPL, O, KO...",
        "btn_search": "🔍",
        "hero_title": "Análise Financeira Profissional",
        "hero_sub": "Dados fundamentais, dividendos e valuation em segundos.",
        "card_1_title": "🛡️ Segurança",
        "card_1_text": "Análise de Dívida e Solvência.",
        "card_2_title": "💰 Dividendos",
        "card_2_text": "Histórico e Segurança do Payout.",
        "card_3_title": "🏰 Moat",
        "card_3_text": "Vantagens Competitivas Reais.",
        "ex_btn": "Ver Exemplo:",
        "loading": "A carregar dados de",
        "price": "Preço",
        "market_cap": "Valor de Mercado",
        "yield": "Dividend Yield",
        "profit_margin": "Margem Líquida",
        "perf_title": "I. Performance Financeira",
        "affo_trend": "Tendência AFFO ($)",
        "eps_trend": "Tendência EPS ($)",
        "cash_metric": "Fluxo de Caixa Operacional",
        "total_cash": "Cash Flow Total",
        "struct_title": "II. Estrutura & Segurança",
        "shares": "Ações em Circulação",
        "debt": "Dívida Total",
        "safety_score": "Scorecard de Segurança",
        "net_debt": "Dívida Líq./EBITDA",
        "int_cov": "Cob. de Juros",
        "insider": "Insiders (6M)",
        "beta": "Beta",
        "val_title": "III. Avaliação & Qualidade",
        "val_score": "Scorecard de Avaliação",
        "yield_hist": "Histórico Yield",
        "rev_hist": "Histórico Receita",
        "gm_trend": "Margem Bruta",
        "div_hist": "Histórico Dividendos",
        "ni_hist": "Lucro Líquido",
        "moat_title": "🏰 Vantagem Competitiva (Moat)",
        "safety_title": "IV. Solvência & Cash Flow",
        "div_safety": "Segurança do Dividendo",
        "solvency": "Solvência",
        "analyst_title": "V. Analistas & Notícias",
        "consensus": "Consenso",
        "target": "Preço Alvo",
        "news": "Notícias Recentes",
        "auto_summary": "🤖 Análise Automática",
        "bull": "Pontos Fortes",
        "bear": "Pontos Fracos",
        "comp_title": "VI. Comparação",
        "comp_input": "Comparar com (tickers):",
        "no_data": "Sem dados ou ticker inválido.",
        "footer": "Dados Yahoo Finance | Uso Educacional"
    },
    "en": {
        "title": "Paulo Moura Dashboard",
        "search_label": "Search Asset",
        "search_placeholder": "e.g. AAPL, O, KO...",
        "btn_search": "🔍",
        "hero_title": "Professional Financial Analysis",
        "hero_sub": "Fundamental data, dividends, and valuation in seconds.",
        "card_1_title": "🛡️ Safety",
        "card_1_text": "Debt & Solvency Analysis.",
        "card_2_title": "💰 Dividends",
        "card_2_text": "History & Payout Safety.",
        "card_3_title": "🏰 Moat",
        "card_3_text": "Competitive Advantages.",
        "ex_btn": "Try Example:",
        "loading": "Loading data for",
        "price": "Price",
        "market_cap": "Market Cap",
        "yield": "Dividend Yield",
        "profit_margin": "Net Margin",
        "perf_title": "I. Financial Performance",
        "affo_trend": "AFFO Trend ($)",
        "eps_trend": "EPS Trend ($)",
        "cash_metric": "Operating Cash Flow",
        "total_cash": "Total Cash Flow",
        "struct_title": "II. Structure & Safety",
        "shares": "Shares Outstanding",
        "debt": "Total Debt",
        "safety_score": "Safety Scorecard",
        "net_debt": "Net Debt/EBITDA",
        "int_cov": "Interest Cov.",
        "insider": "Insiders (6M)",
        "beta": "Beta",
        "val_title": "III. Valuation & Quality",
        "val_score": "Valuation Scorecard",
        "yield_hist": "Yield History",
        "rev_hist": "Revenue History",
        "gm_trend": "Gross Margin",
        "div_hist": "Dividend History",
        "ni_hist": "Net Income",
        "moat_title": "🏰 Competitive Advantage (Moat)",
        "safety_title": "IV. Solvency & Cash Flow",
        "div_safety": "Dividend Safety",
        "solvency": "Solvency",
        "analyst_title": "V. Analysts & News",
        "consensus": "Consensus",
        "target": "Price Target",
        "news": "Latest News",
        "auto_summary": "🤖 Automated Analysis",
        "bull": "Bull Case",
        "bear": "Bear Case",
        "comp_title": "VI. Comparison",
        "comp_input": "Compare with (tickers):",
        "no_data": "No data or invalid ticker.",
        "footer": "Data by Yahoo Finance | Educational Use"
    },
    "fr": {
        "title": "Tableau de Bord Paulo Moura",
        "search_label": "Rechercher un Actif",
        "search_placeholder": "ex: LVMH, AAPL, O...",
        "btn_search": "🔍",
        "hero_title": "Analyse Financière Pro",
        "hero_sub": "Données fondamentales, dividendes et valorisation.",
        "card_1_title": "🛡️ Sécurité",
        "card_1_text": "Analyse de la Dette.",
        "card_2_title": "💰 Dividendes",
        "card_2_text": "Historique et Sûreté.",
        "card_3_title": "🏰 Moat",
        "card_3_text": "Avantages Concurrentiels.",
        "ex_btn": "Exemple:",
        "loading": "Chargement des données",
        "price": "Prix",
        "market_cap": "Cap. Boursière",
        "yield": "Rendement",
        "profit_margin": "Marge Nette",
        "perf_title": "I. Performance Financière",
        "affo_trend": "Tendance AFFO ($)",
        "eps_trend": "Tendance BPA ($)",
        "cash_metric": "Flux de Trésorerie",
        "total_cash": "Cash Flow Total",
        "struct_title": "II. Structure & Sécurité",
        "shares": "Actions en Circulation",
        "debt": "Dette Totale",
        "safety_score": "Score de Sécurité",
        "net_debt": "Dette Nette/EBITDA",
        "int_cov": "Couv. Intérêts",
        "insider": "Initiés (6M)",
        "beta": "Bêta",
        "val_title": "III. Valorisation & Qualité",
        "val_score": "Score de Valorisation",
        "yield_hist": "Historique Rendement",
        "rev_hist": "Historique Revenus",
        "gm_trend": "Marge Brute",
        "div_hist": "Historique Dividendes",
        "ni_hist": "Résultat Net",
        "moat_title": "🏰 Avantage Concurrentiel (Moat)",
        "safety_title": "IV. Solvabilité & Cash Flow",
        "div_safety": "Sûreté du Dividende",
        "solvency": "Solvabilité",
        "analyst_title": "V. Analystes & Actualités",
        "consensus": "Consensus",
        "target": "Objectif de Cours",
        "news": "Actualités",
        "auto_summary": "🤖 Analyse Automatique",
        "bull": "Points Forts",
        "bear": "Points Faibles",
        "comp_title": "VI. Comparaison",
        "comp_input": "Comparer avec:",
        "no_data": "Pas de données.",
        "footer": "Données Yahoo Finance | Usage Éducatif"
    }
}

# Definir idioma atual
T = LANG[st.session_state.lang]

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Global Clean Style */
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; color: #111; letter-spacing: -0.5px; }
    
    /* Top Bar Styling */
    .lang-btn { 
        border: none; 
        background: none; 
        font-size: 1.5rem; 
        cursor: pointer; 
        padding: 5px;
        transition: transform 0.2s;
    }
    .lang-btn:hover { transform: scale(1.2); }
    
    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 60px 20px;
        margin-bottom: 30px;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #1a2a6c, #b21f1f, #fdbb2d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .hero-sub {
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 40px;
    }
    
    /* Feature Cards */
    .feature-grid {
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
    }
    .feature-card {
        background: white;
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 20px;
        width: 250px;
        text-align: left;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .feature-card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    .fc-icon { font-size: 2rem; margin-bottom: 10px; }
    .fc-title { font-weight: 700; font-size: 1.1rem; color: #333; margin-bottom: 5px; }
    .fc-text { font-size: 0.9rem; color: #777; }

    /* Moat Cards (Analysis) */
    .moat-container { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
    .moat-card { flex: 1; min-width: 140px; background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #e0e0e0; }
    .moat-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .moat-value { font-size: 1.1rem; font-weight: 700; color: #333; }
    .moat-good { border-top: 4px solid #28a745; }
    .moat-avg { border-top: 4px solid #ffc107; }
    .moat-bad { border-top: 4px solid #dc3545; }
    
    /* Buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* News */
    a.news-link { text-decoration: none; color: #0066cc; font-weight: 600; }
    .news-meta { color: #999; font-size: 0.75rem; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px; margin-bottom: 12px; display: block;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER LAYOUT (TITLE + LANG) ---
c_title, c_fill, c_lang = st.columns([6, 3, 3])

with c_title:
    st.markdown(f"### 📊 {T['title']}")

with c_lang:
    # Language Buttons aligned right
    l1, l2, l3 = st.columns(3)
    
    def set_lang(l):
        st.session_state.lang = l
        # st.rerun() # Uncomment if needed, but button click usually triggers rerun

    if l1.button("🇵🇹", use_container_width=True): set_lang('pt')
    if l2.button("🇺🇸", use_container_width=True): set_lang('en')
    if l3.button("🇫🇷", use_container_width=True): set_lang('fr')

st.markdown("---")

# --- SEARCH BAR ---
# Using a form to handle 'Enter' key and clean UI
with st.container():
    c_search, c_btn = st.columns([5, 1])
    with c_search:
        # Bind input to session state to preserve value across reloads
        query = st.text_input(
            T['search_label'], 
            value=st.session_state.search_term, 
            placeholder=T['search_placeholder'],
            label_visibility="collapsed"
        ).strip()
    
    with c_btn:
        if st.button(T['btn_search'], use_container_width=True):
            st.session_state.search_term = query # Update state explicitly

    # Update state if input changes
    if query != st.session_state.search_term:
        st.session_state.search_term = query

# --- HELPER FUNCTIONS ---
def safe_get(data_dict, key, default=0):
    if not isinstance(data_dict, dict): return default
    val = data_dict.get(key)
    return val if val is not None else default

def find_line(df, terms):
    try:
        if df is None or df.empty: return None
        df.index = df.index.map(str).str.lower()
        for idx in df.index:
            if any(t in idx for t in terms):
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

def get_metric_status(value, is_reit, metric_type):
    if value is None: return None, "off"
    
    if metric_type == 'payout':
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
        limit_bad = 1.5; limit_good = 3.0
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
    return None, "off"

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

def get_google_news(ticker):
    try:
        lang_code = st.session_state.lang
        url = f"https://news.google.com/rss/search?q={ticker}+stock+finance&hl={lang_code}&gl=US&ceid=US:{lang_code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=4) 
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

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(ticker):
    max_retries = 3
    stock = yf.Ticker(ticker)
    for i in range(max_retries):
        try:
            history = stock.history(period="10y")
            if not history.empty:
                try: info = stock.info
                except: info = {}
                fast_info_dict = {}
                try:
                    fast_info = stock.fast_info
                    fast_info_dict = {'last_price': fast_info.last_price, 'market_cap': fast_info.market_cap}
                except: pass
                
                insider = None
                try: insider = stock.insider_transactions
                except: pass

                return {
                    "info": info, "fast_info": fast_info_dict, "history": history,
                    "financials": stock.financials, "cashflow": stock.cashflow,
                    "balance": stock.balance_sheet, "dividends": stock.dividends,
                    "q_cashflow": stock.quarterly_cashflow, "insider": insider
                }
        except Exception: time.sleep(1)
    return None

def create_altair_chart(data, bar_color, value_format='$.2f', y_title=''):
    try:
        if data is None or data.empty: return None
        df_chart = pd.DataFrame()
        if hasattr(data.index, 'strftime'): years = data.index.strftime('%Y')
        else: years = data.index.astype(str)
        if isinstance(data, pd.Series): df_chart = pd.DataFrame({'Year': years, 'Value': data.values})
        elif isinstance(data, pd.DataFrame):
             df_chart = data.copy(); df_chart['Year'] = years
             if 'Value' not in df_chart.columns: df_chart['Value'] = df_chart.iloc[:, 0]
        df_chart = df_chart.dropna().sort_values('Year').tail(10)
        if df_chart.empty: return None
        return alt.Chart(df_chart).mark_bar(width=30, color=bar_color).encode(
            x=alt.X('Year', axis=alt.Axis(title='', labelAngle=0), scale=alt.Scale(padding=0.3)),
            y=alt.Y('Value', axis=alt.Axis(title=y_title, format=value_format, grid=True, gridColor='#f0f0f0')),
            tooltip=['Year', alt.Tooltip('Value', format=value_format)]
        ).properties(height=220)
    except: return None

def create_line_chart(data, line_color, value_format='$.2f'):
    try:
        if data is None or data.empty: return None
        df_chart = pd.DataFrame()
        if hasattr(data.index, 'strftime'): years = data.index.strftime('%Y')
        else: years = data.index.astype(str)
        if isinstance(data, pd.Series): df_chart = pd.DataFrame({'Year': years, 'Value': data.values})
        elif isinstance(data, pd.DataFrame):
             df_chart = data.copy(); df_chart['Year'] = years
             if 'Value' not in df_chart.columns: df_chart['Value'] = df_chart.iloc[:, 0]
        df_chart = df_chart.dropna().sort_values('Year').tail(10)
        if df_chart.empty: return None
        line = alt.Chart(df_chart).mark_line(color=line_color, strokeWidth=3).encode(
            x=alt.X('Year', axis=alt.Axis(title='', labelAngle=0)),
            y=alt.Y('Value', axis=alt.Axis(title='', format=value_format, grid=True, gridColor='#f0f0f0')),
             tooltip=['Year', alt.Tooltip('Value', format=value_format)]
        )
        points = alt.Chart(df_chart).mark_circle(size=80, color=line_color).encode(x='Year', y='Value', tooltip=['Year', alt.Tooltip('Value', format=value_format)])
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
        if colors and isinstance(colors, dict): range_colors = [colors.get(m, '#888888') for m in domain]
        return alt.Chart(df_long).mark_bar(strokeWidth=0).encode(
            x=alt.X('Year:O', axis=alt.Axis(title='', labelAngle=0), scale=alt.Scale(padding=0.3)),
            y=alt.Y('Value:Q', axis=alt.Axis(title='Value ($)', format='$.2s', grid=True, gridColor='#f0f0f0')),
            color=alt.Color('Metric:N', scale=alt.Scale(domain=domain, range=range_colors), legend=alt.Legend(title="", orient="bottom")),
            xOffset='Metric:N', tooltip=['Year', 'Metric', alt.Tooltip('Value', format='$.2s')]
        ).properties(height=280)
    except: return None

# --- LANDING PAGE (NO SEARCH) ---
if not st.session_state.search_term:
    st.markdown(f"""
    <div class='hero-container'>
        <div class='hero-title'>{T['hero_title']}</div>
        <div class='hero-sub'>{T['hero_sub']}</div>
        
        <div class='feature-grid'>
            <div class='feature-card'>
                <div class='fc-icon'>🛡️</div>
                <div class='fc-title'>{T['card_1_title']}</div>
                <div class='fc-text'>{T['card_1_text']}</div>
            </div>
            <div class='feature-card'>
                <div class='fc-icon'>💰</div>
                <div class='fc-title'>{T['card_2_title']}</div>
                <div class='fc-text'>{T['card_2_text']}</div>
            </div>
            <div class='feature-card'>
                <div class='fc-icon'>🏰</div>
                <div class='fc-title'>{T['card_3_title']}</div>
                <div class='fc-text'>{T['card_3_text']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.markdown(f"<p style='text-align:center; color:#888;'>{T['ex_btn']}</p>", unsafe_allow_html=True)
    
    # Center buttons using columns
    _, c1, c2, c3, _ = st.columns([4, 2, 2, 2, 4])
    def set_search(t):
        st.session_state.search_term = t
        
    if c1.button("🍎 AAPL"): set_search("AAPL"); st.rerun()
    if c2.button("🏘 O (Realty)"): set_search("O"); st.rerun()
    if c3.button("🥤 KO (Coke)"): set_search("KO"); st.rerun()

# --- MAIN ANALYSIS LOGIC ---
if st.session_state.search_term:
    ticker = st.session_state.search_term.upper()
    if " " in ticker or len(ticker) > 5:
        with st.spinner(f"{T['loading']}..."):
            found_ticker = search_symbol(ticker)
            if found_ticker: ticker = found_ticker

    # Fetch Data
    with st.spinner(f"{T['loading']} {ticker}..."):
        data_bundle = fetch_stock_data(ticker)
    
    if data_bundle is None:
        st.error(T['no_data'])
    else:
        # Unpack
        info = data_bundle['info']
        fast_info = data_bundle.get('fast_info', {})
        financials = data_bundle['financials']
        cashflow = data_bundle['cashflow']
        balance = data_bundle['balance']
        divs = data_bundle['dividends']
        hist_price = data_bundle['history']
        q_cashflow = data_bundle['q_cashflow']
        insider_tx = data_bundle['insider']

        # --- CALCULATIONS ---
        with st.spinner('Calculating...'):
            price_curr = fast_info.get('last_price')
            if not price_curr: price_curr = safe_get(info, 'currentPrice')
            if not price_curr and not hist_price.empty: price_curr = hist_price['Close'].iloc[-1]
            if price_curr is None: price_curr = 0.0
            
            mkt_cap = fast_info.get('market_cap')
            if not mkt_cap: mkt_cap = safe_get(info, 'marketCap')

            h_net_income = find_line(cashflow, ['net income'])
            if h_net_income is None: h_net_income = find_line(financials, ['net income'])
            h_depr = find_line(cashflow, ['depreciation'])
            if h_depr is None: h_depr = find_line(financials, ['depreciation'])
            h_capex = find_line(cashflow, ['capital expenditure', 'purchase of ppe', 'property'])
            h_shares = find_line(balance, ['share issued', 'ordinary shares number'])
            if h_shares is None: h_shares = find_line(financials, ['basic average shares'])
            h_ocf = find_line(cashflow, ['operating cash flow', 'total cash from operating activities'])

            df_calc = align_annual_data({'NI': h_net_income, 'DEPR': h_depr, 'CAPEX': h_capex, 'SHARES': h_shares, 'OCF': h_ocf})
            series_affo_share = None
            fcf_payout_ratio = None
            
            is_reit = False
            sector = str(info.get('sector', '')).lower()
            industry = str(info.get('industry', '')).lower()
            if 'reit' in sector or 'reit' in industry or 'real estate' in sector: is_reit = True
            
            has_dividends = False
            div_yield_check = safe_get(info, 'dividendRate')
            if div_yield_check and div_yield_check > 0: has_dividends = True
            if not divs.empty and divs.sum() > 0: has_dividends = True

            if not df_calc.empty:
                for col in ['NI', 'DEPR', 'CAPEX', 'OCF']: 
                    if col not in df_calc.columns: df_calc[col] = 0
                
                if is_reit:
                    if df_calc['OCF'].sum() != 0: df_calc['Cash_Metric'] = df_calc['OCF']
                    else: df_calc['Cash_Metric'] = df_calc['NI'].fillna(0) + df_calc['DEPR'].fillna(0)
                else:
                    df_calc['Cash_Metric'] = df_calc['OCF'].fillna(0) + df_calc['CAPEX'].fillna(0)

                if 'SHARES' in df_calc.columns:
                    df_calc['SHARES'] = df_calc['SHARES'].replace(0, 1)
                    df_calc['Cash_Per_Share'] = df_calc['Cash_Metric'] / df_calc['SHARES']
                    series_affo_share = df_calc['Cash_Per_Share']

            h_divs_paid = find_line(cashflow, ['cash dividends paid', 'dividends paid'])
            h_fcf = find_line(cashflow, ['free cash flow'])
            hist_eps = find_line(financials, ['basic eps', 'diluted eps'])
            hist_debt = find_line(balance, ['total debt', 'long term debt'])
            
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
                 if last_ebitda > 0: nd_ebitda_val = (last_debt - last_cash) / last_ebitda

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
            if not pe_ratio and price_curr: 
                 eps_ttm = safe_get(info, 'trailingEps')
                 if eps_ttm and eps_ttm > 0: pe_ratio = price_curr / eps_ttm

            beta_val = safe_get(info, 'beta')

            # --- MOAT SCORE ---
            moat_score = 0
            moat_data = [] 
            
            if is_reit:
                if mkt_cap and mkt_cap > 30_000_000_000: 
                    moat_score += 1; moat_data.append(("Scale", "Massive Cap", "moat-good"))
                elif mkt_cap and mkt_cap > 10_000_000_000: moat_data.append(("Scale", "Large Cap", "moat-avg"))
                else: moat_data.append(("Scale", "Mid/Small", "moat-bad"))

                gm_val_last = series_gross_margin.iloc[-1] if series_gross_margin is not None else 0
                if gm_val_last > 60: 
                    moat_score += 1; moat_data.append(("Efficiency", f"GM {round(gm_val_last,1)}%", "moat-good"))
                elif gm_val_last > 40: moat_data.append(("Efficiency", f"GM {round(gm_val_last,1)}%", "moat-avg"))
                else: moat_data.append(("Efficiency", f"GM {round(gm_val_last,1)}%", "moat-bad"))

                if nd_ebitda_val < 5.5 and nd_ebitda_val > 0:
                    moat_score += 1; moat_data.append(("Safety", f"NetDebt {round(nd_ebitda_val,1)}x", "moat-good"))
                elif nd_ebitda_val < 6.5: moat_data.append(("Safety", f"NetDebt {round(nd_ebitda_val,1)}x", "moat-avg"))
                else: moat_data.append(("Safety", "High Leverage", "moat-bad"))
                moat_data.append(("Type", "REIT", "moat-avg"))
            else:
                if roic_val > 15: 
                    moat_score += 1; moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-good"))
                elif roic_val > 8: moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-avg"))
                else: moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-bad"))
                
                gm_val_last = series_gross_margin.iloc[-1] if series_gross_margin is not None else 0
                if gm_val_last > 40: 
                    moat_score += 1; moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-good"))
                elif gm_val_last > 20: moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-avg"))
                else: moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-bad"))
                
                pm_val_calc = safe_get(info, 'profitMargins') * 100
                if pm_val_calc > 15: 
                    moat_score += 1; moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-good"))
                elif pm_val_calc > 5: moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-avg"))
                else: moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-bad"))
                
                if mkt_cap and mkt_cap > 100_000_000_000: 
                    moat_score += 1; moat_data.append(("Scale", "Mega Cap", "moat-good"))
                elif mkt_cap and mkt_cap > 10_000_000_000: moat_data.append(("Scale", "Large Cap", "moat-avg"))
                else: moat_data.append(("Scale", "Mid/Small", "moat-avg"))

        # --- INSIDER ---
        insider_label = "Neutral"
        insider_val_str = "N/A"
        insider_delta_display = "No Data"
        net_val_insider = 0
        try:
            if insider_tx is not None and not insider_tx.empty:
                recent = insider_tx.head(20) 
                buy_count, sell_count = 0, 0
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
                        if is_buy: net_val_insider += val; buy_count += 1
                        else: net_val_insider -= val; sell_count += 1
                
                if net_val_insider > 0: insider_label = "Net Buying"; insider_val_str = format_large_number(net_val_insider)
                elif net_val_insider < 0: insider_label = "Net Selling"; insider_val_str = format_large_number(net_val_insider).replace("-", "") 
                insider_delta_display = f"{buy_count} Buys / {sell_count} Sells"
        except: pass

        # --- DIVIDENDS & PAYOUT ---
        cagr_3, cagr_5 = 0, 0
        annual_divs = pd.Series()
        series_divs_history = None
        if has_dividends and not divs.empty:
            annual_divs = divs.resample('YE').sum()
            series_divs_history = annual_divs
            clean_divs = annual_divs.copy()
            if len(clean_divs) > 2 and clean_divs.iloc[-1] < (clean_divs.iloc[-2] * 0.7): clean_divs = clean_divs[:-1]
            if len(clean_divs) >= 4: cagr_3 = calculate_cagr(clean_divs.iloc[-4], clean_divs.iloc[-1], 3) * 100
            if len(clean_divs) >= 6: cagr_5 = calculate_cagr(clean_divs.iloc[-6], clean_divs.iloc[-1], 5) * 100
            
            # Payout Logic
            if is_reit:
                ttm_ocf = safe_get(info, 'operatingCashflow')
                if ttm_ocf and ttm_ocf > 0:
                    div_rate = safe_get(info, 'dividendRate')
                    shares = safe_get(info, 'sharesOutstanding')
                    if div_rate and shares:
                        total_div_est = div_rate * shares
                        fcf_payout_ratio = (total_div_est / ttm_ocf) * 100
            
            if fcf_payout_ratio is None:
                try:
                    # Manual Calc
                    if q_cashflow is not None and not q_cashflow.empty:
                        line_ocf = find_line(q_cashflow, ['operating cash flow', 'total cash from operating activities'])
                        line_capex = find_line(q_cashflow, ['capital expenditure', 'purchase of ppe'])
                        if line_ocf is not None:
                            ttm_ocf = line_ocf.iloc[:4].sum()
                            if is_reit: manual_cash_metric = ttm_ocf
                            else:
                                ttm_capex = 0
                                if line_capex is not None: ttm_capex = line_capex.iloc[:4].sum() 
                                manual_cash_metric = ttm_ocf + ttm_capex
                            div_rate = safe_get(info, 'dividendRate')
                            shares = safe_get(info, 'sharesOutstanding')
                            if manual_cash_metric > 0 and div_rate > 0 and shares > 0:
                                total_div_est = div_rate * shares
                                fcf_payout_ratio = (total_div_est / manual_cash_metric) * 100
                except: pass

        series_yield_history = None
        if has_dividends and not hist_price.empty and not divs.empty:
            avg_price_yr = hist_price['Close'].resample('YE').mean()
            sum_div_yr = divs.resample('YE').sum()
            df_yield_calc = pd.DataFrame({'Price': avg_price_yr, 'Divs': sum_div_yr}).dropna()
            df_yield_calc = df_yield_calc[df_yield_calc['Price'] > 0]
            if not df_yield_calc.empty:
                series_yield_history = (df_yield_calc['Divs'] / df_yield_calc['Price']) * 100

        news_items = get_google_news(ticker)

        # --- DISPLAY ---
        st.header(f"{info.get('longName', ticker)}")
        st.caption(f"Symbol: {ticker} | Sector: {info.get('sector', 'N/A')} | Industry: {info.get('industry', 'N/A')}")
        with st.expander("Business Description", expanded=False):
            st.write(info.get('longBusinessSummary', 'Description not available.'))
        st.divider()

        # METRICS ROW
        m1, m2, m3 = st.columns(3)
        m1.metric(T['price'], f"${round(price_curr, 2)}")
        
        div_yield_val = 0.0
        final_payout_val = 0.0
        
        if has_dividends:
            div_rate_val = safe_get(info, 'dividendRate')
            if price_curr > 0: div_yield_val = (div_rate_val / price_curr * 100)
            
            final_payout_label = "Payout (Cash Flow)"
            
            if fcf_payout_ratio is not None and 0 < fcf_payout_ratio < 500:
                final_payout_val = fcf_payout_ratio
            else:
                if not is_reit:
                    final_payout_val = safe_get(info, 'payoutRatio') * 100
                    final_payout_label = "Payout (GAAP)"
                else:
                    final_payout_val = 0
                    final_payout_label = "Payout (N/A)"

            p_txt, p_col = get_metric_status(final_payout_val, is_reit, 'payout')
            m2.metric(T['yield'], f"{round(div_yield_val, 2)}%")
            m3.metric(final_payout_label, f"{round(final_payout_val, 1)}%", p_txt, delta_color=p_col)
        else:
            m2.metric(T['market_cap'], format_large_number(mkt_cap))
            pm_val = safe_get(info, 'profitMargins') * 100
            pm_txt, pm_col = get_metric_status(pm_val, is_reit, 'profit_margin')
            m3.metric(T['profit_margin'], f"{round(pm_val, 2)}%", pm_txt, delta_color=pm_col)

        st.divider()

        # I. PERFORMANCE
        st.markdown(f"### {T['perf_title']}")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if is_reit:
                st.markdown(f"##### {T['affo_trend']}")
                if series_affo_share is not None: st.altair_chart(create_altair_chart(series_affo_share, "#003366"), use_container_width=True)
                else: st.info("N/A")
            else:
                st.markdown(f"##### {T['eps_trend']}")
                if hist_eps is not None: st.altair_chart(create_altair_chart(hist_eps, "#003366"), use_container_width=True)
                else: st.info("N/A")
        with c2: 
            st.markdown(f"##### {T['cash_metric']}")
            if series_affo_share is not None: st.altair_chart(create_altair_chart(series_affo_share, "#4169E1"), use_container_width=True)
            else: st.info("N/A")
        with c3: 
            st.markdown(f"##### {T['total_cash']}")
            data_to_show = h_ocf if is_reit else h_fcf
            if data_to_show is not None: st.altair_chart(create_altair_chart(data_to_show, "#708090", '$.2s'), use_container_width=True)
            else: st.info("N/A")
        st.divider()

        # II. STRUCTURE
        st.markdown(f"### {T['struct_title']}")
        h1, h2, h3 = st.columns(3)
        with h1: 
            st.markdown(f"##### {T['shares']}")
            if h_shares is not None: st.altair_chart(create_altair_chart(h_shares, "#CC5500", '.2s'), use_container_width=True)
            else: st.info("N/A")
        with h2: 
            st.markdown(f"##### {T['debt']}")
            if hist_debt is not None: st.altair_chart(create_altair_chart(hist_debt, "#800020", '$.2s'), use_container_width=True)
            else: st.info("N/A")
        with h3:
            st.markdown(f"##### {T['safety_score']}")
            st.write("")
            col_s1, col_s2 = st.columns(2)
            
            debt_txt, debt_col = get_metric_status(nd_ebitda_val, is_reit, 'net_debt_ebitda')
            int_txt, int_col = get_metric_status(int_cov_val, is_reit, 'int_cov')
            beta_txt, beta_col = get_metric_status(beta_val, is_reit, 'beta')
            
            with col_s1:
                st.metric(T['net_debt'], f"{round(nd_ebitda_val, 1)}x", debt_txt, delta_color=debt_col)
                st.metric(T['int_cov'], f"{round(int_cov_val, 1)}x", int_txt, delta_color=int_col)
            with col_s2:
                ins_col = "normal" if insider_label == "Net Buying" else "inverse" if insider_label == "Net Selling" else "off"
                st.metric(T['insider'], insider_label, insider_delta_display, delta_color=ins_col)
                beta_fmt = f"{round(beta_val, 2)}" if beta_val else "N/A"
                st.metric(T['beta'], beta_fmt, beta_txt, delta_color=beta_col)

        st.divider()

        # III. VALUATION
        st.markdown(f"### {T['val_title']}")
        
        chowder_val = div_yield_val + cagr_5
        chow_txt, chow_col = get_metric_status(chowder_val, is_reit, 'chowder')
        
        roe_display = f"{round(roe_val, 2)}%"
        roe_txt, roe_col = get_metric_status(roe_val, is_reit, 'roe')
        if is_neg_equity: roe_display = "Neg. Equity"; roe_txt = "Alert"; roe_col = "off"

        roic_txt, roic_col = get_metric_status(roic_val, is_reit, 'roic')
        gm_val = series_gross_margin.iloc[-1] if series_gross_margin is not None else 0
        gm_txt, gm_col = get_metric_status(gm_val, is_reit, 'gross_margin')

        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            if has_dividends:
                st.markdown(f"##### {T['yield_hist']}")
                if series_yield_history is not None: st.altair_chart(create_line_chart(series_yield_history, "#008080", '.2f'), use_container_width=True)
                else: st.info("N/A")
            else:
                st.markdown(f"##### {T['rev_hist']}")
                if h_revenue is not None: st.altair_chart(create_altair_chart(h_revenue, "#B8860B", '$.2s', "Total Revenue"), use_container_width=True)
                else: st.info("N/A")

        with r1_c2:
            st.markdown(f"##### {T['gm_trend']}")
            if series_gross_margin is not None: 
                st.altair_chart(create_line_chart(series_gross_margin, "#DAA520", '.1f'), use_container_width=True)
            else: st.info("N/A")
            
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
             if has_dividends:
                 st.markdown(f"##### {T['div_hist']}")
                 if series_divs_history is not None: st.altair_chart(create_line_chart(series_divs_history, "#228B22", '$.2f'), use_container_width=True)
                 else: st.info("N/A")
             else:
                 st.markdown(f"##### {T['ni_hist']}")
                 if h_net_income is not None: st.altair_chart(create_altair_chart(h_net_income, "#228B22", '$.2s'), use_container_width=True)
                 else: st.info("N/A")

        with r2_c2:
             st.markdown(f"##### {T['val_score']}")
             st.write("")
             col_g1, col_g2, col_g3 = st.columns(3)
             with col_g1:
                 if has_dividends:
                     st.metric(T['div_cagr'], f"{round(cagr_5, 2)}%")
                     st.metric(T['chowder'], f"{round(chowder_val, 1)}", chow_txt, delta_color=chow_col)
                 else:
                     rev_growth = safe_get(info, 'revenueGrowth') * 100
                     st.metric(T['rev_growth'], f"{round(rev_growth, 2)}%")
                     eps_growth = safe_get(info, 'earningsGrowth') * 100
                     st.metric(T['eps_growth'], f"{round(eps_growth, 2)}%")

             with col_g2:
                 st.metric("ROE", roe_display, roe_txt, delta_color=roe_col)
                 st.metric("ROIC", f"{round(roic_val, 2)}%", roic_txt, delta_color=roic_col)
             with col_g3:
                 pe_fmt = "N/A"
                 if not is_reit: pe_fmt = f"{round(pe_ratio, 1)}" if pe_ratio else "N/A"
                 st.metric("P/E Ratio", pe_fmt)
                 p_fcf_display = "N/A"
                 if series_affo_share is not None and price_curr:
                     last_cash_per_share = series_affo_share.iloc[-1]
                     if last_cash_per_share > 0:
                         val_pfcf = price_curr / last_cash_per_share
                         p_fcf_display = f"{round(val_pfcf, 1)}"
                 st.metric("P/FCF", p_fcf_display)
             
             st.write("")
             st.markdown(f"##### {T['moat_title']}")
             moat_html = f"""
             <div class="moat-container">
                <div class="moat-card {moat_data[0][2]}"><div class="moat-label">{moat_data[0][0]}</div><div class="moat-value">{moat_data[0][1]}</div></div>
                <div class="moat-card {moat_data[1][2]}"><div class="moat-label">{moat_data[1][0]}</div><div class="moat-value">{moat_data[1][1]}</div></div>
                <div class="moat-card {moat_data[2][2]}"><div class="moat-label">{moat_data[2][0]}</div><div class="moat-value">{moat_data[2][1]}</div></div>
                <div class="moat-card {moat_data[3][2]}"><div class="moat-label">{moat_data[3][0]}</div><div class="moat-value">{moat_data[3][1]}</div></div>
             </div>"""
             st.markdown(moat_html, unsafe_allow_html=True)

        st.divider()

        # IV. SAFETY
        st.markdown(f"### {T['safety_title']}")
        df_div_safety = pd.DataFrame()
        df_debt_safety = pd.DataFrame()
        
        h_cash_metric_chart = h_ocf if is_reit else h_fcf
        
        if h_divs_paid is not None and h_cash_metric_chart is not None:
            df_div_safety = align_annual_data({'Cash Flow': h_cash_metric_chart, 'Dividends Paid': h_divs_paid.abs()})
        if h_cash_metric_chart is not None and hist_debt is not None:
            df_debt_safety = align_annual_data({'Cash Flow': h_cash_metric_chart, 'Total Debt': hist_debt})

        if has_dividends:
            c_safe_1, c_safe_2 = st.columns(2)
            with c_safe_1:
                st.markdown(f"##### {T['div_safety']}")
                if not df_div_safety.empty: st.altair_chart(create_grouped_bar_chart(df_div_safety, {'Cash Flow': '#2F4F4F', 'Dividends Paid': '#228B22'}), use_container_width=True)
                else: st.warning("No Data")
            with c_safe_2:
                st.markdown(f"##### {T['solvency']}")
                if not df_debt_safety.empty: st.altair_chart(create_grouped_bar_chart(df_debt_safety, {'Cash Flow': '#2F4F4F', 'Total Debt': '#800000'}), use_container_width=True)
                else: st.warning("No Data")
        else:
            st.markdown(f"##### {T['solvency']}")
            if not df_debt_safety.empty: st.altair_chart(create_grouped_bar_chart(df_debt_safety, {'Cash Flow': '#2F4F4F', 'Total Debt': '#800000'}), use_container_width=True)
            else: st.warning("No Data")

        st.divider()

        # V. ANALYST
        st.markdown(f"### {T['analyst_title']}")
        target_price = safe_get(info, 'targetMeanPrice')
        recommendation = safe_get(info, 'recommendationKey', 'N/A').title()
        col_metrics, col_news = st.columns([1, 2])
        with col_metrics:
            st.markdown(f"##### {T['consensus']}")
            if target_price and target_price > 0:
                upside_pot = ((target_price - price_curr) / price_curr) * 100
                st.metric(T['target'], f"${round(target_price, 2)}", f"{round(upside_pot, 2)}%")
            else: st.metric(T['target'], "N/A")
            st.metric(T['consensus'], recommendation)

        with col_news:
            st.markdown(f"##### {T['news']}")
            if news_items:
                for n in news_items: st.markdown(f"<div class='news-item'><a href='{n['link']}' class='news-link' target='_blank'>• {n['title']}</a><span class='news-meta'>{n['date']}</span></div>", unsafe_allow_html=True)
            else:
                st.info("Live feed unavailable.")
                st.markdown(f"<a href='https://finance.yahoo.com/quote/{ticker}/news' target='_blank' class='fallback-btn'>Read Full News Coverage ➔</a>", unsafe_allow_html=True)

        # --- AUTO SUMMARY ---
        st.write(""); st.markdown(f"### {T['auto_summary']}")
        bull_points, bear_points = [], []
        if pe_ratio:
            if not is_reit:
                if pe_ratio < 15: bull_points.append(f"**Value Territory:** P/E Ratio of {round(pe_ratio, 1)} suggests the stock is inexpensive.")
                elif pe_ratio > 50: bear_points.append(f"**Expensive Valuation:** P/E Ratio of {round(pe_ratio, 1)} is very high.")
        if roic_val > 15: bull_points.append(f"**High Capital Efficiency:** ROIC of {round(roic_val, 1)}% indicates strong management.")
        if target_price and price_curr:
            upside = ((target_price - price_curr) / price_curr) * 100
            if upside > 15: bull_points.append(f"**Analyst Conviction:** Wall St. sees {round(upside, 1)}% upside potential.")
        d_limit = 6.0 if is_reit else 3.0
        if nd_ebitda_val < d_limit: bull_points.append(f"**Solid Balance Sheet:** Net Debt/EBITDA is safe at {round(nd_ebitda_val, 1)}x.")
        else: bear_points.append(f"**Leverage Risk:** Net Debt/EBITDA is elevated at {round(nd_ebitda_val, 1)}x.")
        if has_dividends:
            p_limit = 90 if is_reit else 75
            if final_payout_val < p_limit: bull_points.append(f"**Safe Dividend:** Cash Payout Ratio is {round(final_payout_val, 1)}% (Well covered).")
            else: bear_points.append(f"**Dividend Pressure:** Cash Payout Ratio is {round(final_payout_val, 1)}% (High).")
            c_limit = 8 if is_reit else 12
            if (div_yield_val + cagr_5) > c_limit: bull_points.append(f"**Chowder Check Passed:** Attractive Yield + Growth combo.")
        if net_val_insider > 0: bull_points.append("**Insider Confidence:** Management has been net buying recently.")
        
        sc1, sc2 = st.columns(2)
        with sc1:
            st.success(f"🟢 {T['bull']}")
            for p in bull_points: st.markdown(f"- {p}")
            if not bull_points: st.write("None.")
        with sc2:
            st.error(f"🔴 {T['bear']}")
            for p in bear_points: st.markdown(f"- {p}")
            if not bear_points: st.write("None.")

        # --- VI. COMPETITORS ---
        st.divider(); st.markdown(f"### {T['comp_title']}")
        col_comp_input, _ = st.columns([3, 1])
        with col_comp_input: peers_input = st.text_input(T['comp_input'], placeholder="Ex: KO, PEP, MNST")
        
        if peers_input:
            with st.spinner(f"{T['loading']}..."):
                tickers_to_compare = [t.strip().upper() for t in peers_input.split(",") if t.strip()]
                if ticker not in tickers_to_compare: tickers_to_compare.insert(0, ticker)
                comp_data = []
                for t in tickers_to_compare:
                    try:
                        p_stock = yf.Ticker(t)
                        p_info = p_stock.info
                        p_price = p_stock.fast_info.last_price
                        if not p_price: p_price = safe_get(p_info, 'currentPrice')
                        
                        comp_data.append({
                            "Ticker": t, "Price ($)": p_price, "P/E": safe_get(p_info, 'trailingPE'),
                            "Yield (%)": safe_get(p_info, 'dividendYield', 0)*100, "Payout (%)": safe_get(p_info, 'payoutRatio', 0)*100,
                            "ROE (%)": safe_get(p_info, 'returnOnEquity', 0)*100, "Net Mg (%)": safe_get(p_info, 'profitMargins', 0)*100,
                            "Debt/Eq": safe_get(p_info, 'debtToEquity', 0)
                        })
                    except: pass
                if comp_data:
                    df_comp = pd.DataFrame(comp_data).set_index("Ticker")
                    st.dataframe(df_comp.style.format("{:.2f}").highlight_max(subset=["Yield (%)", "ROE (%)", "Net Mg (%)"], color='#d4edda').highlight_min(subset=["P/E", "Debt/Eq", "Payout (%)"], color='#d4edda'), use_container_width=True)
                else: st.warning(T['no_data'])

        st.write(""); st.write(""); st.markdown("---")
        st.markdown(f"<div style='text-align: center; color: #888; font-size: 0.8rem;'>{T['footer']}</div>", unsafe_allow_html=True)