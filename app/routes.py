import json
import pickle
import plotly

from flask import render_template, request

from app import app
from scripts.preprocess_data import return_figures, get_ua_from_country


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    with open('data/data.pkl', 'rb') as file:
        data = pickle.load(file)

    with open('data/country_ua_dict.pkl', 'rb') as file:
        country_ua_dict = pickle.load(file)

    country_codes = data[0]
    job_options = data[1]

    # Parse the POST request countries list
    if (request.method == 'POST') and request.form:
        data = request.form.to_dict(flat=False)
        try:
            country_list = data['country_form']
            ua_list = get_ua_from_country(country_ua_dict, country_list)
        except:
            country_list = ['Guatemala', 'El Salvador', 'Honduras', 'Costa Rica', 'Panama']
            ua_list = get_ua_from_country(country_ua_dict, country_list)
        try:
            job_list = data['job_form']
        except:
            job_list = ['Data Analyst', 'Data Scientist', 'Mobile Developer', 'Software Engineer', 'Research Scientist']

        figures = return_figures(country_list, job_list, ua_list)

    # GET request returns all countries for initial page load
    else:
        country_list = ['Guatemala', 'El Salvador', 'Honduras', 'Costa Rica', 'Panama']
        ua_list = get_ua_from_country(country_ua_dict, country_list)
        jobs_list = ['Data Analyst', 'Data Scientist', 'Mobile Developer', 'Software Engineer', 'Research Scientist']
        figures = return_figures(country_list, jobs_list, ua_list)

    # plot ids for the html id tag
    ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]

    # Convert the plotly figures to JSON for javascript in html template
    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)
    #print(figuresJSON)

    return render_template('index.html', ids=ids,
                           figuresJSON=figuresJSON,
                           all_countries=country_codes,
                           all_jobs=job_options)
