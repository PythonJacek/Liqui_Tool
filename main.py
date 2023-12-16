import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


events=pd.read_excel('Df_1_Project_1.xlsx', sheet_name="Events")

app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

load_figure_template("SLATE")

app.layout = html.Div([
       html.H4("Select Entity"),
       dcc.Dropdown(
              id="Entity_Picker",
              options=events.loc[:,"Entity"].unique(),
              value="Fund_1"
       ),
       dcc.Graph(
              id="Cash_Forecast"
       )
])
@app.callback(
       Output("Cash_Forecast","figure"),
       Input("Entity_Picker","value"),
)

def plot_cashflow_forecats(entity):
       date_recent_cash_balance = events.query("Entity in @entity and Event in 'Cash_Balance_1'")\
                                         .loc[:, "Date"].max()

       cash_flow = events.assign(
              Inflows = lambda x: np.where(x["In/Out"] >= 0, x["Amount"], 0),
              Outflows = lambda x: np.where(x["In/Out"] < 0, x["Amount"] * x["In/Out"], 0),
              Net_Cashflows = lambda x: x["Inflows"] + x["Outflows"])\
              .groupby(["Date", "Entity"], as_index=False)\
              .agg("sum")\
              .query("Entity in @entity and Date >= @date_recent_cash_balance")\
              .assign(
              Cash_Balance = lambda x: x["Net_Cashflows"].cumsum())

       cash_flow_line = px.line(cash_flow,
              x="Date",
              y="Cash_Balance")

       cash_flow_bar = px.bar(cash_flow,
              x="Date",
              y="Net_Cashflows",
              # color="Net_Cashflows",
              # color_continuous_scale='sunset'
                       )
       fig = cash_flow_line.add_trace(cash_flow_bar.data[0])

       return fig


app.run_server(debug=True)

