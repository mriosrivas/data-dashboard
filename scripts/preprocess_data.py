import requests
import pandas as pd
import plotly.graph_objs as go


# Get Urban Area from Country
def get_ua_from_country(country_ua_dict, country_list):
    ua_list = []
    for country in country_list:
        try:
            ua_list.append(country_ua_dict[country][0])
        except:
            pass
    return ua_list


# Get Urban City respective Country
def get_ua_country(ua_id):
    r = requests.get(f'https://api.teleport.org/api/urban_areas/{ua_id}/')
    ua_datail = r.json()
    return ua_datail['_links']['ua:countries'][0]['name']


# Get Job Dictionary
def get_job_dictionary():
    return dict(get_country_salary('iso_alpha2:US')[['job.title', 'job.id']].values)


# Get Country Dictionary
def get_country_dict():
    r = requests.get('https://api.teleport.org/api/countries/')
    countries = r.json()
    df_countries = pd.json_normalize(countries['_links']['country:items'])
    df_countries['iso2'] = df_countries['href'].str.split('/', expand=True)[[5]]
    return dict(zip(df_countries['iso2'].str.split(':', expand=True)[1].values, df_countries['name'].values))


# Get Country ISO
def get_country_iso(country_list):
    r = requests.get('https://api.teleport.org/api/countries/')
    countries = r.json()
    df_countries = pd.json_normalize(countries['_links']['country:items'])
    df_countries['iso2'] = df_countries['href'].str.split('/', expand=True)[[5]]
    country_iso = df_countries[df_countries['name'].isin(country_list)]['iso2'].values
    return country_iso


# Get Country Salary
def get_country_salary(iso):
    link = f'https://api.teleport.org/api/countries/{iso}/salaries/'
    r = requests.get(link)
    salaries = r.json()
    return pd.json_normalize(salaries['salaries'])


# Get Job Salary by Country
def get_job_salary(jobs_df, jobs_list):
    #print(jobs_list)
    return jobs_df[jobs_df['job.id'].isin(jobs_list)].reset_index()


# Get Job Data
def get_job_data(country_list, jobs_list):
    country_iso = get_country_iso(country_list)
    countries = []
    salaries = []

    for iso in country_iso:
        countries.append(iso.split(':')[1])
        jobs_df = get_country_salary(iso)
        salary_df = get_job_salary(jobs_df, jobs_list)
        salary = salary_df['salary_percentiles.percentile_50'].values
        salaries.append(salary)

    job_dict = dict(jobs_df[['job.id', 'job.title']].values)
    return pd.DataFrame(dict(zip(countries, salaries)), index=list(salary_df['job.id'].values)), job_dict


def get_figure_one(country_dict, country_list, jobs_list):
    # country_list = ['Guatemala', 'El Salvador', 'Honduras', 'Costa Rica', 'Nicaragua', 'Panama']
    # jobs_list = ['DATA-SCIENTIST']
    data, job_dict = get_job_data(country_list, jobs_list)

    country_dict_list = []
    for c in data.columns.values:
        country_dict_list.append(country_dict[c])

    graph_one = [go.Bar(
        x=list(country_dict_list),
        y=list(data.values[0].round(1)),
    )]

    layout_one = dict(title=f'{job_dict[jobs_list[0]]} Job Comparison Between Countries',
                      xaxis=dict(title='Country', ),
                      yaxis=dict(title='Medium Salary per Year in USD'),
                      )

    return dict(data=graph_one, layout=layout_one)


def get_figure_two(country_list, jobs_list):
    # country_list = ['Guatemala']
    # jobs_list = ['DATA-ANALYST', 'DATA-SCIENTIST', 'MOBILE-DEVELOPER', 'SOFTWARE-ENGINEER', 'RESEARCH-SCIENTIST']
    data, job_dict = get_job_data(country_list, jobs_list)

    job_dict_list = []
    for j in data.index.values:
        job_dict_list.append(job_dict[j])

    graph_one = [go.Bar(
        x=job_dict_list,
        y=list(data.values.flatten().round(1)),
    )]

    layout_one = dict(title=f'Different Job Market in {country_list[0]}',
                      xaxis=dict(title='Job', ),
                      yaxis=dict(title='Medium Salary per Year in USD'),
                      )

    return dict(data=graph_one, layout=layout_one)


