# Import required libraries
import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ------------------------------------------------------------------
# 创建模拟数据，代替原 CSV（原链接 404）
# ------------------------------------------------------------------
np.random.seed(0)

years = list(range(1980, 2014))               # 1980-2013
months = list(range(1, 13))                   # 1-12 月
vehicle_types = ['Superminicar', 'Smallfamilycar', 'Mediumfamilycar', 'Sports']

rows = []
for y in years:
    for m in months:
        for vt in vehicle_types:
            rows.append({
                'Year': y,
                'Month': m,
                'Date': pd.Timestamp(year=y, month=m, day=1),
                'Automobile_Sales': np.random.randint(50, 200),
                'Vehicle_Type': vt,
                'Advertising_Expenditure': np.random.randint(5, 50),
                'Recession': 1 if (y in [1981, 1982, 1991, 2008, 2009]) else 0,
                'unemployment_rate': np.random.uniform(3, 12)
            })

data = pd.DataFrame(rows)
# ------------------------------------------------------------------

# Create Dash application
app = dash.Dash(__name__)

# ------------------------------------------------------------------
# TASK 2.1: Title + Layout
# ------------------------------------------------------------------
app.layout = html.Div(children=[
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'fontSize': 24
        }
    ),

    # TASK 2.2: Dropdowns
    dcc.Dropdown(
        id='report-type',
        options=[
            {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
            {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
        ],
        value='Yearly Statistics',
        placeholder='Select a report type'
    ),

    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in years],
        value=1980,
        placeholder='Select a year'
    ),

    html.Div(id='output-container')
])

# ------------------------------------------------------------------
# TASK 2.3: Enable / Disable year dropdown
# ------------------------------------------------------------------
@app.callback(
    Output('year-dropdown', 'disabled'),
    Input('report-type', 'value')
)
def toggle_year_dropdown(report_type):
    return False if report_type == 'Yearly Statistics' else True


# ------------------------------------------------------------------
# TASK 2.4 + 2.5 + 2.6: Plotting callback
#   - Yearly Statistics  -> 4 个图
#   - Recession Period   -> 4 个图
# ------------------------------------------------------------------
@app.callback(
    Output('output-container', 'children'),
    [Input('report-type', 'value'),
     Input('year-dropdown', 'value')]
)
def update_charts(report_type, selected_year):

    # ===== Recession Period Statistics (TASK 2.5) =====
    if report_type == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]

        # Plot 1: Average automobile sales over recession years (line chart)
        yearly_rec = recession_data.groupby(['Year'])['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x='Year',
                y='Automobile_Sales',
                title='Average Automobile Sales during Recession Period'
            )
        )

        # Plot 2: Average number of vehicles sold by vehicle type (bar chart)
        average_sales = recession_data.groupby(['Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(
                average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title='Average Vehicles Sold by Vehicle Type during Recession'
            )
        )

        # Plot 3: Advertising expenditure share by vehicle type (pie chart)
        exp_rec = recession_data.groupby(['Vehicle_Type'])['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title='Advertising Expenditure Share by Vehicle Type during Recessions'
            )
        )

        # Plot 4: Effect of unemployment rate on vehicle type and sales (bar chart)
        unemp_data = recession_data.groupby(
            ['unemployment_rate', 'Vehicle_Type']
        )['Automobile_Sales'].mean().reset_index()

        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data,
                x='unemployment_rate',
                y='Automobile_Sales',
                color='Vehicle_Type',
                labels={
                    'unemployment_rate': 'Unemployment Rate',
                    'Automobile_Sales': 'Average Automobile Sales'
                },
                title='Effect of Unemployment Rate on Vehicle Type and Sales'
            )
        )

        return [
            html.Div(className='chart-item',
                     children=[html.Div(children=R_chart1),
                               html.Div(children=R_chart2)],
                     style={'display': 'flex'}),
            html.Div(className='chart-item',
                     children=[html.Div(children=R_chart3),
                               html.Div(children=R_chart4)],
                     style={'display': 'flex'})
        ]

    # ===== Yearly Statistics (TASK 2.6) =====
    else:
        input_year = selected_year
        yearly_data = data[data['Year'] == input_year]

        # Plot 1: Average automobile sales per year (whole period)
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas,
                x='Year',
                y='Automobile_Sales',
                title='Average Automobile Sales per Year (1980–2013)'
            )
        )

        # Plot 2: Total monthly automobile sales in selected year
        mas_data = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(
                mas_data,
                x='Month',
                y='Automobile_Sales',
                title='Total Monthly Automobile Sales'
            )
        )

        # Plot 3: Average vehicles sold by vehicle type in selected year
        avr_data = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_data,
                x='Vehicle_Type',
                y='Automobile_Sales',
            ),
        )

        # Plot 4: Total advertisement expenditure for each vehicle type (pie chart)
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title='Total Advertisment Expenditure for Each Vehicle'
            )
        )

        return [
            html.Div(className='chart-item',
                     children=[html.Div(children=Y_chart1),
                               html.Div(children=Y_chart2)],
                     style={'display': 'flex'}),
            html.Div(className='chart-item',
                     children=[html.Div(children=Y_chart3),
                               html.Div(children=Y_chart4)],
                     style={'display': 'flex'})
        ]


# ------------------------------------------------------------------
# Run the app
# ------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8051, debug=True)
