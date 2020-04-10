from app import app
from flask import render_template, request, redirect, url_for, make_response, send_file
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import os
import matplotlib.pyplot as plt
import pandas as pd
import random
from io import StringIO
import json
import plotly
import plotly.graph_objs as go
import numpy as np
import logging
import requests
from pandas import json_normalize 

@app.route('/', methods=["POST", "GET"])
@app.route('/index')
def index():
    if request.method == "POST":
        uf = request.form["select_uf"]
        muni = request.form["select_municipio"]
        bar = create_plot(uf, muni)
    logging.info(' logged in successfully')
    return render_template("index.html", content=get_ufs(), plot='')

@app.route('/output_plot', methods=['GET', 'POST'])
def change_features():

    logging.warning("Passou")
    uf = request.json['select_uf']
    muni = request.json["select_municipio"]

    dados = get_data(uf, muni);
    print(isinstance(dados, str))
    if isinstance(dados, str):
        print('entrou')
        # return dados
        from flask import jsonify, make_response
        data = {'message': 'Created', 'code': 'SUCCESS'}
        return make_response(jsonify(dados), 201)
    else:
        graphJSON = create_plot(dados)
        return graphJSON

def get_ufs():
    print('hello')
    import requests

    response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados")
    results = response.json()
    # ret = []
    # for x in results:
    #     ret.append(x['sigla'])
    #     ret.append(x['sigla'])
    # ret.sort()
    results = sorted(results, key = lambda i: i['sigla']) 
    return results;

def get_data(uf, muni):
    print('get_data')

    response = requests.get("https://brasil.io/api/dataset/covid19/caso/data?is_last=False&city_ibge_code="+muni)

    dados = response.json()['results']
    logging.info(str(dados))

    df = json_normalize(dados)
    print(df)
    if df.empty:
        return 'Não temos dados para esta região.'

    return df
def create_plot(df):

    print('create_plot')
    print(df)
    print(type(df))
        
    data = df.date.tolist() 
    confirmados = df.confirmed.tolist() 
    
    data.reverse()
    confirmados.reverse()

    # trace = go.Scatter(x = data,
    #                 y = confirmados,
    #                 mode = 'markers')
    # data = [trace]
    # graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    # xaxis_title="Data",
    # yaxis_title="Casos confirmados",
    # trace = go.Scatter(x=data, y=confirmados, xaxis_title = 'Data', yaxis_title= 'Casos confirmados')

    fig = go.Figure(go.Scatter(
    y=confirmados,
    x=data))

    fig.update_layout(
        title={
            'text': "Casos confirmados 2020",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        annotations=[
            dict(
                x=0.5,
                y=-0.15,
                showarrow=False,
                text="Data",
                xref="paper",
                yref="paper"
            ),
            dict(
                x=-0.09,
                y=0.5,
                showarrow=False,
                text="Número de casos",
                textangle=-90,
                xref="paper",
                yref="paper"
            )
        ],
        xaxis_tickformat = '%d/%m',
        width=1000,
        height=500,
    )

    data = fig
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON