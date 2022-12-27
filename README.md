# Teleport Data Dashboard

This is the repository of a dashboard that uses the Teleport Open API to request information about job salaries and quality of life of different cities and countries. You can see the working data dashboard https://data-dashboard.onrender.com/

## Getting Started

If you want to run this dashboard locally you can do it by going inside the root folder of this repository and type the following commands:

```bash
pipenv install
pipenv run gunicorn --bind 0.0.0.0:3000 app:app
```

Notice that you will need to have `pipenv` installed.

### Prerequisites

For development purposes the following packages are required:

* `flask 2.1.3`
* `gunicorn`
* `requests`
* `numpy 1.21.6`
* `pandas  1.2.4`
* `plotly 5.11.0`

## Authors

- **Manuel Rios**
  
   https://github.com/mriosrivas

## License

This project is licensed under MIT licence.
