import glob
import pandas as pd
import dash
import numpy as np
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.validators.scatter.marker import SymbolValidator

#tlo 051c28 051628

# Read the data
frames = []
for f in glob.glob("data/coin_*.csv"):
    frames.append(pd.read_csv(f))
df = pd.concat(frames)
currencies = sorted(df['Name'].unique())
# Initialise the app
app = dash.Dash(__name__)
app.title = "PUTCOIN"
server = app.server
x = df[['Name','Symbol','Open']].groupby(df['Name']).tail(2).reset_index(drop=True)
series = x.groupby(x.Name)['Open'].pct_change().dropna()
pct_change_df = x.join(series, lsuffix='_other', rsuffix='_pct_change').drop(columns=['Open_other']).dropna().drop_duplicates().round(4)


# Define the app
def rsi(values):
    up = values[values>0].mean()
    down = -1*values[values<0].mean()
    return 100 * up / (up + down)
def get_mini_plots():
    names = df[["Name", "Symbol"]].drop_duplicates()
    names.reset_index(drop=True, inplace=True)
    fig = make_subplots(rows=names.shape[0], cols=1)
    for i in range(names.shape[0]):
        open_data = df[df['Name'] == names.loc[i, "Name"]]['Open']
        fig.append_trace(go.Scatter(x=list(range(30)),
                                    y=open_data.iloc[open_data.shape[0]-30:open_data.shape[0]],
                                    line=dict(color='#00628b'), hoverinfo='skip'),
                         row=i + 1, col=1)
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        width= 100,
        height= 720,
        margin=dict(
            l=15,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=30,  # top margin)
        )
    )
    return fig
app.layout = html.Div(children=[
    html.Div(children=[
        html.Div(className="tile",children=[
            html.Img(src=app.get_asset_url('putcoin2.png'), style={'height': 'auto', 'width': '300px',
                                            "margin": "25px 0px 50px 50px","float":"left"}),
        ],style={"width":"100%","height":"100px","float":"left"}),
        html.Div(children=[
            html.Div(className="tile",children=[
                html.Div(children = [
                html.Div(children=[
                    dash_table.DataTable(
                        id='table',
                        columns=[
                            {"name": i, "id": i, "deletable": False, "selectable": False} for i in pct_change_df.columns
                        ],
                        data=pct_change_df.drop_duplicates().to_dict('records'),
                        editable=False,
                        style_header={'backgroundColor': 'rgb(0, 0, 0,0)',
                                      'display': 'none'},
                        style_data={'border': 'none','width':"60%"},
                        style_cell={
                            'backgroundColor': 'rgb(0, 0, 0,0)',
                        },
                        style_cell_conditional=[{
                            'if': {
                                'filter_query': '{Open_pct_change} > 0',
                                'column_id': 'Open_pct_change'
                            },
                                'color': '#3D9970'
                        }, {
                            'if': {
                                'filter_query': '{Open_pct_change} < 0',
                                'column_id': 'Open_pct_change'
                            },
                            'color': '#FF3131'
                        }
                        ],
                        fill_width=False,
                    ), dcc.Graph(id="mini_plots", figure=get_mini_plots(), config={
                        'displayModeBar': False
                    }),
                ],style={ "display": "flex","width": "max-content","margin": "auto"}
                )],
                    style={'height': '100%', 'overflowY': 'auto', "width": "100%",
                           "overflowX": "hidden",
                           "padding-right": "27px"},
                )
            ],
                style={'height': '350px', "width": "25%", "overflow": "hidden", "float": "left", "display": "block",
                       "maxwidth": "25%", "margin-top": "25px"}
            )
        ]),
        html.Div(className="tile",children=[
                    dcc.Graph(
                        id='candle',
                        figure=px.line(template='plotly_dark').update_layout(
                            {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                             'paper_bgcolor': 'rgba(0, 0, 0, 0)',"height":350},),
                        config={
                            'displayModeBar': False
                        }
                    ),
                ],style={'float':'left',"display":"block","width":"70%","margin-top":"25px","margin-left":"25px",
                         "box-shadow:":"5px 10px red","height":"350px"}),
        html.Div(className="tile",children=[dcc.Graph(figure={"layout":{"height": 200}}, config={
                    'displayModeBar': False})],
                 style={'width': '25%', "float": "left", "height": "200px","margin-top":"25px"}),
        html.Div(className="tile",children=[
            dcc.Graph(id="indexes",figure={"layout":{"height": 200}}, config={
                    'displayModeBar': False})],style={'float':'left',"height":"200px","width":"70%",
                                                      "margin-top":"25px","margin-left":"25px"}),
        html.Div(className="tile", children=[dcc.Graph(id='macd', config={
            'displayModeBar': False})],
                 style={'width': '40%', "float": "left", "height": "300px", "margin-top": "25px"}),
        html.Div(className="tile", children=[
            html.Div(
                id="about",
                children=[
                    html.H5("ABOUT", style={"text-align":"center"}),
                    html.P("An irreplaceable platform that can help you with your first steps in stock "
                           "investments. Clear and insightful visualization of cryptocurrencies data dating back as "
                           "far as 2014 give a solid fundaments for analyzing changes in the stock market.  "),
                    html.P("Created by: Mikołaj Kruś & Maciej Filanowicz",style={"text-align":"right"})
                ],style={"margin":"30px"}
            ),


        ],
                 style={'width': '55%', "float": "left", "height": "300px", "margin-top": "25px","margin-left":"25px"}),
    ],style={"width":"90%","height":"100%","overflowX":"hidden","position":"fixed","top":"25px","left":"5%",
             "padding-right":"5%","overflow-y": "scroll","padding-bottom":"25px"})

    #
],style={  "box-sizing": "border-box","margin": "0","overflow":"hidden"})


