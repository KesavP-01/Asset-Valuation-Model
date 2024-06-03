
# Discounted Cash Flow Modelling

## Description:
This script calculates the intrinsic value of a company's stock using the Discounted Cash Flow (DCF) method. It retrieves financial data from Yahoo Finance, projects future revenue and expenses, and estimates the company's future cash flows. By adjusting for growth rates and calculating present value, it derives the enterprise value, equity value, and an implied share price for the stock.

## Usage:

To use this script, follow these steps:

**Import the Necessary Libraries**: Ensure you have yfinance, pandas, and numpy installed. Import these libraries at the beginning of your script.

**Define the DCF Function**: Implement the DCF function, which takes a stock ticker symbol and the number of years (nyears) you want to project into the future as inputs.

**Retrieve Financial Data**: The function uses Yahoo Finance to download the stock's income statement, balance sheet, and cash flow statement. These financial statements are then transposed and trimmed to include only the most recent four years of data.

**Calculate Key Financial Metrics**: The function calculates various financial metrics such as revenue growth, net working capital changes, capital expenditure to sales ratio, EBIT to sales ratio, tax to EBIT ratio, and depreciation to sales ratio. It then computes the Free Cash Flow (FCF) for each year.

**Determine Cost of Capital**: The function downloads the risk-free rate, retrieves the stock's beta, market capitalization, and other financial information to calculate the cost of equity, cost of debt, and the Weighted Average Cost of Capital (WAAC).

**Project Future Financials**: The function projects future revenue growth, EBIT to sales ratio, capital expenditures to sales ratio, tax to EBIT ratio, net working capital to sales ratio, and depreciation to sales ratio for the specified number of years. It then calculates the future revenue, EBIT, capital expenditures, tax provision, net working capital, depreciation, and Free Cash Flow for each projected year.

**Calculate Present Value and Terminal Value**: The function calculates the present value of the projected Free Cash Flows and the terminal value at the end of the projection period. These values are then summed to obtain the enterprise value.

**Compute Equity Value and Implied Share Price**: The function adjusts the enterprise value by adding cash and subtracting debt to obtain the equity value. Finally, it divides the equity value by the number of shares outstanding to get the implied share price.

**Call the Function**: Call the DCF function with the desired stock ticker and projection period. For example, to estimate the intrinsic value of NVIDIA Corporation (ticker: NVDA) over a 10-year period, you would call DCF('NVDA', 10).

**Analyze the Output**: The function returns a DataFrame containing the enterprise value, equity value, and implied share price. Review these values to understand the estimated intrinsic value of the stock.

## Results
The output is a DataFrame containing the following:

**Enterprise_Value**: The total value of the company.\
**Equity_Value**: The value of the company's equity.\
**Implied_Share_Price**: The estimated price per share based on the DCF analysis.