## Hints
# You will need to join the station and measurement tables for some of the queries.
# Use Flask `jsonify` to convert your API data into a valid JSON response object.

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
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# add as conn, with this argument: check_same_thread=False

# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect = True)

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
    test = (f"Welcome to the Hawaii Climate Analysis API!<br/>"
    f"Available Data:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<startdate>/<enddate>")
    return(test)

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

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in latest}
    return jsonify(precip)

# `/api/v1.0/stations`
    # Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Design a query to return a list of stations
    stations_result = session.query(Station.station).all()
    
    # Convert to a list
    stations_list = list(np.ravel(stations_result))
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
    tobs_results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= latest_date_minus_year).all()

    # Convert to a list
    tobs_list = list(np.ravel(tobs_results))
    return jsonify(tobs_list = tobs_list)

# `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
        # for a given start or start-end range.
@app.route("/api/v1.0/<startdate>")
@app.route("/api/v1.0/<startdate>/<enddate>")
def dates(startdate = None, enddate = None):
    # to pass in flask
    temp_calc = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    startdate = datetime(startdate)
    enddate = datetime(enddate)
    
    if not enddate:
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and 
        # equal to the start date.
        temp_data = session.query(*temp_calc).filter(Measurement.date >= startdate).all()
    
    else:
        # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates 
            # between the start and end date inclusive.
        temp_data = session.query(*temp_calc).filter(Measurement.date >= startdate).\
            filter(Measurement.date <= enddate).all()
    
    # Convert to a list
    temp_data_list = list(np.ravel(temp_data))
    return jsonify(temp_data_list = temp_data_list)
 
if __name__ == '__main__':
    app.run()