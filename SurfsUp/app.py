# Import the dependencies.
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

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
@app.route('/')
def homepage():
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    oldest_date_subquery = session.query(
        func.date(func.max(Measurement.date), '-12 months')
    ).scalar_subquery()
    query = session.query(Measurement.date, func.sum(Measurement.prcp).label('prcp'))\
        .filter(Measurement.prcp.is_not(None))\
        .filter(Measurement.date >= oldest_date_subquery)\
        .group_by(Measurement.date)\
        .order_by(Measurement.date)
    measurements = query.all()
    precipitation = {
        measurement.date: measurement.prcp
        for measurement in measurements
    }
    return jsonify(precipitation)


@app.route('/api/v1.0/stations')
def stations():
    query = session.query(Station)
    stations = [
        dict(
            id=station.id,
            station=station.station,
            name=station.name,
            latitude=station.latitude,
            longitude=station.longitude,
            elevation=station.elevation,
        )
        for station in query.all()
    ]
    return jsonify(stations)


@app.route('/api/v1.0/tobs')
def tobs():
    # Query for the most active station
    query = session.query(
            Station.station,
            func.count(func.distinct(Measurement.id)).label('observations'),
        )\
        .filter(Measurement.station == Station.station)\
        .filter(Measurement.tobs.is_not(None))\
        .group_by(Station.station)\
        .order_by(desc('observations'))\
        .limit(1)

    most_active_station = query.first()

    # Make subquery for oldest date for 12 months search
    oldest_date_subquery = session.query(
       func.date(func.max(Measurement.date), '-12 months')
    )\
    .filter(Measurement.station == most_active_station.station)\
    .scalar_subquery()
    
    # Query for temp observations of most active station for last 12 months
    query = session.query(
            Measurement.date,
            func.sum(Measurement.tobs).label('tobs'),
        )\
        .filter(Measurement.tobs.is_not(None))\
        .filter(Measurement.date >= oldest_date_subquery)\
        .group_by(Measurement.date)\
        .order_by(Measurement.date)
    
    measurements = query.all()
    tobs = [
        dict(
            date=measurement.date,
            tobs=measurement.tobs,
        )
        for measurement in measurements
    ]
    
    return jsonify(tobs)


@app.route('/api/v1.0/<start>/<end>')
def temps_from_start_to_end(start, end=None):
    if end is not None and start > end:
        start, end = end, start  # Swap if not in order
    
    query = session.query(
            func.min(Measurement.tobs).label('tmin'),
            func.max(Measurement.tobs).label('tmax'),
            func.avg(Measurement.tobs).label('tavg'),
        )\
        .filter(Measurement.tobs.is_not(None))\
        .filter(Measurement.date >= start)
    
    if end is not None:
        query = query.filter(Measurement.date <= end)

    temps = [
        dict(tmin=temp.tmin, tmax=temp.tmax, tavg=temp.tavg)
        for temp in query.all()
    ]
    
    return jsonify(temps)


@app.route('/api/v1.0/<start>')
def temps_from_start(start):
    return temps_from_start_to_end(start)


if __name__ == '__main__':
    app.run(debug=True)
