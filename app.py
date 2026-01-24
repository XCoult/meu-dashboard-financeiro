# --- MOAT CALCULATION (Lógica Corrigida para REITs) ---
        moat_score = 0
        moat_data = [] # (Name, Value, Class)
        
        if is_reit:
            # --- LÓGICA ESPECÍFICA PARA REITS ---
            
            # 1. Scale (Tamanho é crítico para REITs terem crédito barato)
            if mkt_cap > 30_000_000_000: 
                moat_score += 1
                moat_data.append(("Scale", "Massive Cap", "moat-good"))
            elif mkt_cap > 10_000_000_000:
                moat_data.append(("Scale", "Large Cap", "moat-avg"))
            else:
                moat_data.append(("Scale", "Mid/Small", "moat-bad"))

            # 2. Gross Margin (Eficiência na gestão dos imóveis)
            # REITs bons costumam ter margens brutas altas (>60%)
            gm_val_last = series_gross_margin.iloc[-1] if series_gross_margin is not None else 0
            if gm_val_last > 60: 
                moat_score += 1
                moat_data.append(("Efficiency", f"GM {round(gm_val_last,1)}%", "moat-good"))
            elif gm_val_last > 40:
                moat_data.append(("Efficiency", f"GM {round(gm_val_last,1)}%", "moat-avg"))
            else:
                moat_data.append(("Efficiency", f"GM {round(gm_val_last,1)}%", "moat-bad"))

            # 3. Dividend Growth (O "selo de qualidade" de um REIT)
            if cagr_5 > 3:
                moat_score += 1
                moat_data.append(("Track Record", f"Div Grow {round(cagr_5,1)}%", "moat-good"))
            elif cagr_5 > 0:
                moat_data.append(("Track Record", "Stable Divs", "moat-avg"))
            else:
                moat_data.append(("Track Record", "Cuts/Flat", "moat-bad"))

            # 4. Solvency (Dívida Controlada é Vantagem Competitiva em juros altos)
            if nd_ebitda_val < 5.5 and nd_ebitda_val > 0:
                moat_score += 1
                moat_data.append(("Safety", f"NetDebt {round(nd_ebitda_val,1)}x", "moat-good"))
            elif nd_ebitda_val < 6.5:
                moat_data.append(("Safety", f"NetDebt {round(nd_ebitda_val,1)}x", "moat-avg"))
            else:
                moat_data.append(("Safety", "High Leverage", "moat-bad"))

        else:
            # --- LÓGICA PARA EMPRESAS NORMAIS (Inalterada) ---
            
            # 1. Efficiency (ROIC)
            if roic_val > 15: 
                moat_score += 1
                moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-good"))
            elif roic_val > 8:
                moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-avg"))
            else:
                moat_data.append(("Efficiency", f"ROIC {round(roic_val,1)}%", "moat-bad"))
                
            # 2. Pricing Power (Gross Margin)
            gm_val_last = series_gross_margin.iloc[-1] if series_gross_margin is not None else 0
            if gm_val_last > 40: 
                moat_score += 1
                moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-good"))
            elif gm_val_last > 20:
                moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-avg"))
            else:
                moat_data.append(("Pricing", f"GM {round(gm_val_last,1)}%", "moat-bad"))
                
            # 3. Profitability (Net Margin)
            pm_val_calc = safe_get(info, 'profitMargins') * 100
            if pm_val_calc > 15: 
                moat_score += 1
                moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-good"))
            elif pm_val_calc > 5:
                moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-avg"))
            else:
                moat_data.append(("Profit", f"Net Mg {round(pm_val_calc,1)}%", "moat-bad"))
            
            # 4. Scale (Market Cap)
            if mkt_cap and mkt_cap > 100_000_000_000: 
                moat_score += 1
                moat_data.append(("Scale", "Mega Cap", "moat-good"))
            elif mkt_cap and mkt_cap > 10_000_000_000:
                moat_data.append(("Scale", "Large Cap", "moat-avg"))
            else:
                moat_data.append(("Scale", "Mid/Small", "moat-avg"))