# Get Urban Areas Dictionary
def get_ua_id_dict():
    r = requests.get('https://api.teleport.org/api/urban_areas/')
    urban_areas = r.json()
    df_urban_areas = pd.json_normalize(urban_areas['_links']['ua:item'])
    df_urban_areas['ua_id'] = df_urban_areas['href'].str.split('/', expand=True)[5]
    return dict(zip(df_urban_areas['name'].values, df_urban_areas['ua_id'].values))


# Get Single Urban Area Score
def get_single_urban_areas_scores(ua_id):
    # ua_id = 'slug:guatemala-city'
    ua = ua_id.split(':')[1]
    r = requests.get(f'https://api.teleport.org/api/urban_areas/{ua_id}/scores/')
    scores = r.json()
    df_scores = pd.json_normalize(scores['categories'])
    return df_scores.drop(columns=['color']).rename(columns={'name': 'category', 'score_out_of_10': ua})


# Get Urban Area Score
def get_urban_scores(ua_ids):
    for i, ua_id in enumerate(ua_ids):
        if i == 0:
            last_urban_areas_scores = get_single_urban_areas_scores(ua_id)
        else:
            last_urban_areas_scores = pd.merge(last_urban_areas_scores, get_single_urban_areas_scores(ua_id))
    return last_urban_areas_scores


def get_figure_radial(ua_id_dict, ua_list, categories, title):
    # ua_list = ['Berlin', 'Buenos Aires', 'Cardiff', 'Copenhagen']
    #print(f'ua_list = {ua_list}')
    ua_id_list = [ua_id_dict[ua] for ua in ua_list]
    ua_list = [ua_id.split(':')[1] for ua_id in ua_id_list]

    # human_quality_categories = ['Housing', 'Cost of Living', 'Safety', 'Healthcare',
    #                            'Education', 'Environmental Quality']

    urban_scores = get_urban_scores(ua_id_list)
    category_scores = urban_scores[urban_scores['category'].isin(categories)]

    graph = []

    theta = list(category_scores['category'].values)
    theta.append(theta[0])

    for ua in ua_list:
        r = list(category_scores[ua].values)
        r.append(r[0])

        graph.append(go.Scatterpolar(
            r=r,
            theta=theta,
            fill='toself',
            name=ua
        ))

    layout = dict(title=title,
                  radialaxis=dict(visible=True, range=[0, 15]),
                  showlegend=True)

    return dict(data=graph, layout=layout)


def return_figures(country_list, jobs_list, ua_list):
    # Get dictionaries
    country_dict = get_country_dict()
    ua_id_dict = get_ua_id_dict()
    job_dict = get_job_dictionary()

    #print(f'{jobs_list}')

    jobs_list_from_dict = []
    for job in jobs_list:
        jobs_list_from_dict.append(job_dict[job])

    # Lists
    #print(f'Country list is {country_list}')
    # jobs_list = ['DATA-ANALYST', 'DATA-SCIENTIST', 'MOBILE-DEVELOPER', 'SOFTWARE-ENGINEER', 'RESEARCH-SCIENTIST']
    # ua_list = ['Berlin', 'Buenos Aires', 'Cardiff', 'Copenhagen']

    # Figure one parameters
    jobs = [jobs_list_from_dict[0]]

    # Figure two parameters
    country = [country_list[0]]

    # Figure three parameters
    human_quality_categories = ['Housing', 'Cost of Living', 'Safety', 'Healthcare',
                                'Education', 'Environmental Quality']

    # Figure four parameters
    business_categories = ['Startups', 'Venture Capital', 'Business Freedom', 'Economy', 'Taxation']

    figures = [get_figure_one(country_dict, country_list, jobs),
               get_figure_two(country, jobs_list_from_dict),
               get_figure_radial(ua_id_dict, ua_list, human_quality_categories,
                                 'Life Quality Parameters by Urban Area'),
               get_figure_radial(ua_id_dict, ua_list, business_categories,
                                 'Business Quality Parameters by Urban Area')]

    return figures


if __name__ == "__main__":
    print(return_figures())