# Callback
@app.callback(
    Output('indexes', 'figure'),
    [Input('table', 'active_cell')]
)
def update_graph(row):
    if row is None:
        currency = 'Aave'
    else:
        currency = pct_change_df.drop_duplicates().to_dict('records')[row['row']]['Name']
    sub_df = df.loc[df['Name'] == currency]

    fig = make_subplots(rows=1, cols=3, shared_xaxes=True)
    moving_avg = sub_df['Close'].rolling(center=False, window=40).mean().dropna().reset_index(drop=True)
    fig.append_trace(go.Scatter(y=moving_avg, line=dict(color='#00628b')), row=1, col=1)
    on_balance_value = (np.sign(sub_df['Close'].diff()) * sub_df['Volume']).fillna(0).cumsum()
    fig.append_trace(go.Scatter(y=on_balance_value, line=dict(color='#00628b')), row=1, col=2)
    rsiN = sub_df['Close'].diff().rolling(center=False, window=6).apply(rsi)
    fig.append_trace(go.Scatter(y=rsiN, line=dict(color='#00628b')), row=1, col=3)
    fig.update_xaxes(showticklabels=False, showgrid = False)
    fig['layout']['xaxis1']['title'] = 'Moving AVG'
    fig['layout']['xaxis2']['title'] = 'OBV'
    fig['layout']['xaxis3']['title'] = 'RSI'
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template='plotly_dark',
        height = 200,
        showlegend=False,
        hovermode='x',
        margin=dict(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin)
        )

    )
    return fig

# Callback
@app.callback(
    Output('candle', 'figure'),
    [Input('table', 'active_cell')]
)
def update_figure(row):
    if row is None:
        currency = 'Aave'
    else:
        currency = pct_change_df.drop_duplicates().to_dict('records')[row['row']]['Name']
    sub_df = df.loc[df['Name'] == currency]

    # Create figure with secondary y-axis
    fig = make_subplots(
        specs=[[{"secondary_y": True}]])

    # include candlestick with rangeselector
    fig.add_trace(
        go.Ohlc(
            x=sub_df['Date'],
            open=sub_df['Open'],
            high=sub_df['High'],
            low=sub_df['Low'],
            close=sub_df['Close'],
            name=currency),
        secondary_y=True)

    # include a go.Bar trace for volumes
    fig.add_trace(
        go.Bar(
            x=sub_df['Date'],
            y=sub_df['Volume'],
            opacity=0.75,
            marker={'color': '#00628B', 'line_color': '#00628B'},
            name="Volume"),
        secondary_y=False)

    # include marketcap
    fig.add_trace(
        go.Scatter(
            x=sub_df['Date'],
            y=sub_df['Marketcap'],
            line=dict(color='#E8B34A'),
            name="Marketcap"),
        secondary_y=False)

    fig.layout.yaxis2.showgrid = False
    fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
         'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
        template='plotly_dark',
        hovermode='x',
        barmode='group',
        bargroupgap=0,
        bargap=0,
        height = 350,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        # showlegend=False,
        margin=dict(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin)
        )
    )
    fig.update_yaxes(
        title_text="Volume and market capitalization",
        secondary_y=False)
    fig.update_yaxes(
        title_text="Price in USD",
        secondary_y=True)
    return fig

