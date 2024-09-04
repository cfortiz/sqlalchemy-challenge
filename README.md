# Module 10 - Advanced SQL: SQLAlchemy Challenge

Use Python and SQLAlchemy to do a basic climate analysis and data exploration of
your climate database.

## Files

* `README.md`: This file.
* `SurfsUp/climate_starter.ipynb`: Jupyter notebook with code for hawaii climate
  analysis.
* `SurfsUp/app.py`: Flask rest service code.
* `SurfsUp/Resources/hawaii*`: SQLite db and CSV data files (provided).

## Notes

Because of the order of the excercises, the jupyter notebook does not leverage
access to the rest service to implement its functionality.  It wasn't clear
whether the individual observations were for overlapping areas or not.  Under
the assumption that observations in the measurements table were for different
non-overlapping areas, measurement sums were computed in most cases, grouped by
date, unless otherwise specified as part of the challenge.
