#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt


# # Get Country ISO

# In[2]:


def get_country_iso(country_list):
    r = requests.get('https://api.teleport.org/api/countries/')
    countries = r.json()
    df_countries = pd.json_normalize(countries['_links']['country:items'])
    df_countries['iso2'] = df_countries['href'].str.split('/', expand=True)[[5]]
    country_iso = df_countries[df_countries['name'].isin(country_list)]['iso2'].values
    return country_iso


# # Get Country Salary

# In[3]:


def get_country_salary(iso):
    link = f'https://api.teleport.org/api/countries/{iso}/salaries/'
    r = requests.get(link)
    salaries = r.json()
    return pd.json_normalize(salaries['salaries'])


# # Get Job Salary by Country

# In[4]:


def get_job_salary(jobs_df, jobs_list):
    return jobs_df[jobs_df['job.id'].isin(jobs_list)].reset_index()


# # Get Job Data

# In[5]:


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

    return pd.DataFrame(dict(zip(countries, salaries)), index=list(salary_df['job.id'].values))


# # Plot 1: Same Job Around the World

# In[6]:


#country_list = ['Guatemala', 'Spain','Russia']
#jobs_list = ['ELECTRICAL-ENGINEER', 'CHEF']

country_list = ['Guatemala', 'Spain','Russia', 'United States']
jobs_list = ['ELECTRICAL-ENGINEER', 'DATA-SCIENTIST']

country_iso = get_country_iso(country_list)
country_iso


# In[7]:


data = get_job_data(country_list, jobs_list)
data


# In[8]:


key = 'ELECTRICAL-ENGINEER'
sns.barplot(x=data.loc[key].index, y=data.loc[key].values)
plt.show()


# # Plot 2: Jobs Compared in your Country

# In[14]:


get_country_salary('iso_alpha2:GT')


# In[27]:


#country_list = ['Guatemala', 'Spain','Russia']
#jobs_list = ['ELECTRICAL-ENGINEER', 'CHEF']

country_list = ['Guatemala']
jobs_list = ['DATA-ANALYST', 'DATA-SCIENTIST', 'MOBILE-DEVELOPER', 'SOFTWARE-ENGINEER', 'RESEARCH-SCIENTIST']

country_iso = get_country_iso(country_list)
country_iso


# In[28]:


data = get_job_data(country_list, jobs_list)
data


# In[30]:


sns.barplot(x=data.index.values, y=data.values.flatten())
plt.show()


# In[ ]:




