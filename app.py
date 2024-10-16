import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for rendering the plot to a file
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import io
import base64
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve form data
        ticker = request.form['ticker']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        interval = request.form['interval']
        amount = float(request.form['amount'])
        
        total_investment = 0
        shares = 0
        
        # Download data using yfinance
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        data = data.dropna()
        data_one_month = data.resample('ME').first()
        
        dollar_average_cost_log = []
        
        # Dollar Cost Averaging logic
        for date, row in data_one_month.iterrows():
            dollar_average_cost = amount / row['Adj Close']
            total_investment += amount
            shares += amount / row['Adj Close']
            dollar_average_cost_log.append(
                {
                    'Date': date,
                    'Dollar Average Cost': round(dollar_average_cost, 2),
                    'Total Investment': round(total_investment, 2),
                    'Shares': shares,
                    'Portfolio Value': round(shares * row['Adj Close'], 2)
                }
            )
        
        dollar_average_cost_df = pd.DataFrame(dollar_average_cost_log)
        
        # Final portfolio value and total profit
        final_portfolio_value = round(dollar_average_cost_df['Portfolio Value'].iloc[-1], 2)
        total_profit = round(final_portfolio_value - total_investment, 2)
        
        # Generate the plot
        plt.figure(figsize=(10, 6))
        plt.plot(dollar_average_cost_df['Date'], dollar_average_cost_df['Portfolio Value'], label='Portfolio Value')
        plt.plot(dollar_average_cost_df['Date'], dollar_average_cost_df['Total Investment'], label='Total Investment')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value (USD)')
        plt.title(f'{ticker} Portfolio Value Over Time')
        plt.legend()
        plt.grid(True)
        
        # Save plot to a BytesIO object
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        
        # Encode the image to base64 string
        plot_url = base64.b64encode(img.read()).decode('utf8')
        
        # Render the results page with the plot
        return render_template('results.html', plot_url=plot_url, final_portfolio_value=final_portfolio_value, total_profit=total_profit, total_investment=round(total_investment, 2))
    
    # Render the input form page if no POST request is made
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False)
