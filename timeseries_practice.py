import numpy as np
import pandas as pd
import tkinter as tk
import pandas_datareader.data as web

# import plotly.express as px
import plotly.graph_objects as go
# from plotly.subplots import make_subplots

import dash
import dash_core_components as dcc
import dash_html_components as html
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from statsmodels.tsa.seasonal import seasonal_decompose, STL
# from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

start_date = '2010-01-01'
end_date = '2016-12-31'


def get_width_height():
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.after(20, lambda: root.destroy())
    return width, height


def get_tickers():
    #  This returns the available_indicators that will be your column options from your tabular data
    tickers = {'MSFT': 'Microsoft', 'GOOGL': 'Google', 'AMZN': 'Amazon', 'AAPL': 'Apple'}
    return tickers


def get_stock_data_types():
    stock_values = ['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close']
    return stock_values


class ComboDash:
    def __init__(self):
        self.width, self.height = get_width_height()
        self.available_tickers = get_tickers()
        self.available_stock_data = get_stock_data_types()
        self.stock = None
        self.app = dash.Dash(__name__)
        self.dash_app()

    def dash_app(self):
        self.app.layout = html.Div([

            #  Menu items
            html.Div(id='controls-container', children=[
                html.Div([dcc.Dropdown(id='ticker-selection',
                                       options=[{'label': val, 'value': key} for key, val
                                                in self.available_tickers.items()],
                                       value='MSFT',), ],
                         style={'width': '40%',
                                'display': 'table-cell', 'verticalAlign': 'middle'}
                         ),
                html.Div([dcc.Dropdown(id='stock-value-type',
                                       options=[{'label': i, 'value': i} for i in self.available_stock_data],
                                       value='Close'), ],
                         style={'width': '40%',
                                'display': 'table-cell', 'verticalAlign': 'middle'}
                         ),
                html.Div([dcc.Input(id='period', placeholder="Enter Frequency", type="text",
                                    value="1")],
                         style={'width': '20%', 'display': 'table-cell'},
                         ),
            ],
                     style={'width': '100%', 'display': 'table'}),

            # Graphs display
            html.Div([
                dcc.Graph(id='stock-graph', style={'height': f"{int(self.height/2 - 120)}px"}),
                ], style={'width': '50%', 'float': 'left'},
            ),
            html.Div([
                dcc.Graph(id='trend-graph', style={'height': f"{int(self.height/2 - 120)}px"}),
            ], style={'width': '50%', 'float': 'right'},
            ),
            html.Div([
                dcc.Graph(id='seasonal-graph', style={'height': f"{int(self.height/2 - 120)}px"}),
            ], style={'width': '50%', 'float': 'left'},
            ),
            html.Div([
                dcc.Graph(id='noise-graph', style={'height': f"{int(self.height/2 - 120)}px"}),
            ], style={'width': '50%', 'float': 'right'},
            ),
        ])

        @self.app.callback(
            Output('stock-graph', 'figure'),
            [Input('ticker-selection', 'value'),
             Input('stock-value-type', 'value'), ]
        )
        def display_ticker_graph(ticker, stock_type):
            """
            :param ticker: Stock ticker company
            :param stock_type: Stock value type: 'High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close'
            :return: a graph of the stock type of the given company
            """
            fig = go.Figure()
            try:
                self.stock = web.DataReader(ticker, 'yahoo', start_date, end_date)
                fig.add_trace(go.Scatter(
                    x=self.stock.index,
                    y=self.stock[stock_type],
                    name=stock_type,
                    line=dict(color='#000000')
                ))
                fig.update_layout(title=f"{self.available_tickers[ticker]} {stock_type}")
                return fig
            except TypeError:
                return fig

        @self.app.callback([
            Output('trend-graph', 'figure'),
            Output('seasonal-graph', 'figure'),
            Output('noise-graph', 'figure'), ],
            [Input('ticker-selection', 'value'),
             Input('stock-value-type', 'value'),
             Input('period', 'value')]
        )
        def display_trend_season_noise_graph(ticker, stock_type, period):
            figs = [go.Figure() for _ in range(3)]
            self.stock = web.DataReader(ticker, 'yahoo', start_date, end_date)
            decomposed = seasonal_decompose(self.stock[stock_type], model='additive', period=int(period))
            decomp_aspects = ['Trend', 'Residual', 'Seasonal']
            try:
                figs[0].add_trace(go.Scatter(
                    x=self.stock.index,
                    y=decomposed.trend,
                    name=f"Trend",
                    line=dict(color='#000000')
                ))
                figs[1].add_trace(go.Scatter(
                    x=self.stock.index,
                    y=decomposed.resid,
                    name=f"Residual",
                    line=dict(color='#000000')
                ))
                figs[2].add_trace(go.Scatter(
                    x=self.stock.index,
                    y=decomposed.seasonal,
                    name=f"Seasonal",
                    line=dict(color='#000000')
                ))
                for ii, fig in enumerate(figs):
                    fig.update_layout(
                        title=f"{decomp_aspects[ii]}")
            except TypeError:
                print(f"Seasonal decomposition failed for {ticker} stock data.")

            return figs

        self.app.run_server(debug=True)


if __name__ == '__main__':
    das = ComboDash()



