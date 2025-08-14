import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from python_units.stock_downloader import StockDataDownloader

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Portfolio Risk Visualizer"

# Initialize downloader
downloader = StockDataDownloader("my_portfolio_data")

def load_portfolio_data():
    """Load all available historical data from the portfolio"""
    portfolio_data = {}
    data_dir = "my_portfolio_data"
    
    if not os.path.exists(data_dir):
        return portfolio_data
    
    # Get all ticker directories
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path):
            ticker = item
            hist_file = os.path.join(item_path, "historical.csv")
            if os.path.exists(hist_file):
                try:
                    data = pd.read_csv(hist_file, index_col=0, parse_dates=True)
                    portfolio_data[ticker] = data
                    print(f"Loaded {ticker}: {len(data)} records")
                except Exception as e:
                    print(f"Error loading {ticker}: {e}")
    
    return portfolio_data

def calculate_returns(data):
    """Calculate daily returns"""
    return data['Close'].pct_change().dropna()

def calculate_portfolio_metrics(portfolio_data):
    """Calculate basic risk metrics for the portfolio"""
    metrics = {}
    
    for ticker, data in portfolio_data.items():
        returns = calculate_returns(data)
        metrics[ticker] = {
            'daily_volatility': returns.std(),
            'annualized_volatility': returns.std() * np.sqrt(252),
            'total_return': (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100,
            'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() != 0 else 0
        }
    
    return metrics

# Load data
portfolio_data = load_portfolio_data()
portfolio_metrics = calculate_portfolio_metrics(portfolio_data)

# App layout
app.layout = html.Div([
    html.H1("Portfolio Risk Visualizer", 
            style={'text-align': 'center', 'margin-bottom': '30px', 'color': '#2c3e50'}),
    
    html.Div([
        html.H3("Portfolio Overview", style={'margin-bottom': '20px'}),
        html.P(f"Loaded {len(portfolio_data)} stocks: {', '.join(portfolio_data.keys())}")
    ], style={'margin-bottom': '30px', 'padding': '20px', 'background-color': '#f8f9fa', 'border-radius': '5px'}),
    
    # Dropdown for chart type selection
    html.Div([
        html.Label("Select Chart Type:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[
                {'label': 'Price History', 'value': 'price'},
                {'label': 'Normalized Returns', 'value': 'normalized'},
                {'label': 'Daily Returns', 'value': 'returns'},
                {'label': 'Volatility Comparison', 'value': 'volatility'},
                {'label': 'Risk-Return Scatter', 'value': 'risk_return'}
            ],
            value='price',
            style={'margin-bottom': '20px'}
        )
    ]),
    
    # Date range picker
    html.Div([
        html.Label("Select Date Range:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=datetime.now() - timedelta(days=365),
            end_date=datetime.now(),
            display_format='YYYY-MM-DD'
        )
    ], style={'margin-bottom': '30px'}),
    
    # Main chart
    dcc.Graph(id='main-chart'),
    
    # Risk metrics table
    html.Div(id='risk-metrics-table', style={'margin-top': '30px'})
    
], style={'padding': '20px', 'max-width': '1200px', 'margin': '0 auto'})

