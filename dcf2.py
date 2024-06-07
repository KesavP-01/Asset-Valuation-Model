import pandas as pd
import yfinance as yf
import numpy as np


def Dcf(ticker, noOfYears):
    ticker = yf.Ticker(ticker)
    
    Income_Statement = (ticker.income_stmt.T.astype(float).fillna(0)) / 10**9
    Cash_Flow = (ticker.cash_flow.T.astype(float).fillna(0)) / 10**9
    Balance_Sheet = (ticker.balance_sheet.T.astype(float).fillna(0)) / 10**9
    stats = pd.DataFrame((ticker.info))
    
    Reference_columns = ['Total Revenue', 'EBIT', 'Total Debt', 'Working Capital', 
                         'Capital Expenditure', 'Tax Provision', 'Depreciation And Amortization',
                         'Interest Expense', 'Cash And Cash Equivalents', 'Share Issued', 'EBITDA']
    
    
    pf = pd.concat([Income_Statement, Balance_Sheet, Cash_Flow], axis = 1).sort_index()
    df = pd.DataFrame(columns=Reference_columns, index=pf.index)
    
    for i in Reference_columns:
        df[i] = pf[i]
    df = df.dropna()
    
    # Assumptions
    
    growth = 0.1
    wc_gr = 0.06
    cp_gr = 0.08
    tx_gr = 0.15
    ebit_gr = 0.22
    dna_gr = 0.035
    mar_ret = 0.095
    
    # Feature Creation
    df['rev_growth'] = df['Total Revenue'].pct_change()
    df['EBIAT'] = df['EBIT'] - df['Tax Provision']
    df['Net_Working_Capital'] = df['Working Capital'].diff()
    mul = (stats['enterpriseValue'][1] / 10**9) / df['Total Revenue'].values[-1] 
    
    # Factors 
    df['cap_fac'] = abs(df['Capital Expenditure']) / df['Total Revenue']
    df['dna_fac'] = df['Depreciation And Amortization'] / df['Total Revenue']
    df['tax_fac'] = df['Tax Provision'] / df['EBIT']
    df['ebit_fac'] = df['EBIT'] / df['Total Revenue'] 
    df['wc_fac'] = df['Working Capital'] / df['Total Revenue']
    
    df['FCF'] = df['EBIAT'] + df['Depreciation And Amortization'] - abs(df['Capital Expenditure']) - df['Net_Working_Capital']
    
    
    def Proj(df, final, n):
        return np.linspace(df, final, n)
    n = noOfYears
    no = n
    
    
    # Projections
    years = range(df.index[-1].year + 1, df.index.year[-1] + n + 1)
    
    
    dt = pd.DataFrame(index=years)
    d = pd.DataFrame(index=years)
    
    dt['rev_growth'] = (1+Proj(df['rev_growth'][-1], growth, n)).cumprod()
    dt['cap_fac'] = (1+Proj(df['cap_fac'][-1], cp_gr, n)).cumprod()
    dt['tax_fac'] = (1+Proj(df['tax_fac'][-1], tx_gr, n)).cumprod()
    dt['dna_fac'] = (1+Proj(df['dna_fac'][-1], dna_gr, n)).cumprod()
    dt['ebit_fac'] = (1+Proj(df['ebit_fac'][-1], ebit_gr, n)).cumprod()
    dt['wc_fac'] = (1+Proj(df['wc_fac'][-1], wc_gr, n)).cumprod()
    
    
    
    
    d['Total_Revenue'] = df['Total Revenue'][-1] * dt['rev_growth']
    d['Capex'] = df['Capital Expenditure'][-1] * dt['cap_fac']
    d['Tax'] = df['Tax Provision'][-1] * dt['tax_fac']
    d['EBIT'] = df['EBIT'][-1] * dt['ebit_fac']
    d['WC'] = df['Working Capital'][-1] * dt['wc_fac']
    d['DNA'] = df['Depreciation And Amortization'][-1] * dt['dna_fac']
    d['EBIAT'] = d['EBIT'] - d['Tax']
    d['EBITDA'] = d['EBIT'] + d['Tax']
    d['NWC'] = d['WC'].diff()
    
    d['FCF'] = d['EBIAT'] + d['DNA'] - abs(d['Capex']) - d['NWC']
    
    # WACC Calculation
    beta = ticker.info['beta']
    mar_cap = ticker.info['marketCap'] / 10**9
    
    t = yf.download('^FVX')['Adj Close']
    rf = round(t[-1], 3) / 100
    
    COE = rf + beta * (mar_ret - rf)
    
    debt = df['Total Debt'][-1]
    Total = debt + mar_cap
    COD = (df['Interest Expense'] / df['Total Debt'])[1]
    
    WACC = (COD * (debt/Total) * (1-tx_gr)) + (COE * (mar_cap / Total))
    
    
    # Projected DCF's and Terminal Value
    
    n = np.arange(start=5,stop=mul,step=10)
    ter_val = []
    p_val = []

    for i in n:
        T = d['EBITDA'].values[-1] * i
        ter_val.append(T)   
    
    d['dcf'] = [cf/(1+WACC)**n for n, cf in enumerate(d['FCF'].values, start = 1)]
    
    for i in ter_val:
        p = i / (1 + WACC)**no
        p_val.append(p)
    
    tv = d['Total_Revenue'].values[-1] * mul
    pv = tv/((1+WACC)**no)
    

    # Enterprise Value
    
    Ent_Val = np.sum(d['dcf']) + pv
    cash = df['Cash And Cash Equivalents'][-1]
    Eq_Val = Ent_Val + cash - debt
    Out_Shares = df['Share Issued'][-1]
    
    Implied_Share_Price = Eq_Val / Out_Shares
    
    return pd.DataFrame({'Ent_Val' : Ent_Val, 'Equ_Val': Eq_Val, 'Share_Price': Implied_Share_Price}, index=[0]), d

stat, dcf = Dcf('MSFT', 5)

