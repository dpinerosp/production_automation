from dash import (Dash, 
                Input, 
                Output, 
                callback, 
                dash_table,
                html, 
                dcc)
import pandas as pd

from utils.constants import (daily_reports_processed, 
                            nominations_processed
                            )

from components.table import make_dash_table

data_nominations_processed = pd.read_csv(nominations_processed)

layout = html.Div([
    html.Div([
        # Contenedor para la selección del tipo de dato a trabajar y las operaciones
        # a realizar con ellos
        html.Div([
            # Seleccionar datos
            html.H2('Empresas'),
            html.Div(id="table-data-companies"),
            dcc.Input(id="add-company-input", type="text", placeholder="Nueva Empresa"), 
            html.Div([
                html.Button('Agregar', id='add-company', n_clicks=0, className="button add-button"),
                html.Button('Borrar', id='delete-company', n_clicks=0, className="button delete-button"),
            ], className="button-data-container")
            
        ], className='create_container five columns'),
        # Contenedor para graficar la participación en la producción por empresa
        html.Div([
            html.H2("Tipos de Crudo"),
            html.Div(id="table-oil-types"),
            dcc.Input(id="add-oil-input", type="text", placeholder="Nombre Crudo"), 
            dcc.Input(id="add-livianos-input", type="text", placeholder="Livianos (Si/No)?"), 
            html.Div([
                html.Button('Agregar', id='add-oil', n_clicks=0, className="button add-button"),
                html.Button('Borrar', id='delete-oil', n_clicks=0, className="button delete-button"),
            ], className="button-data-container")
        ], className='create_container seven columns'),
    ], className='row flex-display'),

    html.Div([
        # Contenedor para la selección del tipo de dato a trabajar y las operaciones
        # a realizar con ellos
        html.Div([
            # Seleccionar datos
            html.H2('Reportes Diarios Procesados'),
            make_dash_table(daily_reports_processed),
        ], className='create_container five columns'),
        # Contenedor para graficar la participación en la producción por empresa
        html.Div([
            html.H2('Nominaciones Procesadas'),
            make_dash_table(nominations_processed)
        ], className='create_container seven columns'),
    ], className='row flex-display'),
    
])