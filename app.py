import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import altair as alt
import requests
import xml.etree.ElementTree as ET
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Paulo Moura Dashboard", layout="wide", page_icon="📊")

# --- SESSION STATE INITIALIZATION ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'pt'
if 'search_term' not in st.session_state:
    st.session_state.search_term = ''

# --- TRANSLATIONS (PT / EN / FR) ---
LANG = {
    "pt": {
        "title": "Paulo Moura Dashboard",
        "search_label": "Pesquisar",
        "search_placeholder": "Ticker (Ex: O, AAPL...)",
        "btn_search": "🔍",
        "welcome_title": "👋 Bem-vindo!",
        "welcome_msg": "Introduza o símbolo de uma ação (ex: <b>AAPL</b>, <b>KO</b>, <b>O</b>) para ver a análise fundamentalista.",
        "try_ex": "Ou experimente:",
        "loading": "A analisar",
        "no_data": "Dados não encontrados ou erro de conexão.",
        "price": "Preço",
        "market_cap": "Valor de Mercado",
        "yield": "Dividend Yield",
        "profit_margin": "Margem Líquida",
        # Metrics
        "eps_trend": "Tendência EPS ($)",
        "affo_trend": "Tendência AFFO ($)",
        "cash_metric": "Fluxo de Caixa (Op/FCF)",
        "rev_hist": "Histórico de Receita",
        "gm_trend": "Margem Bruta (%)",
        "ni_hist": "Lucro Líquido",
        "shares": "Ações em Circulação",
        "debt": "Dívida Total",
        "safety_score": "Scorecard de Segurança",
        "net_debt": "Dívida Líq./EBITDA",
        "int_cov": "Cob. de Juros",
        "insider": "Transações Insiders",
        "solvency": "Solvência (Cash vs Dívida)",
        "div_hist": "Histórico Dividendos",
        "chowder": "Regra de Chowder",
        "rev_growth": "Cresc. Receita",
        "div_cagr": "Cresc. Div (5A)",
        "consensus": "Consenso Wall St.",
        "target": "Preço Alvo",
        "news": "Últimas Notícias",
        "auto_summary": "🤖 Análise Automática",
        "bull": "Pontos Fortes",
        "bear": "Pontos Fracos",
        "comp_title": "Comparação com Competidores",
        "comp_input": "Adicionar concorrentes (sep. por vírgula):",
        # Insights Contextuais
        "insight_premium": "💎 **Prémio de Qualidade detetado:** Os modelos clássicos (Graham/Lynch) indicam que a ação está cara, mas o **ROIC elevado (>15%)** sugere uma vantagem competitiva forte. O mercado paga frequentemente múltiplos mais altos por empresas de qualidade 'Premium' (Ex: Visa, Costco) do que os modelos conservadores sugerem.",
        "insight_growth": "🚀 **Expectativa de Crescimento:** O P/E Ratio é muito elevado. Isto significa que o preço atual reflete lucros futuros muito agressivos. Os modelos de valorização baseados no presente vão falhar aqui.",
        "insight_value": "📉 **Possível Subavaliação:** A ação parece barata nos modelos. Verifique se os lucros são estáveis. Se estiverem a cair, pode ser uma 'Armadilha de Valor'.",
        "insight_neutral": "⚖️ **Valorização Standard:** O preço parece alinhar-se razoavelmente com os fundamentos de crescimento e lucro atuais.",
        # Tooltips (Explicações)
        "help_net_debt": "Mede quantos anos a empresa demoraria a pagar a dívida com o lucro operacional (EBITDA). < 3x é ideal.",
        "help_int_cov": "Capacidade de pagar os juros da dívida. > 3x é seguro. < 1.5x é perigoso.",
        "help_insider": "Indica se os diretores (CEOs, CFOs) estão a comprar (confiança) ou a vender as suas próprias ações.",
        "help_altman": "Probabilidade de falência nos próximos 2 anos.\n> 3.0: Zona Segura (Verde)\n< 1.8: Zona de Risco (Vermelho)\n(Não aplicável a Bancos e REITs)",
        "help_solvency": "Compara o dinheiro em caixa vs a dívida total. Barras de dívida muito maiores que as de caixa indicam risco em caso de crise.",
        "help_tech": "Linha Verde (SMA50): Média curto prazo.\nLinha Vermelha (SMA200): Média longo prazo.\n\nSinais:\n- Preço > Ambas: Tendência de alta.\n- Verde cruza Vermelha para cima (Golden Cross): Sinal de Compra.\n- Verde cruza Vermelha para baixo (Death Cross): Sinal de Venda.",
        "help_models": "Estes modelos foram criados para encontrar pechinchas tradicionais. Eles tendem a subavaliar empresas de tecnologia ou com fossos económicos (Moats) enormes.",
        # Tabs & Labels
        "tab_perf": "📈 Performance",
        "tab_safe": "🛡️ Segurança",
        "tab_val": "💰 Valor & Dividendos",
        "tab_anal": "🧠 Análise & Notícias",
        "tab_comp": "🏢 Concorrentes",
        "fair_val_title": "⚖️ Estimativa de Preço Justo",
        "lynch": "Modelo Peter Lynch",
        "graham": "Fórmula Ben Graham",
        "yield_channel": "Canal de Yield (vs Média 5A)",
        "tech_chart": "Tendência Técnica (SMA 50/200)",
        "footer": "Dados Yahoo Finance | Uso Educacional | Calculos automáticos não constituem recomendação de compra."
    },
    "en": {
        "title": "Paulo Moura Dashboard",
        "search_label": "Search",
        "search_placeholder": "Ticker (e.g. O, AAPL...)",
        "btn_search": "🔍",
        "welcome_title": "👋 Welcome!",
        "welcome_msg": "Enter a stock ticker (e.g., <b>AAPL</b>, <b>KO</b>, <b>O</b>) to see fundamental analysis.",
        "try_ex": "Or try:",
        "loading": "Analyzing",
        "no_data": "Data not found or connection error.",
        "price": "Price",
        "market_cap": "Market Cap",
        "yield": "Dividend Yield",
        "profit_margin": "Net Margin",
        "eps_trend": "EPS Trend ($)",
        "affo_trend": "AFFO Trend ($)",
        "cash_metric": "Cash Flow (Op/FCF)",
        "rev_hist": "Revenue History",
        "gm_trend": "Gross Margin (%)",
        "ni_hist": "Net Income",
        "shares": "Shares Outstanding",
        "debt": "Total Debt",
        "safety_score": "Safety Scorecard",
        "net_debt": "Net Debt/EBITDA",
        "int_cov": "Interest Cov.",
        "insider": "Insider Trading",
        "solvency": "Solvency (Cash vs Debt)",
        "div_hist": "Dividend History",
        "chowder": "Chowder Rule",
        "rev_growth": "Rev Growth",
        "div_cagr": "Div Growth (5Y)",
        "consensus": "Wall St. Consensus",
        "target": "Price Target",
        "news": "Latest Headlines",
        "auto_summary": "🤖 Automated Analysis",
        "bull": "Bull Case",
        "bear": "Bear Case",
        "comp_title": "Competitor Comparison",
        "comp_input": "Add competitors (comma sep):",
        # Insights
        "insight_premium": "💎 **Quality Premium Detected:** Classic models (Graham/Lynch) imply the stock is expensive, but high **ROIC (>15%)** suggests a strong competitive advantage. The market often pays a premium multiple for high-quality 'Compounders' (e.g., Visa, Costco).",
        "insight_growth": "🚀 **High Growth Expectations:** The P/E Ratio is very high. This means the current price reflects aggressive future earnings. Valuation models based on present earnings will fail here.",
        "insight_value": "📉 **Potential Undervaluation:** The stock looks cheap on models. Check if earnings are stable. If declining, it could be a 'Value Trap'.",
        "insight_neutral": "⚖️ **Standard Valuation:** The price seems reasonably aligned with current growth and earnings fundamentals.",
        # Tooltips
        "help_net_debt": "Measures how many years it would take to pay off debt with current EBITDA. < 3x is ideal.",
        "help_int_cov": "Ability to pay interest expenses. > 3x is safe. < 1.5x is critical.",
        "help_insider": "Shows if company directors are buying (confidence) or selling their own shares.",
        "help_altman": "Bankruptcy probability within 2 years.\n> 3.0: Safe Zone (Green)\n< 1.8: Distress Zone (Red)\n(Not applicable to Banks/REITs)",
        "help_solvency": "Compares Cash on hand vs Total Debt. Debt bars much larger than cash bars indicate liquidity risk.",
        "help_tech": "Green Line (SMA50): Short-term avg.\nRed Line (SMA200): Long-term avg.\n\nSignals:\n- Price > Both: Bullish trend.\n- Green crosses Red upward (Golden Cross): Buy Signal.\n- Green crosses Red downward (Death Cross): Sell Signal.",
        "help_models": "These models were built to find traditional bargains. They tend to undervalue tech companies or those with massive economic Moats.",
        # Tabs
        "tab_perf": "📈 Performance",
        "tab_safe": "🛡️ Safety",
        "tab_val": "💰 Value & Dividends",
        "tab_anal": "🧠 Analysis & News",
        "tab_comp": "🏢 Competitors",
        "fair_val_title": "⚖️ Fair Value Estimate",
        "lynch": "Peter Lynch Model",
        "graham": "Ben Graham Formula",
        "yield_channel": "Yield Channel (vs 5Y Avg)",
        "tech_chart": "Technical Trend (SMA 50/200)",
        "footer": "Data by Yahoo Finance | Educational Use | Automated calculations are not buy recommendations."
    },
    "fr": {
        "title": "Tableau de Bord Paulo Moura",
        "search_label": "Recherche",
        "search_placeholder": "Ticker (ex: O, AAPL...)",
        "btn_search": "🔍",
        "welcome_title": "👋 Bienvenue!",
        "welcome_msg": "Entrez un ticker (ex: <b>AAPL</b>, <b>LVMH</b>, <b>O</b>) pour voir l'analyse fondamentale.",
        "try_ex": "Ou essayez:",
        "loading": "Analyse en cours",
        "no_data": "Données introuvables.",
        "price": "Prix",
        "market_cap": "Cap. Boursière",
        "yield": "Rendement",
        "profit_margin": "Marge Nette",
        "eps_trend": "Tendance BPA ($)",
        "affo_trend": "Tendance AFFO ($)",
        "cash_metric": "Flux de Trésorerie",
        "rev_hist": "Historique Revenus",
        "gm_trend": "Marge Brute (%)",
        "ni_hist": "Résultat Net",
        "shares": "Actions en Circulation",
        "debt": "Dette Totale",
        "safety_score": "Score de Sécurité",
        "net_debt": "Dette Nette/EBITDA",
        "int_cov": "Couv. Intérêts",
        "insider": "Trans. Initiés",
        "solvency": "Solvabilité",
        "div_hist": "Hist. Dividendes",
        "chowder": "Règle de Chowder",
        "rev_growth": "Croiss. Revenus",
        "div_cagr": "Croiss. Div (5A)",
        "consensus": "Consensus",
        "target": "Objectif de Cours",
        "news": "Actualités",
        "auto_summary": "🤖 Analyse Automatique",
        "bull": "Points Forts",
        "bear": "Points Faibles",
        "comp_title": "Comparaison",
        "comp_input": "Comparer avec (séparé par virgule):",
        # Insights
        "insight_premium": "💎 **Prime de Qualité:** Les modèles classiques indiquent que l'action est chère, mais un **ROIC élevé (>15%)** suggère un avantage concurrentiel. Le marché paie souvent plus cher pour la qualité 'Premium' (ex: Visa) que ne le suggèrent les modèles.",
        "insight_growth": "🚀 **Attentes de Croissance:** Le P/E est très élevé. Le prix actuel reflète des bénéfices futurs agressifs.",
        "insight_value": "📉 **Sous-évaluation Possible:** L'action semble bon marché. Vérifiez si les bénéfices sont stables. S'ils baissent, attention au 'Piège de Valeur'.",
        "insight_neutral": "⚖️ **Valorisation Standard:** Le prix semble aligné avec les fondamentaux actuels.",
        # Tooltips
        "help_net_debt": "Mesure le nombre d'années pour rembourser la dette avec l'EBITDA actuel. < 3x est idéal.",
        "help_int_cov": "Capacité à payer les intérêts. > 3x est sûr. < 1.5x est critique.",
        "help_insider": "Indique si les dirigeants achètent (confiance) ou vendent leurs propres actions.",
        "help_altman": "Probabilité de faillite.\n> 3.0: Zone Sûre (Vert)\n< 1.8: Zone de Risque (Rouge)\n(Non applicable aux Banques/REITs)",
        "help_solvency": "Compare la Trésorerie vs Dette Totale. Une dette bien plus élevée que le cash indique un risque.",
        "help_tech": "Ligne Verte (SMA50): Moyenne court terme.\nLigne Rouge (SMA200): Moyenne long terme.\n\nSignaux:\n- Prix > Les deux: Tendance haussière.\n- Croix d'Or (Golden Cross): Achat.\n- Croix de la Mort (Death Cross): Vente.",
        "help_models": "Ces modèles sont conçus pour trouver des bonnes affaires traditionnelles. Ils sous-évaluent souvent la tech ou les entreprises de qualité.",
        # Tabs
        "tab_perf": "📈 Performance",
        "tab_safe": "🛡️ Sécurité",
        "tab_val": "💰 Valeur & Dividendes",
        "tab_anal": "🧠 Analyse & Actu",
        "tab_comp": "🏢 Concurrents",
        "fair_val_title": "⚖️ Estimation Juste Valeur",
        "lynch": "Modèle Peter Lynch",
        "graham": "Formule Ben Graham",
        "yield_channel": "Canal de Rendement (vs Moy 5A)",
        "tech_chart": "Tendance Technique (SMA 50/200)",
        "footer": "Données Yahoo Finance | Usage Éducatif"
    }
}

