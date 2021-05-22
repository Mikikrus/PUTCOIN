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
        html.Div(children=[
            html.Img(src=app.get_asset_url('PUTCOIN.png'), style={'height': 'auto', 'width': '200px',
                                            "margin": "25px 0px 50px 50px","float":"left"}),
        ],style={"width":"100%","height":"100px","float":"left"}),
        html.Div(children=[
            html.Div(children=[
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
                        style_data={'border': 'none'},
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
                        fill_width=False
                    ), dcc.Graph(id="mini_plots", figure=get_mini_plots(), config={
                        'displayModeBar': False
                    }),
                ],
                    style={'height': '100%', 'overflowY': 'auto', "width": "100%", "display": "flex",
                           "overflowX": "hidden",
                           "padding-right": "17px"},
                )
            ],
                style={'height': '450px', "width": "25%", "overflow": "hidden", "float": "left", "display": "block",
                       "maxwidth": "25%", "margin-top": "20px"}
            )
        ]),
        html.Div(children=[
                    dcc.Graph(
                        id='candle',
                        figure=px.line(template='plotly_dark').update_layout(
                            {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                             'paper_bgcolor': 'rgba(0, 0, 0, 0)'}),
                        config={
                            'displayModeBar': False
                        }
                    ),
                ],style={'float':'left',"display":"block","width":"75%","margin-top":"25px"}),
        html.Div(children=[dcc.Graph(figure={"layout":{"height": 200}}, config={
                    'displayModeBar': False})],
                 style={'width': '25%', "float": "left", "height": "200px","margin-top":"25px"}),
        html.Div(children=[
            dcc.Graph(id="indexes", config={
                    'displayModeBar': False})],style={'float':'left' ,"height":"200px","margin-top":"25px",
                                                      "margin-left":"25px"})
    ],style={"width":"100%","height":"100%","overflowX":"hidden","position":"fixed","top":"0","left":"0"})

    #
],style={  "box-sizing": "border-box","margin": "0"})


# Callback
@app.callback(
    Output('indexes', 'figure'),
    [Input('table', 'active_cell')]
)
def update_graph(row):
    sub_df = df.loc[df['Name'] == pct_change_df.drop_duplicates().to_dict('records')[row['row']]['Name']]
    fig = make_subplots(rows=1, cols=3)
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
    sub_df = df.loc[df['Name'] == pct_change_df.drop_duplicates().to_dict('records')[row['row']]['Name']]
    # Create figure with secondary y-axis
    fig = make_subplots(
        specs=[[{"secondary_y": True}]])

    # include candlestick with rangeselector
    fig.add_trace(
        go.Candlestick(
            x=sub_df['Date'],
            open=sub_df['Open'],
            high=sub_df['High'],
            low=sub_df['Low'],
            close=sub_df['Close'],
            name=pct_change_df.drop_duplicates().to_dict('records')[row['row']]['Name']),
        secondary_y=True)

    # include a go.Bar trace for volumes
    fig.add_trace(
        go.Bar(
            x=sub_df['Date'],
            y=sub_df['Volume'],
            opacity=0.75,
            marker={'color': 'steelblue', 'line_color': 'steelblue'},
            name="Volume"),
        secondary_y=False)

    # include marketcap
    fig.add_trace(
        go.Scatter(
            x=sub_df['Date'],
            y=sub_df['Marketcap'],
            line=dict(color='orange'),
            name="Marketcap"),
        secondary_y=False)

    fig.layout.yaxis2.showgrid = False
    fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
         'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
        template='plotly_dark',
        barmode='group',
        bargroupgap=0,
        bargap=0,
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

# Run the app
if __name__ == '__main__':
    app.run_server()


