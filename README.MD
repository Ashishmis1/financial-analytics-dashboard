# Financial Market Analytics Dashboard

Live App: https://financial-analytics-dashboard-ktghw2puvsdhvfyztypmjh.streamlit.app/

## About the Project
I built this dashboard to automate equity research and technical analysis for Indian (NSE/BSE) and global stocks. Instead of just plotting charts, the goal was to build a proper ETL pipeline and generate automated insights that a business stakeholder could actually use. 

It handles data extraction, loads it into a local SQLite database for querying, and outputs benchmarked performance metrics.

## Key Features
* ETL & SQL Backend: Pulls live market data via the Yahoo Finance API, transforms it with Pandas, and loads it into a local database. 
* Plain-English Insights: Translates technical indicators (RSI, Moving Averages) into readable text summaries for non-technical users.
* Market Benchmarking: Compares individual stock returns directly against major indices like the Nifty 50.
* Sector Peer Comparison: Allows side-by-side comparison of up to 3 competing stocks (like TCS vs Infosys vs Wipro) to evaluate risk and volatility.
* BI Ready: 1-click export generates cleaned CSV files specifically formatted for Power BI or Excel.

## Tech Stack
* Python
* SQLite, SQL
* Pandas, NumPy, pandas-ta, yfinance
* Streamlit, Plotly

## How to Run Locally

1. Clone this repository to your local machine.
2. Install the required Python packages:
pip install -r requirements.txt
3. Run the Streamlit app:
streamlit run trading_app.py

Disclaimer: This project is for educational and portfolio purposes only.
