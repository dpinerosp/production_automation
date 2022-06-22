from dash import (Dash, 
                Input, 
                Output, 
                callback, 
                dash_table,
                html, 
                dcc)
import pandas as pd

df = pd.read_csv("C:/Users/DPINEROS/OneDrive - GeoPark Limited/auto_geopark/reportes_procesados.csv")

layout_datos = html.Div([
    html.Div([
        # Contenedor para la selección del tipo de dato a trabajar y las operaciones
        # a realizar con ellos
        html.Div([
            # Seleccionar datos
            html.H2('Datos',
                    className='fix_label',
                    style={'color':'white', 'text-align':'center'}),
            dcc.Dropdown(options=['Reportes diarios', 'Nominaciones', 'Crudos'],
                        value='Reportes diarios',
                        clearable=False,
                        id='tipo-datos',
                        multi=False,
                        className='dash-dropdown'),
            # Crear botones para las diferentes operaciones con los datos
            html.H2('Operaciones',
                    className='fix_label',
                    style={'color':'white', 'text-align':'center'}),
            dcc.Upload(html.Button('Agregar', id='crear-val', n_clicks=0)),
            html.Button('Actualizar', id='actualizar-val', n_clicks=0),
            html.Button('Borrar', id='borrar-val', n_clicks=0),
        ], className='create_container three columns'),
        # Contenedor para graficar la participación en la producción por empresa
        html.Div([
            html.H3("Registros",
                    className='fix_label',
                    style={'color':'white', 'text-align':'center'}),
            dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], id='tbl')
        ], className='create_container nine columns'),
    ], className='row flex-display'),
    
])