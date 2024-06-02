import yfinance as yf
import pandas as pd
import numpy as np




def DCF(ticker, nyears):
    stock = yf.Ticker(ticker)
    
    Income_statement = stock.income_stmt
    Balance_sheet = stock.balance_sheet
    Cash_flow = stock.cash_flow
    
    Income_statement = Income_statement.T
    Balance_sheet = Balance_sheet.T
    Cash_flow = Cash_flow.T
    Cash_flow = Cash_flow[ :4]
    Income_statement = Income_statement[:4]
    Balance_sheet = Balance_sheet[: 4]
    
    
    df = pd.concat([Income_statement, Balance_sheet, Cash_flow], axis = 1).sort_index()
    
    
    df['revgrowth'] = df['Total Revenue'].pct_change()
    df['nwc'] = df['Working Capital'].diff()
    df['nwc/sales'] = df['nwc'] / df['Total Revenue']
    df['capex/sales'] = df['Capital Expenditure'] / df['Total Revenue']
    df['ebit/sales'] = df['EBIT'] / df['Total Revenue']
    df['tax/ebit'] = df['Tax Provision'] / df['EBIT']
    df['ebiat'] = df['EBIT'] - df['Tax Provision']
    df['dep/sales'] = df['Reconciled Depreciation'] / df['Total Revenue']
    
    df['FCF'] = df['ebiat'] + df['Reconciled Depreciation'] - abs(df['Capital Expenditure']) - df['nwc']
    
    rf = yf.download('^FVX')['Adj Close']
    rf = rf[-1] / 100
    b = stock.info['beta']
    mc = stock.info['marketCap']
    Cost_of_Equity = (rf + b * (0.093 - rf)) 
    Cost_of_debt = (df['Interest Expense'] / df['Total Debt'])[1] 
    Total = mc + df['Total Liabilities Net Minority Interest'][-1]
    debt = df['Total Liabilities Net Minority Interest'][-1]
    
    
    WAAC = ((Cost_of_Equity * (mc/Total)) + (Cost_of_debt * (debt / Total)* (1 - 0.21))) 
    
    
    def forecast(Initial, Terminal, years):
        return np.linspace(Initial, Terminal, years)
    
    years = range(df.index[-1].year + 1, df.index[-1].year + 1 + nyears)
    
    dt = pd.DataFrame(index=years)
    
    dt['rev_growth'] = forecast(df['revgrowth'][-1], 0.04, nyears)
    dt['ebit/sales'] = forecast(df['ebit/sales'][-1], 0.2, nyears)
    dt['capex/sales'] = forecast(df['capex/sales'][-1], 0.05, nyears)
    dt['tax/ebit'] = forecast(df['tax/ebit'][-1], 0.22, nyears)
    dt['nwc/sales'] = forecast(df['nwc/sales'][-1], 0.06, nyears)
    dt['dep/sales'] = forecast(df['dep/sales'][-1], 0.025, nyears)
    
    dt['Total Revenue'] = df['Total Revenue'][-1] * (1+dt['rev_growth']).cumprod()
    dt['Capex'] = df['Capital Expenditure'][-1] * (1+dt['capex/sales']).cumprod()
    dt['EBIT'] = df['EBIT'][-1] * (1+dt['ebit/sales']).cumprod()
    dt['Tax Provision'] = df['Tax Provision'][-1] * (1+dt['tax/ebit']).cumprod()
    dt['nwc'] = df['nwc'][-1] * (1+dt['nwc/sales']).cumprod()
    dt['dep'] = df['Reconciled Depreciation'][-1] * (1+dt['dep/sales']).cumprod()
    dt['EBIAT'] = dt['EBIT'] - dt['Tax Provision']
    
    dt['FCF'] = dt['EBIAT'] + dt['dep'] - abs(dt['Capex']) - dt['nwc']  
    
    def Present_Value(FCF, DF):
        pv = [cf/(1+DF)**n for n, cf in enumerate(FCF, start = 1)]
        return pv
    dt['PV'] = Present_Value(dt['FCF'].values, WAAC)
    
    TV = (dt['PV'].values[-1] * (1+0.025)) / (WAAC - 0.025)
    TV_pv = TV / (1+WAAC)**nyears
    
    Ent_val = np.sum(dt['FCF']) + TV_pv
    cash = df['Cash And Cash Equivalents'][-1]
    Equity_Val = Ent_val - debt + cash
    Shares = df['Share Issued'][-1]
    
    ImpliedSharePrice = Equity_Val / Shares
    
    return pd.DataFrame({'Enterprise_Value' : Ent_val, 'Equity_Value' : Equity_Val,
                         'Implied_Share_Price' : ImpliedSharePrice}, index = [ticker])


stock = DCF('NVDA', 10)
