from json import load
from dash import dcc, callback_context, Input, Output, State
from matplotlib.cbook import report_memory
import plotly.graph_objs as go

# Librerías para el tratamiento de datos
import numpy as np
import pandas as pd

from dash import html

from components.nominations_graph import graph_nominations_results
from pages.balance.balance_data import remove_entries_balance
from pages.nominations.tabs.tigana import tigana_nominations
from pages.nominations.tabs.livianos import livianos_nominations

from app import app

from components.nominations_graph import graph_accomplishment_factor

from pages.nominations.nominations_data import add_styles_nominations, daily_transported_oil_type, data_transported_nominated, filter_data_nominations, filter_data_transported, get_data_nominations_report, parse_contents, remove_entries_nominations, results_per_company

from utils.constants import (balance_data, 
                            header_nominations, 
                            nominations_processed, 
                            nominations_data,
                            months)
from utils.functions import filter_data_by_date, load_data, log_processed, verify_processed
from datetime import datetime

import os
from openpyxl import load_workbook

@app.callback(Output("files-to-process-nominations", "children"),
            [Input("subir-nominaciones", 'contents')],
            [State('subir-nominaciones', 'filename'),
            State('subir-nominaciones', 'last_modified')])
def update_daily_reports(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = list()
        # Nombres de los valores a guardar en el balance
        header = header_nominations
        for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
            try:
                df = parse_contents(c, n, d, header)
                if df['fecha'].dtypes == "datetime64[ns]": 
                    if verify_processed(n, nominations_processed):
                        new_data = remove_entries_nominations(nominations_data, n)
                        new_data.to_csv(nominations_data, index=False)
                    else:
                        log_processed(n, nominations_processed, ["fecha actualizacion", "fecha reporte"], "reporte")
                    children.append(html.P(n))
                    df.to_csv(nominations_data, mode="a", header=False, index=False)
                else:
                    children.append(html.Div(['There was an error processing this file.']))
                    
            except Exception as e:
                print(e)
                children.append(html.Div(['There was an error processing this file.']))

        return children

# Callback to download nominations report
# Callback for downloading button
@app.callback(Output("downloaded-report-nomination", "children"),
            [Input("descargar-info-nominaciones", "n_clicks"),
            Input("nomination-period", "start_date"),
            Input("nomination-period", "end_date")])
def download_report_nomination(n_clicks, start_date, end_date):
    df = load_data(balance_data)

    if not os.path.exists("../ReportesMensuales/Nominaciones/"):
        os.mkdir("../ReportesMensuales/Nominaciones/")

    date_nominations = datetime.strptime(start_date.split('T')[0], "%Y-%m-%d")
    report_name = f'Nominaciones {months[ date_nominations.month - 1]}-{date_nominations.year}.xlsx'
    data_nominations_report = get_data_nominations_report(start_date, end_date)
    averages = data_nominations_report.mean(axis=0, numeric_only=True)
    days = data_nominations_report.shape[0]

    r_geopark = results_per_company(data_nominations_report, "geopark", ["Jacana", "Tigana", "Livianos"])
    r_verano = results_per_company(data_nominations_report, "verano", ["Jacana", "Tigana", "Cabrestero", "Livianos"])

    data_nominations_report.loc[data_nominations_report.shape[0]] = ["Promedio"] + [round(v, 2) for v in averages.values]
    data_nominations_report.loc[data_nominations_report.shape[0]] = ["Días"] + [days] * 14
    
    if callback_context.triggered[0]['prop_id'] == "descargar-info-nominaciones.n_clicks":
        with pd.ExcelWriter(f"../ReportesMensuales/Nominaciones/{report_name}") as writer:
            data_nominations_report.to_excel(writer, index=False,
                                        sheet_name='Nominaciones')
            r_geopark.to_excel(writer, index=False,
                                        sheet_name='Resultados Geopark')
            r_verano.to_excel(writer, index=False,
                                        sheet_name='Resultados Verano')

         # Cargar el documento generado anteriormente y seleccionar la hoja activa
        wb = load_workbook(f'../ReportesMensuales/Nominaciones/{ report_name }')
        ws = wb["Nominaciones"]
        add_styles_nominations(ws, "FF0000", "000000")
        wb.save(f'../ReportesMensuales/Nominaciones/{ report_name }')
        wb.close()
        return html.P(f'Se ha descargado el archivo: { report_name }')

@app.callback(Output("graph-nominations-results", component_property="figure"),
            [Input("tabs-nominations", "value"),
            Input("nomination-period", "start_date"),
            Input("nomination-period", "end_date")])
def render_tabs_nominations(tab, start_date, end_date):
    data = load_data(balance_data)
    if tab == "tigana":
        return tigana_nominations(data, start_date, end_date)
    elif tab == "livianos":
        return livianos_nominations(data, start_date, end_date)

@app.callback(Output("production-factor", component_property="figure"),
            [Input("nomination-period", "start_date"),
            Input("nomination-period", "end_date"),
            Input("remitente-nominacion", "value")])
def update_production_factor(start_date, end_date, company):
     # Load nominations data
    data_nominations, data_transported = data_transported_nominated(start_date, end_date, company)
    
    type_oils_nominations = {f"nominado jacana {company.lower()}": "Jacana", 
                            f"nominado tigana {company.lower()}": "Tigana", 
                            f"nominado livianos {company.lower()}": "Livianos", 
                            f"nominado cabrestero {company.lower()}":"Cabrestero"}

    type_oils_transported = {f"JACANA ESTACION": "Jacana", 
                            f"TIGANA ESTACION": "Tigana", 
                            f"CABRESTERO - BACANO JACANA ESTACION": "Cabrestero", 
                            f"Livianos":"Livianos"}
    # Generación colores dummi
    colors = {"Jacana":"#FC7637", "Tigana": "#137ED2", "Livianos": "#A5A5A5", "Cabrestero": "#0A2A58"}
    date_nominations = datetime.strptime(start_date.split('T')[0], "%Y-%m-%d")

    new_name = company.capitalize()
    if new_name == "Verano":
        new_name = "Verano/Parex"

    title_graph = f"""
    Cumplimiento Nominación<br>
    Mes: {months[ date_nominations.month - 1]}.{date_nominations.year}<br>
    Remitente: {new_name}
    """
    return graph_accomplishment_factor(type_oils_nominations,
                                    type_oils_transported, 
                                    colors, 
                                    title_graph, 
                                    data_nominations, 
                                    data_transported)



