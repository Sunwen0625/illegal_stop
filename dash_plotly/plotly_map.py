import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go

# 創建 Dash 應用
app = dash.Dash(__name__)

# 創建初始地圖圖表
fig = px.scatter_mapbox(
    lat=[23.6927], lon=[120.5345],  # 初始座標
    zoom=15, height=600
)
fig.update_layout(mapbox_style="open-street-map")

# 設定 Dash 佈局
app.layout = html.Div([
    dcc.Graph(id='map', figure=fig),
    dcc.Store(id='marker-store', data=[]),  # 用來存儲標記列表
    html.Div([
        html.Label('經度:'),
        dcc.Input(id='input-lon', type='number', placeholder='經度', step=0.0001),
        html.Label('緯度:'),
        dcc.Input(id='input-lat', type='number', placeholder='緯度', step=0.0001),
        html.Label('選擇顏色:'),
        dcc.Dropdown(
            id='input-color',
            options=[
                {'label': '紅色', 'value': 'red'},
                {'label': '藍色', 'value': 'blue'},
                {'label': '綠色', 'value': 'green'},
                {'label': '黃色', 'value': 'yellow'}
            ],
            value='red'  # 預設顏色
        ),
        html.Button('添加標記', id='submit-val', n_clicks=0),
    ], style={'margin-top': '20px'}),
    html.Div([
        html.Label('選擇要移除的標記:'),
        dcc.Dropdown(id='remove-marker-dropdown', placeholder='選擇標記'),
        html.Button('移除標記', id='remove-val', n_clicks=0)
    ], style={'margin-top': '20px'}),
])

# 回調函數，用於添加和移除標記，以及地圖居中
@app.callback(
    [Output('map', 'figure'),
     Output('marker-store', 'data'),
     Output('remove-marker-dropdown', 'options')],
    [Input('submit-val', 'n_clicks'),
     Input('remove-val', 'n_clicks'),
     Input('remove-marker-dropdown', 'value')],
    [State('input-lon', 'value'),
     State('input-lat', 'value'),
     State('input-color', 'value'),
     State('marker-store', 'data')]
)
def update_map(add_clicks, remove_clicks, remove_value, lon_input, lat_input, color, markers):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    center_lat, center_lon = 23.6927, 120.5345  # 預設地圖中心

    # 添加標記邏輯
    if triggered_id == 'submit-val' and lon_input is not None and lat_input is not None:
        lon = lon_input
        lat = lat_input
        markers.append({'lon': lon, 'lat': lat, 'label': f'Marker {len(markers) + 1}', 'color': color})

    # 移除標記邏輯
    if triggered_id == 'remove-val' and remove_value is not None:
        markers = [marker for marker in markers if marker['label'] != remove_value]

    # 如果有選擇標記，將地圖居中到該標記
    if triggered_id == 'remove-marker-dropdown' and remove_value is not None:
        selected_marker = next(marker for marker in markers if marker['label'] == remove_value)
        center_lat, center_lon = selected_marker['lat'], selected_marker['lon']

    # 更新地圖
    new_fig = px.scatter_mapbox(
        lat=[center_lat], lon=[center_lon],  # 設定中心點
        zoom=15, height=600
    )
    new_fig.update_layout(mapbox_style="open-street-map")

    # 添加所有現有的標記到地圖
    for marker in markers:
        new_fig.add_trace(go.Scattermapbox(
            lat=[marker['lat']], lon=[marker['lon']],
            mode='markers',
            marker=go.scattermapbox.Marker(size=14, color=marker['color']),
            name=marker['label']
        ))

    # 更新標記下拉選項
    options = [{'label': marker['label'], 'value': marker['label']} for marker in markers]

    return new_fig, markers, options

# 運行應用
if __name__ == '__main__':
    app.run_server(debug=True)
