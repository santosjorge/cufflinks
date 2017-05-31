import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from plotly import graph_objs as go 
from pandas_dataread import data as web
from datetime import datetime as dt 

app = dash.Dash('Hello World')

app.layout = html.Div([
	html.H3('Hello World'),
	dcc.Dropdown(
		id='my-dropdown',
		options=[
			{'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
		],
		value='COKE'
		),
	dcc.Graph(id='my-graph')
	])


# Register a callback to update the 'figure' property of the 'my-graph'
# component when the 'value' property of the 'my-dropdown' component changes
@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    df = web.DataReader(

        # this is going to be equal to `COKE`, `TSLA`, or `AAPL`
        selected_dropdown_value,

        'yahoo',
        dt(2017, 1, 1), dt.now()
    )
    return go.Figure(
        data=[{
            'x': df.index,
            'y': df.Close
        }],
        layout={
            'margin': {'l': 20, 'r': 10, 't': 20, 'b': 30}
        }
    )

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)