@app.callback(
    Output('macd', 'figure'),
    [Input('table', 'active_cell')]
)
def update_macd(row):
    if row is None:
        currency = 'Aave'
    else:
        currency = pct_change_df.drop_duplicates().to_dict('records')[row['row']]['Name']
    sub_df = df.loc[df['Name'] == currency]

    shortEMA = sub_df.Close.ewm(span=12, adjust=False).mean()
    longEMA = sub_df.Close.ewm(span=26, adjust=False).mean()
    sub_df['macd'] = shortEMA - longEMA
    sub_df['signal'] = sub_df['macd'].ewm(span=9, adjust=False).mean()
    idx = np.argwhere(np.diff(np.sign(    sub_df['signal'] -     sub_df['macd']))).flatten()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sub_df['Date'], y= sub_df['macd'], name='MACD',
                             line=dict(color='#00628b')))
    fig.add_trace(go.Scatter(x=sub_df['Date'], y=sub_df['signal'], name='Signal line',
                             line=dict(color='#E8B34A')))

    buy_sell = sub_df.loc[idx]
    arrow = []
    x = buy_sell['macd'][0] < buy_sell['signal'][0]
    for i in range(len(buy_sell)):
        arrow.append(x)
        x = not x
    fig.add_trace(go.Scatter(mode="markers", x=buy_sell['Date'], y=buy_sell['macd'],
                             marker_symbol=['arrow-up' if i else 'arrow-down' for i in arrow],
                             marker_color=["#3D9970" if i else '#FF3131' for i in arrow],
                             marker_size=9,
                             hovertemplate=['<extra></extra>recommendation to buy' if i else ' <extra></extra>recommendation to sell' for i in arrow],
                             showlegend=False))

    fig.add_trace(
        go.Bar(
            x=sub_df['Date'],
            y=sub_df['macd'] - sub_df['signal'],
            opacity=0.5,
            marker={'color': '#00628B', 'line_color': '#00628B'},
            name="Difference"))
    fig.update_layout(
        title="MACD Indicator",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template='plotly_dark',
        hovermode='x',
        height=250,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(
            l=25,  # left margin
            r=25,  # right margin
            b=25,  # bottom margin
            t=25,  # top margin)
        )
    )
    fig.update_yaxes(visible=False)
    return fig

### INFORMATION SECTION CALLBACK ###
@app.callback(
    Output('about', 'children'),
    [
        Input('candle', 'hoverData'),
        Input('macd', 'hoverData'),
        Input('indexes', 'hoverData'),
    ],
    prevent_initial_call=True
)
def info_change(in1, in2, in3):
    ctx = dash.callback_context

    if not ctx.triggered:
        input_id = 'No clicks yet'
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if input_id == 'candle':
        children = [
            html.H5("CANDLESTICK CHART", style={"text-align": "center"}),
            html.P("It is perhaps the most common visual aid for decision making in stock trading."
                   " Looking at a candlestick, one can identify an asset’s opening and closing prices, highs and lows, and overall range for a specific time frame."
                   " Candlestick charts serve as a cornerstone of technical analysis. For example, when the bar is green and high relative to other time periods,"
                   " it means buyers are very bullish. The opposite is true for a red bar."),
            html.P("Created by: Mikołaj Kruś & Maciej Filanowicz", style={"text-align": "right"})
        ]
        return children
    if input_id == 'macd':
        children = [
            html.H5("MOVING AVERAGE CONVERGENCE/DIVERGENCE", style={"text-align": "center"}),
            html.P(
                "The MACD indicator is a collection of three time series calculated from historical price data, most often the closing price."
                " Exponential moving averages highlight recent changes in a stock's price. By comparing EMAs of different lengths,"
                " the MACD series gauges changes in the trend of a stock."
                " It is recommended to buy if the MACD line crosses up through the signal line, or to sell if it crosses down through the signal line."),
            html.P("Created by: Mikołaj Kruś & Maciej Filanowicz", style={"text-align": "right"})
        ]
        return children

    if input_id == 'indexes':
        children = [
            html.H5("TECHNICAL INDICATORS", style={"text-align": "center"}),
            html.P(
                "MOVING AVERAGE: Given a series of numbers and a fixed subset size, the first element of the moving average is obtained by taking the average of the initial fixed subset of the number series."
                " Then the subset is modified by excluding the first number of the series and including the next value in the subset."),
            html.P(
                "ON_BALANCE VOLUME: When prices are going up, OBV should be going up too, and when prices make a new rally high, then OBV should too."
                " If OBV fails to go past its previous rally high, then this is a negative divergence, suggesting a weak move."),
            html.P(
                "RELATIVE STRENGTH INDEX: The RSI computes momentum as the ratio of higher closes to lower closes:"
                " stocks which have had more or stronger positive changes have a higher RSI than stocks which have had more or stronger negative changes."),
            html.P("Created by: Mikołaj Kruś & Maciej Filanowicz", style={"text-align": "right"})
        ]
        return children

# Run the app
if __name__ == '__main__':
    app.run_server()


