from django.http import JsonResponse
from django.views import View
import yfinance as yf
import http.client
import json
from decouple import config

SECRET_KEY = config('API_KEY')
class StockDataView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Get stock symbol (uppercase for consistency)
            symbol = kwargs.get('symbol', 'RGTI').upper()
            print(f"Fetching data for symbol: {symbol}")  # Debugging Symbol

            # -------- Fetch stock data using yfinance --------
            stock = yf.Ticker(symbol)

            # Extract Data
            data = {}

            # Current Price
            hist = stock.history(period="1d")
            data['current_price'] = round(hist['Close'].iloc[-1], 2) if not hist.empty else "N/A"
            print(f"Current Price: {data['current_price']}")

            # Market Cap
            market_cap = stock.info.get('marketCap', None)
            data['market_cap'] = market_cap if market_cap else "N/A"
            print(f"Market Cap: {data['market_cap']}")

            # EPS (TTM - Trailing Twelve Months)
            eps = stock.info.get('trailingEps', None)
            data['eps'] = round(eps, 2) if eps else "N/A"
            print(f"EPS: {data['eps']}")

            # Volume
            data['volume'] = stock.info.get('volume', "N/A")
            print(f"Volume: {data['volume']}")

            # Earnings Date
            earnings_dates = stock.calendar if 'Earnings Date' in stock.calendar else "N/A"
            data['earnings_date'] = earnings_dates['Earnings Date'][0].strftime('%Y-%m-%d') if isinstance(earnings_dates, dict) else "N/A"
            print(f"Earnings Date: {data['earnings_date']}")

            # Debt
            total_debt = stock.info.get('totalDebt', None)
            data['debt'] = f"${total_debt:,}" if total_debt else "N/A"
            print(f"Total Debt: {data['debt']}")

            # Earnings (EBITDA)
            ebitda = stock.info.get('ebitda', None)
            data['earnings'] = f"${ebitda:,}" if ebitda else "N/A"
            print(f"Earnings (EBITDA): {data['earnings']}")

            # Total Revenue
        # Total Revenue
            revenue = stock.info.get('totalRevenue', None)
            data['revenue'] = f"${revenue:,}" if revenue else "N/A"
            print(f"Revenue: {data['revenue']}")

            # Dividend Information
            dividend_rate = stock.info.get('dividendRate', None)
            data['dividend'] = f"${dividend_rate:.2f}" if dividend_rate else "No Dividend"
            print(f"Dividend Rate: {data['dividend']}")

            dividend_yield = stock.info.get('dividendYield', None)
            data['dividend_yield'] = f"{(dividend_yield * 100):.2f}%" if dividend_yield else "N/A"
            print(f"Dividend Yield: {data['dividend_yield']}")

            last_dividend_date = stock.info.get('lastDividendDate', None)
            data['last_dividend_date'] = last_dividend_date if last_dividend_date else "N/A"
            print(f"Last Dividend Date: {data['last_dividend_date']}")

            # -------- Fetch Additional Data from Yahoo API (Statistics) --------

            # -------- Fetch Additional Data from Yahoo API (Statistics) --------
            conn = http.client.HTTPSConnection("yahoo-finance15.p.rapidapi.com")

            headers = {
                'x-rapidapi-key': SECRET_KEY,
                'x-rapidapi-host': "yahoo-finance15.p.rapidapi.com"
            }

            # API Request for Statistics Data
            conn.request("GET", f"/api/v1/markets/stock/modules?ticker={symbol}&module=statistics", headers=headers)
            res = conn.getresponse()
            stats_data = json.loads(res.read().decode("utf-8")).get('body', {})
            
            # Get Income Statement Data for Quarterly History
            conn.request("GET", f"/api/v1/markets/stock/modules?ticker={symbol}&module=income-statement", headers=headers)
            res = conn.getresponse()
            income_data = json.loads(res.read().decode("utf-8")).get('body', {})
            
            # Parse Quarterly History (last 3 quarters)
            quarterly_history = []
            if income_data and 'incomeStatementHistoryQuarterly' in income_data:
                quarters = income_data['incomeStatementHistoryQuarterly']['incomeStatementHistory'][:3]
                for i, quarter in enumerate(quarters):
                    quarter_num = i + 2  # Start from Q2 (most recent)
                    quarter_data = {
                        'quarter': f'Q{quarter_num}',
                        'date': quarter['endDate']['fmt'],
                        'revenue': f"${quarter['totalRevenue']['raw']:,}" if quarter.get('totalRevenue', {}).get('raw') else "N/A",
                        'net_income': f"${quarter['netIncome']['raw']:,}" if quarter.get('netIncome', {}).get('raw') else "N/A",
                        'profit_margin': f"{(quarter['netIncome']['raw'] / quarter['totalRevenue']['raw'] * 100):.2f}%" 
                            if quarter.get('netIncome', {}).get('raw') and quarter.get('totalRevenue', {}).get('raw') 
                            else "N/A"
                    }
                    quarterly_history.append(quarter_data)
            
            data['quarterly_history'] = quarterly_history

            # Net Income
            net_income = stats_data.get('netIncomeToCommon', {}).get('raw', None)
            data['net_income'] = f"${net_income / 1_000_000:.2f}M" if net_income else "N/A"
            print(f"Net Income: {data['net_income']}")

            # Enterprise Value
            enterprise_value = stats_data.get('enterpriseValue', {}).get('raw', None)
            data['enterprise_value'] = f"${enterprise_value / 1_000_000_000:.2f}B" if enterprise_value else "N/A"
            print(f"Enterprise Value: {data['enterprise_value']}")

            # ----------- Manual Calculations -----------

            # 1. Calculate PE Ratio
            try:
                # First try using earnings (EBITDA)
                if data['earnings'] != "N/A":
                    earnings_value = float(data['earnings'].replace('$', '').replace(',', ''))
                    if earnings_value != 0:
                        pe_ratio = round(abs(data['current_price'] / (earnings_value / market_cap)), 2)
                        data['pe_ratio'] = pe_ratio
                    else:
                        # Fallback to net income
                        if data['net_income'] != "N/A":
                            net_income_value = float(data['net_income'].replace('$', '').replace('M', '')) * 1_000_000
                            if net_income_value != 0:
                                pe_ratio = round(abs(data['current_price'] / (net_income_value / market_cap)), 2)
                                data['pe_ratio'] = pe_ratio
                            else:
                                data['pe_ratio'] = "N/A"
                        else:
                            data['pe_ratio'] = "N/A"
                else:
                    data['pe_ratio'] = "N/A"
            except Exception as e:
                print(f"PE Ratio calculation error: {str(e)}")
                data['pe_ratio'] = "N/A"
            print(f"PE Ratio (Calculated): {data['pe_ratio']}")

            # 2. Calculate Profit Margin
            try:
                if net_income and revenue and revenue > 0:
                    profit_margin = round((net_income / revenue) * 100, 2)
                    data['profit_margin'] = f"{profit_margin}%" if profit_margin >= 0 else "0.00%"
                else:
                    data['profit_margin'] = "N/A"
            except Exception as e:
                data['profit_margin'] = "N/A"
            print(f"Profit Margin (Calculated): {data['profit_margin']}")

            # Return JSON response
            return JsonResponse(data)

        except Exception as e:
            # Print and return error if any
            print(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)