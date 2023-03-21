import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio
from datetime import date, datetime

pio.renderers.default = 'browser'

assets = requests.get('https://api.coincap.io/v2/assets')
assets = pd.json_normalize(assets.json(), record_path='data')[['id', 'symbol']]

app = dash.Dash(__name__)

app.layout = html.Div([
	html.Div([
		html.Div('Date from'),
		dcc.DatePickerSingle(
			id='date_picker_start',
			min_date_allowed=date(2022, 3, 22),
			max_date_allowed=date(2023, 3, 20),
			date=date(2022, 12, 10)),
		html.Div('Date to'),
		dcc.DatePickerSingle(
			id='date_picker_end',
			min_date_allowed=date(2022, 3, 22),
			max_date_allowed=date.today(),
			date=date(2023, 1, 10))
	]),
	html.Div([
		html.Div('Select an asset'),
		dcc.Dropdown(assets['symbol'], 
					value='BTC', 
					id='asset_dropdown')
	], style = {'width': '131px'}),
	dcc.Graph(
		id='output_fig')
])


@app.callback(
	Output(component_id='output_fig', component_property='figure'),
	Input(component_id='date_picker_start', component_property='date'),
	Input(component_id='date_picker_end', component_property='date'),
	Input(component_id='asset_dropdown', component_property='value')
	)
def update_output_fig(start_date, end_date, input_asset):
	asset_value = assets[assets['symbol'] == input_asset]['id'].reset_index(drop=True)[0]
	start_date_unix = str(round(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000))
	end_date_unix = str(round(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000))
	history = requests.get('https://api.coincap.io/v2/assets/'+asset_value+'/history?interval=d1&start='+start_date_unix+'&end='+end_date_unix)
	history = pd.json_normalize(history.json(), record_path='data')[['priceUsd', 'time']]
	history['time'] = pd.to_datetime(history['time'], unit='ms')
	history['priceUsd'] = pd.to_numeric(history['priceUsd'], errors='raise')
	fig = px.bar(history, y='priceUsd', x='time')

	return fig

if __name__ == '__main__':
	app.run_server(debug=True)