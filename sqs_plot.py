import json
import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import base64
import io
import  numpy as np

app = dash.Dash(__name__)

# Layout with dynamically populated checklist and upload functionality
app.layout = html.Div([
    html.H1('SRO Dashboard'),

    # File upload component
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a JSON File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    
    # Dynamically populated interaction checklist
    dcc.Checklist(
        id='interaction-checklist',
        options=[],  # Dynamically populated
        value=[],  # Dynamically populated default selection
        labelStyle={'display': 'inline-block'}
    ),
    
    # Dropdown to choose between "1st shell" and "2nd shell"
    dcc.Dropdown(
        id='shell-dropdown',
        options=[
            {'label': '1st shell', 'value': 0},
            {'label': '2nd shell', 'value': 1},
            {'label': 'Average', 'value': 2}
        ],
        value=2,  # Default to 1st shell
        clearable=False
    ),
    
    # Line plot for interactions vs. sqs_id
    dcc.Graph(id='interaction-sros-plot'),
    # Dropdown to select sqs_id
    dcc.Dropdown(
        id='sqs-id-dropdown',
        clearable=False
    ),
    
    # Bar chart for selected sqs_id
    # dcc.Graph(id='sros-bar-chart')

    # Div to contain plot and table side by side
    html.Div([
        # Left column for the spider plot
        html.Div([
            dcc.Graph(id='spider-plot',style={'width': '100%', 'height': '700px'})
        ], style={'width': '60%', 'display': 'inline-block'}),

        # Right column for the table
        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[{'name': 'Pair', 'id': 'Pair'},
                         {'name': '1st Shell', 'id': '1st Shell'},
                         {'name': '2nd Shell', 'id': '2nd Shell'},
                         {'name': 'Average', 'id': 'Average'}],
                data=[],  # Data to be dynamically updated
                style_table={'width': '100%','height': '700px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'left'},
            )
        ], style={'width': '40%', 'display': 'inline-block','padding-top':'200px','padding-left':'0px' })
    ], style={'display': 'flex'})   
])

# Helper function to parse the uploaded JSON file
def parse_contents(contents):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        # Assuming the user uploads a JSON file
        data = json.load(io.StringIO(decoded.decode('utf-8')))
        df=pd.DataFrame(data).sort_values(by='time') #sort_values(by='sqs_id')
        # Subtract the first entry from all others and calculate hours passed
        df['time_difference_hours'] = ((df['time'] - df['time'].iloc[0]) / 3600).round(3)        
        return df
    except Exception as e:
        print(e)
        return None

# Callback to update the interaction checklist and dropdown options based on uploaded data
@app.callback(
    [Output('interaction-checklist', 'options'),
     Output('interaction-checklist', 'value'),
     Output('sqs-id-dropdown', 'options'),
     Output('sqs-id-dropdown', 'value')],
    [Input('upload-data', 'contents')]
)
def update_controls(contents):
    if contents is not None:
        df = parse_contents(contents)
        if df is not None:
            # Extract interaction keys from the first entry's 'sros'
            first_entry_sros = df.iloc[0]['sros']
            interaction_options = [{'label': k, 'value': k} for k in first_entry_sros.keys()]
            
            # Default values for the checklist (select all interactions by default)
            default_interaction = list(first_entry_sros.keys())
            
            # Create dropdown options for sqs_id
            sqs_options = [{'label': f"SQS ID: {row['sqs_id']}", 'value': row['sqs_id']} for _, row in df.iterrows()]
            
            return interaction_options, default_interaction, sqs_options, df.iloc[0]['sqs_id']
    
    return [], [], [], None

