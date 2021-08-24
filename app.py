## Hints
# You will need to join the station and measurement tables for some of the queries.
# Use Flask `jsonify` to convert your API data into a valid JSON response object.
%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect = True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# `/` Home page.  List all routes that are available.
@app.route("/")
def welcome():
    test = (f"Welcome to the Hawaii Climate Analysis API!"<br/>
    f"Available Data:"<br/>
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>""
    f"/api/v1.0/<start>/<end>")

# `/api/v1.0/precipitation`
    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    # Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    # Calculate the date one year from the last date in data set.
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    Year = int(latest_date[0][0:4])
    Month = int(latest_date[0][5:7])
    Day = int(latest_date[0][8:])

    latest_date_ref = datetime(Year, Month, Day)
    latest_date_minus_year = latest_date_ref - timedelta(days = 365)

    # Perform a query to retrieve the data and precipitation scores
    # Sort the dataframe by date
    latest = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= latest_date_minus_year).\
        order_by(Measurement.date).all()

    latest_df = pd.DataFrame(latest)
    latest_df['prcp'] = latest_df['prcp'].fillna(0)

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in latest}
    return jsonify(precip)

# `/api/v1.0/stations`
    # Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Design a query to return a list of stations
    stations = session.query(Station.station).all()
    
    # Convert to a list
    stations_list = list(np.ravel(stations))
    return jsonify(stations_list = stations_list)

# `/api/v1.0/tobs`
    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    Year = int(latest_date[0][0:4])
    Month = int(latest_date[0][5:7])
    Day = int(latest_date[0][8:])

    latest_date_ref = datetime(Year, Month, Day)
    latest_date_minus_year = latest_date_ref - timedelta(days = 365)

    # Design a query to retrieve the last 12 months of temperature observation data (TOBS) for the primary station.
    temps = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= latest_date_minus_year).all()

    # Convert to a list
    temps_list = list(np.ravel(temps))
    return jsonify(temps_list = temps_list)

# `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
        # for a given start or start-end range.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dates(start = None, end = None):
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and 
        # equal to the start date.


    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates 
        # between the start and end date inclusive.


if __name__ = '__main__':
    app.run()