@callback(
    Output('main-chart', 'figure'),
    [Input('chart-type-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_main_chart(chart_type, start_date, end_date):
    """Update the main chart based on selected type and date range"""
    
    if not portfolio_data:
        return go.Figure().add_annotation(
            text="No data available. Please run the stock downloader first.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16)
        )
    
    fig = go.Figure()
    
    # Convert string dates to pandas Timestamps for proper comparison
    base_start_date = pd.to_datetime(start_date)
    base_end_date = pd.to_datetime(end_date)
    
    # Filter data by date range
    filtered_data = {}
    for ticker, data in portfolio_data.items():
        try:
            # Try to use string comparison first (more robust for mixed timezone data)
            start_str = base_start_date.strftime('%Y-%m-%d')
            end_str = base_end_date.strftime('%Y-%m-%d')
            
            # Convert data index to string dates for comparison
            data_dates = data.index.strftime('%Y-%m-%d')
            mask = (data_dates >= start_str) & (data_dates <= end_str)
            filtered_data[ticker] = data.loc[mask]
            
        except Exception as e:
            # Fallback: try timezone-aware comparison
            try:
                # Create local copies for each ticker
                ticker_start_date = base_start_date
                ticker_end_date = base_end_date
                
                # Normalize all to UTC first, then make them compatible
                if hasattr(data.index, 'tz') and data.index.tz is not None:
                    # Data has timezone - convert filter dates to same timezone
                    if ticker_start_date.tz is None:
                        ticker_start_date = ticker_start_date.tz_localize('UTC').tz_convert(data.index.tz)
                        ticker_end_date = ticker_end_date.tz_localize('UTC').tz_convert(data.index.tz)
                else:
                    # Data is timezone-naive - strip timezone from filter dates
                    ticker_start_date = pd.Timestamp(ticker_start_date.date())
                    ticker_end_date = pd.Timestamp(ticker_end_date.date())
                
                mask = (data.index >= ticker_start_date) & (data.index <= ticker_end_date)
                filtered_data[ticker] = data.loc[mask]
                
            except Exception as e2:
                # Final fallback: include all data
                print(f"Warning: Could not filter dates for {ticker}, including all data. Error: {e2}")
                filtered_data[ticker] = data
    
    if chart_type == 'price':
        # Price history chart
        for ticker, data in filtered_data.items():
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name=ticker,
                line=dict(width=2)
            ))
        fig.update_layout(
            title="Stock Price History",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified'
        )
    
    elif chart_type == 'normalized':
        # Normalized returns (starting from 100)
        for ticker, data in filtered_data.items():
            if not data.empty:
                normalized = (data['Close'] / data['Close'].iloc[0]) * 100
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=normalized,
                    mode='lines',
                    name=ticker,
                    line=dict(width=2)
                ))
        fig.update_layout(
            title="Normalized Returns (Base = 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Value",
            hovermode='x unified'
        )
    
    elif chart_type == 'returns':
        # Daily returns
        for ticker, data in filtered_data.items():
            if not data.empty:
                returns = calculate_returns(data) * 100
                fig.add_trace(go.Scatter(
                    x=returns.index,
                    y=returns,
                    mode='lines',
                    name=f"{ticker} Returns",
                    line=dict(width=1, color=px.colors.qualitative.Set1[list(filtered_data.keys()).index(ticker)])
                ))
        fig.update_layout(
            title="Daily Returns (%)",
            xaxis_title="Date",
            yaxis_title="Daily Return (%)",
            hovermode='x unified'
        )
    
    elif chart_type == 'volatility':
        # Rolling volatility
        for ticker, data in filtered_data.items():
            if not data.empty and len(data) > 30:
                returns = calculate_returns(data)
                rolling_vol = returns.rolling(window=30).std() * np.sqrt(252) * 100
                fig.add_trace(go.Scatter(
                    x=rolling_vol.index,
                    y=rolling_vol,
                    mode='lines',
                    name=f"{ticker} (30-day)",
                    line=dict(width=2)
                ))
        fig.update_layout(
            title="Rolling Volatility (30-day, Annualized %)",
            xaxis_title="Date",
            yaxis_title="Volatility (%)",
            hovermode='x unified'
        )
    
    elif chart_type == 'risk_return':
        # Risk-return scatter plot
        returns_data = []
        volatility_data = []
        tickers = []
        
        for ticker, metrics in portfolio_metrics.items():
            returns_data.append(metrics['total_return'])
            volatility_data.append(metrics['annualized_volatility'] * 100)
            tickers.append(ticker)
        
        fig.add_trace(go.Scatter(
            x=volatility_data,
            y=returns_data,
            mode='markers+text',
            text=tickers,
            textposition='top center',
            marker=dict(size=15, opacity=0.7),
            name='Stocks'
        ))
        
        fig.update_layout(
            title="Risk-Return Profile",
            xaxis_title="Annualized Volatility (%)",
            yaxis_title="Total Return (%)",
            showlegend=False
        )
    
    # Common layout updates
    fig.update_layout(
        height=600,
        template='plotly_white',
        font=dict(size=12),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig

@callback(
    Output('risk-metrics-table', 'children'),
    [Input('chart-type-dropdown', 'value')]  # Trigger update when chart changes
)
def update_risk_table(chart_type):
    """Update the risk metrics table"""
    
    if not portfolio_metrics:
        return html.Div("No metrics available")
    
    # Create table data
    table_data = []
    for ticker, metrics in portfolio_metrics.items():
        table_data.append({
            'Stock': ticker,
            'Total Return (%)': f"{metrics['total_return']:.2f}",
            'Annual Volatility (%)': f"{metrics['annualized_volatility']*100:.2f}",
            'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}"
        })
    
    # Create table
    table = html.Table([
        html.Thead([
            html.Tr([html.Th(col) for col in table_data[0].keys()])
        ]),
        html.Tbody([
            html.Tr([html.Td(row[col]) for col in row.keys()]) 
            for row in table_data
        ])
    ], style={
        'width': '100%',
        'border-collapse': 'collapse',
        'margin-top': '20px'
    })
    
    return html.Div([
        html.H3("Risk Metrics Summary"),
        table
    ])

def run_visualizer():
    """Run the portfolio visualizer"""
    print("Starting Portfolio Risk Visualizer...")
    print("Open your browser and go to: http://127.0.0.1:8050")
    app.run(debug=True)

if __name__ == "__main__":
    run_visualizer()

