# --- VI. COMPETITOR COMPARISON ---
        st.divider()
        st.markdown("### VI. Comparação com Competidores")
        
        col_comp_input, col_comp_help = st.columns([3, 1])
        with col_comp_input:
            peers_input = st.text_input("Adicionar concorrentes para comparar (separados por vírgula):", 
                                      placeholder="Ex: KO, PEP, MNST (se estiver analisando bebidas)")
        
        if peers_input:
            with st.spinner("Buscando dados dos competidores..."):
                tickers_to_compare = [t.strip().upper() for t in peers_input.split(",") if t.strip()]
                # Adiciona o ticker principal à lista se não estiver
                if ticker not in tickers_to_compare:
                    tickers_to_compare.insert(0, ticker)
                
                comp_data = []
                
                for t in tickers_to_compare:
                    try:
                        p_stock = yf.Ticker(t)
                        p_info = p_stock.info
                        
                        # Cálculos rápidos
                        p_price = safe_get(p_info, 'currentPrice')
                        p_pe = safe_get(p_info, 'trailingPE')
                        p_fwd_pe = safe_get(p_info, 'forwardPE')
                        p_div_yield = safe_get(p_info, 'dividendYield', 0) * 100
                        p_payout = safe_get(p_info, 'payoutRatio', 0) * 100
                        p_roe = safe_get(p_info, 'returnOnEquity', 0) * 100
                        p_pm = safe_get(p_info, 'profitMargins', 0) * 100
                        p_debt_eq = safe_get(p_info, 'debtToEquity', 0)
                        
                        comp_data.append({
                            "Ticker": t,
                            "Price ($)": p_price,
                            "P/E (Trailing)": p_pe if p_pe else None,
                            "P/E (Forward)": p_fwd_pe if p_fwd_pe else None,
                            "Yield (%)": p_div_yield,
                            "Payout (%)": p_payout,
                            "ROE (%)": p_roe,
                            "Net Margin (%)": p_pm,
                            "Debt/Eq": p_debt_eq
                        })
                    except:
                        pass
                
                if comp_data:
                    df_comp = pd.DataFrame(comp_data).set_index("Ticker")
                    
                    # Formatação condicional (Highlight no maior valor para métricas boas, menor para ruins)
                    st.dataframe(
                        df_comp.style.format("{:.2f}").highlight_max(subset=["Yield (%)", "ROE (%)", "Net Margin (%)"], color='#d4edda', axis=0)
                        .highlight_min(subset=["P/E (Trailing)", "P/E (Forward)", "Debt/Eq", "Payout (%)"], color='#d4edda', axis=0),
                        use_container_width=True
                    )
                else:
                    st.warning("Não foi possível encontrar dados para os tickers informados.")

        # --- VII. VALUATION LAB ---
        st.divider()
        st.markdown("### VII. Laboratório de Valuation")
        st.caption("Estimativas matemáticas simples baseadas em fórmulas clássicas. Não são recomendações de compra.")
        
        v1, v2 = st.columns(2)
        
        # 1. Fórmula de Graham (Simplificada)
        # V = Sqrt(22.5 * EPS * BVPS)
        with v1:
            st.markdown("##### 🧮 Número de Graham")
            try:
                eps_ttm = safe_get(info, 'trailingEps')
                bvps = safe_get(info, 'bookValue')
                
                if eps_ttm > 0 and bvps > 0:
                    graham_number = np.sqrt(22.5 * eps_ttm * bvps)
                    upside_graham = ((graham_number - price_curr) / price_curr) * 100
                    
                    st.metric("Valor Justo (Graham)", f"${round(graham_number, 2)}")
                    
                    if upside_graham > 0:
                        st.success(f"Potencial de Upside: +{round(upside_graham, 1)}% (Subavaliado)")
                    else:
                        st.error(f"Sobreavaliado em: {round(upside_graham, 1)}%")
                    
                    st.caption(f"*Baseado em EPS (${eps_ttm}) e Valor Patrimonial (${bvps}). Ideal para empresas industriais/financeiras clássicas.*")
                else:
                    st.warning("Dados insuficientes (EPS ou Book Value negativos) para cálculo de Graham.")
            except:
                st.info("Erro ao calcular Graham Number.")

        # 2. Modelo de Gordon (Dividendos)
        # P = D1 / (k - g)
        with v2:
            st.markdown("##### 📈 Modelo de Gordon (Dividendos)")
            if has_dividends:
                try:
                    # Premissas interativas
                    risk_free_rate = 0.045 # Treasury 10y aprox
                    beta_gordon = beta_val if beta_val and beta_val > 0 else 1.0
                    equity_risk_premium = 0.05
                    
                    # Custo de Equity (CAPM)
                    k = risk_free_rate + (beta_gordon * equity_risk_premium)
                    
                    # Taxa de crescimento sustentável (g)
                    # Limitamos g a 2% a menos que k para o modelo não quebrar
                    g_sustainable = min(cagr_5/100, k - 0.01) if cagr_5 > 0 else 0.02
                    
                    div_rate_g = safe_get(info, 'dividendRate')
                    
                    if div_rate_g > 0 and k > g_sustainable:
                        fair_value_gordon = (div_rate_g * (1 + g_sustainable)) / (k - g_sustainable)
                        upside_gordon = ((fair_value_gordon - price_curr) / price_curr) * 100
                        
                        st.metric("Valor Justo (Gordon)", f"${round(fair_value_gordon, 2)}")
                        
                        if upside_gordon > 0:
                            st.success(f"Potencial de Upside: +{round(upside_gordon, 1)}%")
                        else:
                            st.error(f"Sobreavaliado em: {round(upside_gordon, 1)}%")
                            
                        st.caption(f"*Premissas: Taxa de Desconto {round(k*100, 1)}%, Crescimento Perpétuo {round(g_sustainable*100, 1)}%.*")
                    else:
                        st.warning("Modelo inaplicável (Crescimento muito alto ou sem dividendos).")
                except:
                    st.info("Erro no cálculo de Gordon.")
            else:
                st.info("Este modelo aplica-se apenas a empresas pagadoras de dividendos.")

        # --- FOOTER ---
        st.write("")
        st.write("")
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #888; font-size: 0.8rem;'>
            <b>Paulo Moura Dashboard</b> | Dados fornecidos por Yahoo Finance.<br>
            Esta ferramenta é para fins educacionais e informativos. Não constitui aconselhamento financeiro.<br>
            As métricas de 'Moat' e 'Safety' são baseadas em regras heurísticas gerais.
        </div>
        """, unsafe_allow_html=True)