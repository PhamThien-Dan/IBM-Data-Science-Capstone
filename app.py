import pandas as pd
import dash
from dash import html, dcc  
from dash.dependencies import Input, Output
import plotly.express as px

# Đọc dữ liệu
spacex_df = pd.read_csv("spacex_launch_geo.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Khởi tạo App
app = dash.Dash(__name__)
server = app.server

# Chuẩn bị danh sách Dropdown
uniquelaunchsites = spacex_df['Launch Site'].unique().tolist()
lsites = [{'label': 'All Sites', 'value': 'All Sites'}]
for site in uniquelaunchsites:
    lsites.append({'label': site, 'value': site})

# Layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown chọn Launch Site
    dcc.Dropdown(id='site_dropdown', 
                 options=lsites, 
                 placeholder='Select a Launch Site here', 
                 searchable=True, 
                 value='All Sites'),
    html.Br(),

    # Biểu đồ Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Thanh trượt Payload
    html.P("Payload range (Kg):", style={'font-weight': 'bold'}),
    dcc.RangeSlider(
        id='payload_slider',
        min=0, max=10000, step=1000,
        marks={i: f'{i} kg' for i in range(0, 10001, 2000)},
        value=[min_payload, max_payload]
    ),

    # Biểu đồ Scatter Chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback cho Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site_dropdown', component_property='value')]
)
def update_graph(site_dropdown):
    if site_dropdown == 'All Sites':
        # Hiển thị tổng số lần phóng thành công theo từng địa điểm
        fig = px.pie(spacex_df, values='class', 
                     names='Launch Site', 
                     title='Total Success Launches By All Sites')
    else:
        # Hiển thị tỷ lệ Thành công (1) vs Thất bại (0) của địa điểm được chọn
        df = spacex_df[spacex_df['Launch Site'] == site_dropdown]
        fig = px.pie(df, names='class', 
                     title=f'Success vs Failure for site {site_dropdown}')
    return fig

# Callback cho Scatter Chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site_dropdown', component_property='value'),
     Input(component_id="payload_slider", component_property="value")]
)
def update_scattergraph(site_dropdown, payload_slider):
    low, high = payload_slider
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    df_filtered = spacex_df[mask]
    
    if site_dropdown != 'All Sites':
        df_filtered = df_filtered[df_filtered['Launch Site'] == site_dropdown]
        
    fig = px.scatter(
        df_filtered, x="Payload Mass (kg)", y="class",
        color="Booster Version",
        title=f'Correlation between Payload and Success for {site_dropdown}',
        hover_data=['Booster Version']
    )
    return fig

if __name__ == '__main__':
    app.run(debug=False)