# Definir idioma atual
T = LANG[st.session_state.lang]

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Clean Look */
    .stApp { background-color: #ffffff; }
    h1, h2, h3, h4, h5 { font-family: 'Arial', sans-serif; color: #333; }
    
    /* Metrics */
    div[data-testid="stMetricValue"] { font-size: 1.4rem !important; color: #333; }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem !important; color: #666; }
    
    /* Buttons */
    div.stButton > button {
        background-color: #f0f2f6;
        color: #333;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    
    /* Welcome Container */
    .welcome-container { 
        text-align: center; 
        margin-top: 50px; 
        color: #555;
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 10px;
        border: 1px solid #eee;
    }
    
    /* Moat Cards */
    .moat-container { display: flex; gap: 10px; margin-bottom: 5px; flex-wrap: wrap; }
    .moat-card { flex: 1; min-width: 130px; background-color: #fff; padding: 12px; border-radius: 8px; text-align: center; border: 1px solid #e0e0e0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .moat-label { font-size: 0.7rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .moat-value { font-size: 1.0rem; font-weight: 700; color: #333; }
    .moat-good { border-bottom: 3px solid #28a745; }
    .moat-avg { border-bottom: 3px solid #ffc107; }
    .moat-bad { border-bottom: 3px solid #dc3545; }
    
    /* News */
    a.news-link { text-decoration: none; color: #1f77b4; font-weight: 600; font-size: 0.90rem; display: block; margin-bottom: 2px;}
    .news-meta { color: #888; font-size: 0.75rem; border-bottom: 1px solid #eee; padding-bottom: 8px; display: block; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
c_head, c_lang = st.columns([8, 2])
with c_head:
    st.markdown(f"### 📊 {T['title']}")
with c_lang:
    c1, c2, c3 = st.columns(3)
    def set_lang(l): st.session_state.lang = l
    if c1.button("🇵🇹"): set_lang('pt'); st.rerun()
    if c2.button("🇺🇸"): set_lang('en'); st.rerun()
    if c3.button("🇫🇷"): set_lang('fr'); st.rerun()

st.markdown("---")

# --- SEARCH ---
c_search, c_btn = st.columns([5, 1])
with c_search:
    query = st.text_input(T['search_label'], value=st.session_state.search_term, placeholder=T['search_placeholder'], label_visibility="collapsed").strip()
with c_btn:
    if st.button(T['btn_search'], use_container_width=True): st.session_state.search_term = query

if query != st.session_state.search_term: st.session_state.search_term = query

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
            if any(t in idx for t in terms): return df.loc[idx].sort_index()
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
        limit_good = 90 if is_reit else 75; limit_bad = 100 if is_reit else 90
        if value < limit_good: return "Safe", "normal"
        elif value > limit_bad: return "High", "inverse"
        else: return "OK", "off"
    elif metric_type == 'net_debt_ebitda':
        limit_good = 6.0 if is_reit else 3.0; limit_bad = 7.5 if is_reit else 4.5
        if value < limit_good: return "Safe", "normal"
        elif value > limit_bad: return "High Debt", "inverse"
        else: return "Elevated", "off"
    elif metric_type == 'int_cov':
        if value > 3.0: return "Safe", "normal"
        elif value < 1.5: return "Critical", "inverse"
        else: return "Tight", "off"
    elif metric_type == 'roe' or metric_type == 'roic' or metric_type == 'profit_margin':
        limit_good = 12 if metric_type == 'roe' else 8
        if metric_type == 'profit_margin': limit_good = 10
        if value > limit_good: return "Good", "normal"
        elif value < 5: return "Low", "inverse"
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
        if 'quotes' in data and len(data['quotes']) > 0: return data['quotes'][0]['symbol']
    except: pass
    return query.upper()

def get_google_news(ticker):
    try:
        l = st.session_state.lang
        url = f"https://news.google.com/rss/search?q={ticker}+stock+finance&hl={l}&gl=US&ceid=US:{l}"
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
                    fi = stock.fast_info
                    fast_info_dict = {'last_price': fi.last_price, 'market_cap': fi.market_cap}
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

def create_altair_chart(data, bar_color):
    try:
        if data is None or data.empty: return None
        df_chart = pd.DataFrame()
        years = data.index.strftime('%Y') if hasattr(data.index, 'strftime') else data.index.astype(str)
        if isinstance(data, pd.Series): df_chart = pd.DataFrame({'Year': years, 'Value': data.values})
        elif isinstance(data, pd.DataFrame): 
            df_chart = data.copy(); df_chart['Year'] = years
            if 'Value' not in df_chart.columns: df_chart['Value'] = df_chart.iloc[:, 0]
        df_chart = df_chart.dropna().sort_values('Year').tail(10)
        if df_chart.empty: return None
        return alt.Chart(df_chart).mark_bar(width=30, color=bar_color).encode(
            x=alt.X('Year', axis=alt.Axis(title='', labelAngle=0)),
            y=alt.Y('Value', axis=alt.Axis(title='', format='$.2s', grid=True)),
            tooltip=['Year', alt.Tooltip('Value', format='$.2s')]
        ).properties(height=220)
    except: return None

def create_line_chart(data, color, is_percent=False):
    try:
        if data is None or data.empty: return None
        df_chart = pd.DataFrame()
        years = data.index.strftime('%Y') if hasattr(data.index, 'strftime') else data.index.astype(str)
        if isinstance(data, pd.Series): df_chart = pd.DataFrame({'Year': years, 'Value': data.values})
        elif isinstance(data, pd.DataFrame): 
            df_chart = data.copy(); df_chart['Year'] = years
            if 'Value' not in df_chart.columns: df_chart['Value'] = df_chart.iloc[:, 0]
        df_chart = df_chart.dropna().sort_values('Year').tail(10)
        if df_chart.empty: return None

        # Escala Y Personalizada (0-100% se for margem)
        y_scale = alt.Axis(title='', format='$.2f', grid=True)
        y_domain = alt.Undefined
        if is_percent:
            y_scale = alt.Axis(title='', format='.1f', grid=True)
            max_val = df_chart['Value'].max()
            y_domain = [0, 100] if max_val <= 100 else [0, max_val + 10]

        line = alt.Chart(df_chart).mark_line(color=color, strokeWidth=3).encode(
            x=alt.X('Year', axis=alt.Axis(title='', labelAngle=0)),
            y=alt.Y('Value', axis=y_scale, scale=alt.Scale(domain=y_domain))
        )
        points = alt.Chart(df_chart).mark_circle(size=80, color=color).encode(
            x='Year', y='Value', tooltip=['Year', alt.Tooltip('Value', format='.1f' if is_percent else '$.2f')]
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
        range_colors = ['#4682B4', '#FFA07A']
        if colors: range_colors = [colors.get(m, '#888') for m in df_long['Metric'].unique()]
        return alt.Chart(df_long).mark_bar(strokeWidth=0).encode(
            x=alt.X('Year:O', axis=alt.Axis(title='', labelAngle=0)),
            y=alt.Y('Value:Q', axis=alt.Axis(title='', format='$.2s')),
            color=alt.Color('Metric:N', scale=alt.Scale(domain=df_long['Metric'].unique(), range=range_colors), legend=alt.Legend(title="", orient="bottom")),
            xOffset='Metric:N', tooltip=['Year', 'Metric', alt.Tooltip('Value', format='$.2s')]
        ).properties(height=280)
    except: return None

def create_price_chart(df):
    try:
        if df is None or df.empty: return None
        df = df.copy()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        df_chart = df.reset_index().tail(500) 
        
        # Transformar para formato longo para permitir legendas automáticas
        df_long = df_chart.melt('Date', value_vars=['Close', 'SMA50', 'SMA200'], var_name='Metric', value_name='Price')
        
        # Mapeamento de cores
        domain = ['Close', 'SMA50', 'SMA200']
        range_ = ['#333333', '#2ca02c', '#d62728'] # Preto, Verde, Vermelho

        chart = alt.Chart(df_long).mark_line().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-45)),
            y=alt.Y('Price', axis=alt.Axis(title='Preço ($)')),
            color=alt.Color('Metric', scale=alt.Scale(domain=domain, range=range_), legend=alt.Legend(title="Indicadores")),
            strokeDash=alt.condition(
                alt.datum.Metric == 'Close',
                alt.value([0]),     # Linha sólida para o preço
                alt.value([5, 5])   # Tracejada para SMAs
            ),
            tooltip=['Date', 'Metric', alt.Tooltip('Price', format='$.2f')]
        ).properties(height=350, title="Análise Técnica (Preço vs Médias)")
        return chart
    except: return None

def calculate_altman_z(balance, financials, info):
    try:
        total_assets = find_line(balance, ['total assets'])
        total_liab = find_line(balance, ['total liabilities', 'total debt'])
        current_assets = find_line(balance, ['current assets', 'total current assets'])
        current_liab = find_line(balance, ['current liabilities', 'total current liabilities'])
        retained_earnings = find_line(balance, ['retained earnings', 'accumulated deficit'])
        ebit = find_line(financials, ['ebit', 'operating income'])
        revenue = find_line(financials, ['total revenue', 'operating revenue'])
        
        if any(x is None for x in [total_assets, total_liab, current_assets, current_liab, retained_earnings, ebit, revenue]):
            return None

        ta = total_assets.iloc[0]; tl = total_liab.iloc[0] if total_liab is not None else 0
        ca = current_assets.iloc[0]; cl = current_liab.iloc[0]
        re = retained_earnings.iloc[0]; ebit_val = ebit.iloc[0]; rev_val = revenue.iloc[0]
        mkt_cap = safe_get(info, 'marketCap', 0)

        if ta == 0 or tl == 0: return None

        A = (ca - cl) / ta
        B = re / ta
        C = ebit_val / ta
        D = mkt_cap / tl
        E = rev_val / ta

        z_score = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
        return z_score
    except: return None

def calculate_fair_value(eps, growth_rate, pe_ratio):
    try:
        lynch_value = 0
        if growth_rate > 0 and eps > 0:
            lynch_value = eps * (growth_rate if growth_rate < 25 else 25) 
        graham_value = 0
        if eps > 0 and growth_rate > 0:
             graham_value = eps * (7 + 1.5 * growth_rate)
        return lynch_value, graham_value
    except: return 0, 0

# --- LANDING PAGE ---
if not st.session_state.search_term:
    st.markdown(f"<div class='welcome-container'><h3>{T['welcome_title']}</h3><p>{T['welcome_msg']}</p></div>", unsafe_allow_html=True)
    st.write("")
    st.markdown(f"<p style='text-align:center; color:#666;'>{T['try_ex']}</p>", unsafe_allow_html=True)
    _, c1, c2, c3, _ = st.columns([4, 2, 2, 2, 4])
    def set_search(t): st.session_state.search_term = t; st.rerun()
    if c1.button("🍎 AAPL"): set_search("AAPL")
    if c2.button("🏘 O"): set_search("O")
    if c3.button("🥤 KO"): set_search("KO")

# --- MAIN LOGIC ---
if st.session_state.search_term:
    ticker = st.session_state.search_term.upper()
    if " " in ticker or len(ticker) > 5:
        with st.spinner(f"{T['loading']}..."):
            found_ticker = search_symbol(ticker)
            if found_ticker: ticker = found_ticker

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

        with st.spinner('Calculating...'):
            # Price & Cap
            price_curr = fast_info.get('last_price')
            if not price_curr: price_curr = safe_get(info, 'currentPrice')
            if not price_curr and not hist_price.empty: price_curr = hist_price['Close'].iloc[-1]
            if price_curr is None: price_curr = 0.0
            mkt_cap = fast_info.get('market_cap')
            if not mkt_cap: mkt_cap = safe_get(info, 'marketCap')

            # Basic Lines
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
            
            # Type Detection
            is_reit = False
            sector = str(info.get('sector', '')).lower()
            industry = str(info.get('industry', '')).lower()
            if 'reit' in sector or 'reit' in industry or 'real estate' in sector: is_reit = True
            
            has_dividends = False
            div_yield_check = safe_get(info, 'dividendRate')
            if (div_yield_check and div_yield_check > 0) or (not divs.empty and divs.sum() > 0): has_dividends = True

            # Cash Flow Logic
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

            # More Lines
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
            if h_ebitda is None and h_net_income is not None and h_depr is not None: h_ebitda = h_net_income + h_depr 
            
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

            # --- INSIDER ---
            insider_label = "Neutral"; insider_val_str = "N/A"; insider_delta_display = "No Data"; net_val_insider = 0
            try:
                if insider_tx is not None and not insider_tx.empty:
                    recent = insider_tx.head(20) 
                    buy_count, sell_count = 0, 0
                    if 'Value' in recent.columns and 'Shares' in recent.columns:
                        for index, row in recent.iterrows():
                            val = row['Value']; is_buy = False
                            if pd.isna(val): val = 0
                            if row['Shares'] > 0: is_buy = True
                            if 'Text' in recent.columns and 'sale' in str(row['Text']).lower(): is_buy = False
                            elif 'Text' in recent.columns and 'purchase' in str(row['Text']).lower(): is_buy = True
                            
                            if is_buy: net_val_insider += val; buy_count += 1
                            else: net_val_insider -= val; sell_count += 1
                        
                    if net_val_insider > 0: insider_label = "Net Buying"; insider_val_str = format_large_number(net_val_insider)
                    elif net_val_insider < 0: insider_label = "Net Selling"; insider_val_str = format_large_number(net_val_insider).replace("-", "") 
                    insider_delta_display = f"{buy_count} Buys / {sell_count} Sells"
            except: pass

            # --- ALTMAN Z ---
            z_score_val = calculate_altman_z(balance, financials, info)
            z_score_txt = "N/A"; z_color = "off"
            if z_score_val is not None and not is_reit and 'financial' not in sector:
                z_score_txt = f"{round(z_score_val, 2)}"
                if z_score_val > 3.0: z_color = "normal" 
                elif z_score_val < 1.8: z_color = "inverse"
            elif is_reit or 'financial' in sector:
                z_score_txt = "N/A (Setor)"

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
            avg_yield_5y = 0
            if has_dividends and not hist_price.empty and not divs.empty:
                avg_price_yr = hist_price['Close'].resample('YE').mean()
                sum_div_yr = divs.resample('YE').sum()
                df_yield_calc = pd.DataFrame({'Price': avg_price_yr, 'Divs': sum_div_yr}).dropna()
                df_yield_calc = df_yield_calc[df_yield_calc['Price'] > 0]
                if not df_yield_calc.empty: 
                    series_yield_history = (df_yield_calc['Divs'] / df_yield_calc['Price']) * 100
                    if len(series_yield_history) >= 5: avg_yield_5y = series_yield_history.tail(5).mean()
                    else: avg_yield_5y = series_yield_history.mean()

            news_items = get_google_news(ticker)

            # --- MOAT CALCULATION (ADVANCED) ---
            avg_roic = 0; avg_gm = 0; roic_trend = "Stable"
            if h_ebit is not None and h_equity is not None and hist_debt is not None:
                try:
                    df_roic = align_annual_data({'EBIT': h_ebit, 'Equity': h_equity, 'Debt': hist_debt, 'Cash': h_cash})
                    if not df_roic.empty:
                        df_roic['InvCap'] = df_roic['Equity'] + df_roic['Debt'] - df_roic['Cash'].fillna(0)
                        df_roic = df_roic[df_roic['InvCap'] > 0]
                        df_roic['ROIC'] = (df_roic['EBIT'] / df_roic['InvCap']) * 100
                        recent_roic = df_roic['ROIC'].tail(5)
                        avg_roic = recent_roic.mean()
                        if len(recent_roic) > 2:
                            if recent_roic.iloc[-1] > recent_roic.mean() * 1.1: roic_trend = "Rising ↗"
                            elif recent_roic.iloc[-1] < recent_roic.mean() * 0.9: roic_trend = "Falling ↘"
                except: pass
            if series_gross_margin is not None and not series_gross_margin.empty:
                avg_gm = series_gross_margin.tail(5).mean()
            
            buffett_score_txt = "N/A"; buffett_class = "moat-avg"
            try:
                h_sga = find_line(financials, ['selling general and administrative', 'selling, general'])
                if h_sga is not None and h_gross_profit is not None:
                    last_sga = h_sga.iloc[0]; last_gp = h_gross_profit.iloc[0]
                    if last_gp > 0:
                        sga_ratio = (last_sga / last_gp) * 100
                        if sga_ratio < 30: buffett_score_txt = f"Great ({round(sga_ratio)}%)"; buffett_class = "moat-good"
                        elif sga_ratio < 70: buffett_score_txt = f"Good ({round(sga_ratio)}%)"; buffett_class = "moat-avg"
                        else: buffett_score_txt = f"High ({round(sga_ratio)}%)"; buffett_class = "moat-bad"
            except: pass

            moat_data = []
            if is_reit:
                if avg_gm > 60: moat_data.append(("GM (5Y)", f"{round(avg_gm,1)}%", "moat-good"))
                elif avg_gm > 40: moat_data.append(("GM (5Y)", f"{round(avg_gm,1)}%", "moat-avg"))
                else: moat_data.append(("GM (5Y)", f"{round(avg_gm,1)}%", "moat-bad"))
            else:
                c_roic = "moat-bad"
                if avg_roic > 15: c_roic = "moat-good"
                elif avg_roic > 9: c_roic = "moat-avg"
                moat_data.append(("ROIC (5Y)", f"{round(avg_roic, 1)}%", c_roic))

            moat_data.append(("Op. Eff (SG&A)", buffett_score_txt, buffett_class))
            
            if nd_ebitda_val < 2.5 and nd_ebitda_val > 0: moat_data.append(("Leverage", "Low Debt", "moat-good"))
            elif nd_ebitda_val < 4.5: moat_data.append(("Leverage", "Moderate", "moat-avg"))
            else: moat_data.append(("Leverage", "High Debt", "moat-bad"))

            if mkt_cap > 100000000000: moat_data.append(("Scale", "Dominant", "moat-good"))
            elif mkt_cap > 20000000000: moat_data.append(("Scale", "Large", "moat-avg"))
            else: moat_data.append(("Scale", "Small", "moat-bad"))

            # --- DISPLAY START ---
            st.header(f"{info.get('longName', ticker)}")
            st.caption(f"Symbol: {ticker} | Sector: {info.get('sector', 'N/A')} | Industry: {info.get('industry', 'N/A')}")
            with st.expander("Business Description", expanded=False): st.write(info.get('longBusinessSummary', 'N/A'))
            st.divider()

            # TOP METRICS
            m1, m2, m3 = st.columns(3)
            m1.metric(T['price'], f"${round(price_curr, 2)}")
            
            div_yield_val = 0.0; final_payout_val = 0.0
            if has_dividends:
                div_rate_val = safe_get(info, 'dividendRate')
                if price_curr > 0: div_yield_val = (div_rate_val / price_curr * 100)
                final_payout_label = "Payout (FCF)"
                if fcf_payout_ratio is not None and 0 < fcf_payout_ratio < 500:
                    final_payout_val = fcf_payout_ratio
                    if is_reit: final_payout_label = "Payout (FFO)"
                else:
                    if not is_reit:
                        final_payout_val = safe_get(info, 'payoutRatio') * 100
                        final_payout_label = "Payout (GAAP)"
                    else: final_payout_val = 0; final_payout_label = "Payout (N/A)"
                p_txt, p_col = get_metric_status(final_payout_val, is_reit, 'payout')
                m2.metric(T['yield'], f"{round(div_yield_val, 2)}%")
                m3.metric(final_payout_label, f"{round(final_payout_val, 1)}%", p_txt, delta_color=p_col)
            else:
                m2.metric(T['market_cap'], format_large_number(mkt_cap))
                pm_val = safe_get(info, 'profitMargins') * 100
                pm_txt, pm_col = get_metric_status(pm_val, is_reit, 'profit_margin')
                m3.metric(T['profit_margin'], f"{round(pm_val, 2)}%", pm_txt, delta_color=pm_col)

            # MOAT SECTION (TOP)
            st.write("")
            st.markdown(f"##### 🏰 Moat Analysis (Competitive Advantage)")
            moat_html = f"""<div class="moat-container">
                <div class="moat-card {moat_data[0][2]}"><div class="moat-label">{moat_data[0][0]}</div><div class="moat-value">{moat_data[0][1]}</div><div style='font-size:0.7rem; color:#888'>{roic_trend if not is_reit else ''}</div></div>
                <div class="moat-card {moat_data[1][2]}"><div class="moat-label">{moat_data[1][0]}</div><div class="moat-value">{moat_data[1][1]}</div></div>
                <div class="moat-card {moat_data[2][2]}"><div class="moat-label">{moat_data[2][0]}</div><div class="moat-value">{moat_data[2][1]}</div></div>
                <div class="moat-card {moat_data[3][2]}"><div class="moat-label">{moat_data[3][0]}</div><div class="moat-value">{moat_data[3][1]}</div></div>
             </div>"""
            st.markdown(moat_html, unsafe_allow_html=True)
            
            good_count = sum(1 for x in moat_data if x[2] == 'moat-good')
            avg_count = sum(1 for x in moat_data if x[2] == 'moat-avg')
            total_score = (good_count * 2) + (avg_count * 1) 
            moat_verdict = "No Moat 🛡️"; moat_color = "#dc3545"; moat_width = 20
            if total_score >= 6: moat_verdict = "Wide Moat 🏰"; moat_color = "#28a745"; moat_width = 100
            elif total_score >= 3: moat_verdict = "Narrow Moat 🏠"; moat_color = "#ffc107"; moat_width = 60
            st.markdown(f"""<div style="margin-top: 5px; background-color: #f1f1f1; border-radius: 5px; height: 18px; width: 100%;"><div style="background-color: {moat_color}; width: {moat_width}%; height: 100%; border-radius: 5px; text-align: center; color: white; font-weight: bold; font-size: 0.75rem; line-height: 18px;">{moat_verdict}</div></div>""", unsafe_allow_html=True)
            
            st.write("")
            
            # --- TABS LAYOUT ---
            tab1, tab2, tab3, tab4, tab5 = st.tabs([T['tab_perf'], T['tab_safe'], T['tab_val'], T['tab_anal'], T['tab_comp']])

            # TAB 1: PERFORMANCE
            with tab1:
                c1, c2, c3 = st.columns(3)
                with c1: 
                    if is_reit:
                        st.markdown(f"##### {T['affo_trend']}")
                        if series_affo_share is not None: st.altair_chart(create_altair_chart(series_affo_share, "#003366"), use_container_width=True)
                    else:
                        st.markdown(f"##### {T['eps_trend']}")
                        if hist_eps is not None: st.altair_chart(create_altair_chart(hist_eps, "#003366"), use_container_width=True)
                with c2: 
                    st.markdown(f"##### {T['cash_metric']}")
                    if series_affo_share is not None: st.altair_chart(create_altair_chart(series_affo_share, "#4169E1"), use_container_width=True)
                with c3: 
                    st.markdown(f"##### {T['rev_hist']}")
                    if h_revenue is not None: st.altair_chart(create_altair_chart(h_revenue, "#B8860B"), use_container_width=True)
                
                st.divider()
                r2_c1, r2_c2 = st.columns(2)
                with r2_c1:
                     st.markdown(f"##### {T['gm_trend']}")
                     if series_gross_margin is not None: st.altair_chart(create_line_chart(series_gross_margin, "#DAA520", is_percent=True), use_container_width=True)
                with r2_c2:
                     st.markdown(f"##### {T['ni_hist']}")
                     if h_net_income is not None: st.altair_chart(create_altair_chart(h_net_income, "#228B22"), use_container_width=True)

            # TAB 2: SAFETY
            with tab2:
                h1, h2, h3 = st.columns(3)
                with h1: 
                    st.markdown(f"##### {T['shares']}")
                    if h_shares is not None: st.altair_chart(create_altair_chart(h_shares, "#CC5500"), use_container_width=True)
                with h2: 
                    st.markdown(f"##### {T['debt']}")
                    if hist_debt is not None: st.altair_chart(create_altair_chart(hist_debt, "#800020"), use_container_width=True)
                with h3:
                    st.markdown(f"##### {T['safety_score']}")
                    col_s1, col_s2 = st.columns(2)
                    debt_txt, debt_col = get_metric_status(nd_ebitda_val, is_reit, 'net_debt_ebitda')
                    int_txt, int_col = get_metric_status(int_cov_val, is_reit, 'int_cov')
                    
                    with col_s1:
                        st.metric(
                            T['net_debt'], 
                            f"{round(nd_ebitda_val, 1)}x", 
                            debt_txt, 
                            delta_color=debt_col,
                            help=T['help_net_debt']
                        )
                        st.metric(
                            T['int_cov'], 
                            f"{round(int_cov_val, 1)}x", 
                            int_txt, 
                            delta_color=int_col,
                            help=T['help_int_cov']
                        )
                    with col_s2:
                        ins_col = "normal" if insider_label == "Net Buying" else "inverse" if insider_label == "Net Selling" else "off"
                        st.metric(
                            T['insider'], 
                            insider_label, 
                            insider_delta_display, 
                            delta_color=ins_col,
                            help=T['help_insider']
                        )
                        z_delta_color = "off"
                        if z_color == "normal": z_delta_color = "normal"
                        elif z_color == "inverse": z_delta_color = "inverse"
                        st.metric(
                            "Altman Z-Score", 
                            z_score_txt, 
                            delta_color=z_delta_color,
                            help=T['help_altman']
                        )
                
                st.divider()
                st.markdown(f"##### {T['solvency']} ℹ️", help=T['help_solvency'])
                df_debt_safety = pd.DataFrame()
                h_cash_metric_chart = h_ocf if is_reit else h_fcf
                if h_cash_metric_chart is not None and hist_debt is not None: df_debt_safety = align_annual_data({'Cash Flow': h_cash_metric_chart, 'Total Debt': hist_debt})
                if not df_debt_safety.empty: st.altair_chart(create_grouped_bar_chart(df_debt_safety, {'Cash Flow': '#2F4F4F', 'Total Debt': '#800000'}), use_container_width=True)

            # TAB 3: VALUATION & DIVIDENDS
            with tab3:
                # Fair Value
                st.markdown(f"##### {T['fair_val_title']} ℹ️", help=T['help_models'])
                eps_ttm = safe_get(info, 'trailingEps')
                growth_est = safe_get(info, 'earningsGrowth', 0.05) * 100 
                if growth_est < 0: growth_est = 5 
                lynch_v, graham_v = calculate_fair_value(eps_ttm, growth_est, safe_get(info, 'trailingPE'))
                
                # --- CONTEXTO DE VALORIZAÇÃO (NOVO) ---
                fair_val_diff = ((graham_v - price_curr) / price_curr) * 100 if graham_v > 0 else 0
                val_insight = T['insight_neutral'] # Default
                
                # Lógica de Insights
                if pe_ratio and pe_ratio > 25 and roic_val > 15:
                    val_insight = T['insight_premium']
                    st.info(val_insight)
                elif pe_ratio and pe_ratio > 50:
                    val_insight = T['insight_growth']
                    st.warning(val_insight)
                elif pe_ratio and pe_ratio < 10 and roic_val < 5:
                    val_insight = T['insight_value']
                    st.warning(val_insight)
                # -------------------------------------

                fv_c1, fv_c2, fv_c3 = st.columns(3)
                with fv_c1:
                    delta_l = round(((lynch_v - price_curr)/price_curr)*100, 1) if lynch_v > 0 else 0
                    st.metric(T['lynch'], f"${round(lynch_v, 2)}", f"{delta_l}%")
                with fv_c2:
                    delta_g = round(((graham_v - price_curr)/price_curr)*100, 1) if graham_v > 0 else 0
                    st.metric(T['graham'], f"${round(graham_v, 2)}", f"{delta_g}%")
                with fv_c3:
                    chowder_val = div_yield_val + cagr_5
                    chow_txt, chow_col = get_metric_status(chowder_val, is_reit, 'chowder')
                    st.metric(T['chowder'], f"{round(chowder_val, 1)}", chow_txt, delta_color=chow_col)
                
                st.divider()

                # Dividends & Yield Channel
                if has_dividends:
                    d_c1, d_c2 = st.columns(2)
                    with d_c1:
                        st.markdown(f"##### {T['div_hist']}")
                        if series_divs_history is not None: st.altair_chart(create_line_chart(series_divs_history, "#228B22"), use_container_width=True)
                    with d_c2:
                         st.markdown(f"##### {T['yield_channel']}")
                         if avg_yield_5y > 0:
                             diff = div_yield_val - avg_yield_5y
                             y_status = "Undervalued" if diff > 0.3 else "Overvalued" if diff < -0.3 else "Fair"
                             y_col = "normal" if diff > 0 else "inverse"
                             st.metric("Yield vs 5Y Avg", f"{round(div_yield_val, 2)}%", f"{round(diff, 2)}% ({y_status})", delta_color=y_col)
                             st.caption(f"5Y Avg Yield: {round(avg_yield_5y, 2)}%")
                         else: st.info("N/A")

                # Scorecard
                st.write("")
                col_g1, col_g2, col_g3 = st.columns(3)
                with col_g1:
                    rev_growth = safe_get(info, 'revenueGrowth') * 100
                    st.metric(T['rev_growth'], f"{round(rev_growth, 2)}%")
                    st.metric(T['div_cagr'], f"{round(cagr_5, 2)}%")
                with col_g2:
                    roe_display = f"{round(roe_val, 2)}%"; roe_txt, roe_col = get_metric_status(roe_val, is_reit, 'roe')
                    st.metric("ROE", roe_display, roe_txt, delta_color=roe_col)
                    st.metric("ROIC", f"{round(roic_val, 2)}%")
                with col_g3:
                    pe_fmt = f"{round(pe_ratio, 1)}" if pe_ratio else "N/A"
                    st.metric("P/E Ratio", pe_fmt)
                    st.metric("PEG", safe_get(info, 'pegRatio'))

            # TAB 4: ANALYSIS
            with tab4:
                # Technical Chart
                st.markdown(f"##### {T['tech_chart']} ℹ️", help=T['help_tech'])
                if not hist_price.empty: st.altair_chart(create_price_chart(hist_price), use_container_width=True)

                st.divider()
                
                col_metrics, col_news = st.columns([1, 2])
                with col_metrics:
                    target_price = safe_get(info, 'targetMeanPrice')
                    recommendation = safe_get(info, 'recommendationKey', 'N/A').title()
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
                    else: st.info("N/A")

                # Auto Summary
                st.write(""); st.markdown(f"##### {T['auto_summary']}")
                bull_points, bear_points = [], []
                if pe_ratio:
                    if not is_reit:
                        if pe_ratio < 15: bull_points.append(f"P/E Ratio {round(pe_ratio, 1)} (Low)")
                        elif pe_ratio > 50: bear_points.append(f"P/E Ratio {round(pe_ratio, 1)} (High)")
                if roic_val > 15: bull_points.append(f"ROIC {round(roic_val, 1)}% (High)")
                if target_price and price_curr:
                    upside = ((target_price - price_curr) / price_curr) * 100
                    if upside > 15: bull_points.append(f"Analyst Upside {round(upside, 1)}%")
                if has_dividends and final_payout_val < 90: bull_points.append(f"Payout {round(final_payout_val, 1)}% (Safe)")
                if total_score >= 6: bull_points.append("Wide Moat")
                if nd_ebitda_val > 5: bear_points.append("High Leverage")
                
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.success(f"🟢 {T['bull']}")
                    for p in bull_points: st.markdown(f"- {p}")
                with sc2:
                    st.error(f"🔴 {T['bear']}")
                    for p in bear_points: st.markdown(f"- {p}")

            # TAB 5: COMPETITORS
            with tab5:
                st.markdown(f"##### {T['comp_title']}")
                col_comp_input, _ = st.columns([3, 1])
                with col_comp_input: peers_input = st.text_input(T['comp_input'], placeholder="Ex: KO, PEP")
                
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
                                    "Ticker": t, "Price": round(p_price, 2), "P/E": round(safe_get(p_info, 'trailingPE'),1),
                                    "Yield%": round(safe_get(p_info, 'dividendYield', 0)*100, 2), "Payout%": round(safe_get(p_info, 'payoutRatio', 0)*100, 1),
                                    "Debt/Eq": round(safe_get(p_info, 'debtToEquity', 0), 1)
                                })
                            except: pass
                        if comp_data:
                            st.dataframe(pd.DataFrame(comp_data).set_index("Ticker"), use_container_width=True)
                        else: st.warning(T['no_data'])
            
            # --- FOOTER & DOWNLOAD ---
            st.divider()
            f_col1, f_col2 = st.columns([4, 1])
            with f_col1:
                st.markdown(f"<div style='color: #888; font-size: 0.8rem;'>{T['footer']}</div>", unsafe_allow_html=True)
            with f_col2:
                st.download_button(label="📥 CSV", data=financials.to_csv().encode('utf-8'), file_name=f'{ticker}_financials.csv', mime='text/csv')