@app.callback(
    [Output('spider-plot', 'figure'),
     Output('data-table', 'data')],
    [Input('sqs-id-dropdown', 'value'),
     State('upload-data', 'contents')]
)
def update_spider_chart_and_table(sqs_id, contents):
    if contents is not None and sqs_id is not None:
        df = parse_contents(contents)
        if df is not None:
            # Find the entry corresponding to the selected sqs_id
            entry = next(item for item in df.to_dict('records') if item['sqs_id'] == sqs_id)
    
            # Extract SROs for plotting
            sros_data = entry['sros']

            # Create a DataFrame for both 1st shell and 2nd shell values
            sros_df = pd.DataFrame(list(sros_data.items()), columns=['Pair', 'SRO Values'])
            sros_df['1st Shell'] = sros_df['SRO Values'].apply(lambda x: x[0])
            sros_df['2nd Shell'] = sros_df['SRO Values'].apply(lambda x: x[1])
            sros_df['Average'] = sros_df['SRO Values'].apply(lambda x: x[2])

            # Categories for radar plot
            categories = sros_df['Pair'].tolist()  

            # Create the radar plot (spider plot) using plotly.graph_objects
            fig = go.Figure()

            # Add trace for 1st shell
            fig.add_trace(go.Scatterpolar(
                r=sros_df['1st Shell'],
                theta=categories,
                opacity=0.9,
                fill='toself',
                name='1st Shell'
            ))

            # Add trace for 2nd shell
            fig.add_trace(go.Scatterpolar(
                r=sros_df['2nd Shell'],
                theta=categories,
                fill='toself',
                opacity=0.5,
                name='2nd Shell'
            ))

            # Add trace for Average
            fig.add_trace(go.Scatterpolar(
                r=sros_df['Average'],
                theta=categories,
                opacity=0.6,
                fill='toself',
                name='Average'
            ))

            # Update layout for the radar plot
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[-0.5, 0.5]  # Adjust based on your data range
                    )),
                title=f'SROs for SQS ID {sqs_id}',
                showlegend=True,
                legend=dict(
                    orientation="v",  # Horizontal legend
                    yanchor="bottom",  # Anchor legend at the bottom
                    y=0.7,  # Place the legend slightly above the plot
                    xanchor="left",  # Center the legend horizontally
                    x=0.0  # Horizontal position (center)
                )
            )

            # Convert DataFrame to dictionary for DataTable
            table_data = sros_df[['Pair', '1st Shell', '2nd Shell', 'Average']].to_dict('records')

            return fig, table_data
    return {}, []

# Callback to update the interaction plot based on checklist and shell selection
@app.callback(
    Output('interaction-sros-plot', 'figure'),
    [Input('interaction-checklist', 'value'),
     Input('shell-dropdown', 'value'),
     State('upload-data', 'contents')]
)
def update_interaction_plot(selected_interactions, selected_shell, contents):
    if contents is not None:
        df = parse_contents(contents)
        print(df['time_difference_hours'])
        if df is not None:
            # Prepare a DataFrame for plotting interactions vs. sqs_id with timestamp
            plot_data = []
            for interaction in selected_interactions:
                shell_values = [item['sros'][interaction][selected_shell] for item in df.to_dict('records')]
                sqs_ids = [item['sqs_id'] for item in df.to_dict('records')]
                timestamps = [item['time_difference_hours'] for item in df.to_dict('records')]  # Add timestamps for each record
                
                plot_df = pd.DataFrame({
                    'sqs_id': sqs_ids,
                    'SRO Values': shell_values,
                    'Interaction': interaction,
                    'Timestamp (Hour)': timestamps  # Include timestamps in the DataFrame
                })
                
                plot_data.append(plot_df)
    
            # Combine the data into one DataFrame
            combined_plot_df = pd.concat(plot_data).sort_values(by='Timestamp (Hour)')
    
            # Create the line plot with markers and include timestamp in hover data
            fig = px.line(
                combined_plot_df, 
                # x='sqs_id', 
                x='Timestamp (Hour)',
                y='SRO Values', 
                color='Interaction', 
                hover_data={'sqs_id': True},  # Add timestamp to the hover data
                title=f'SRO Values for Selected Interactions ({selected_shell+1}st shell)', 
                markers=True
            )

            # Add a shaded region between y=-0.01 and y=0.01
            fig.add_shape(
                type="rect",
                xref="paper",  # Apply the shape across the entire x-axis range
                x0=0, x1=1,  # This covers the full range of the x-axis (timestamps)
                yref="y",  # Use 'y' axis for the vertical positioning
                y0=-0.02, y1=0.02,  # Set the bounds for the shaded region
                fillcolor="grey",  # You can choose a color here
                opacity=0.5,  # Set the transparency of the shaded region
                layer="above",  # Ensure the shaded region is drawn below the plot lines
                line_width=0  # No border around the shaded region
            )

            return fig
    return {}


if __name__ == '__main__':
    app.run_server(debug=True)
