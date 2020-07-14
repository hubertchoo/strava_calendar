# Strava Calendar

Project to make calendar visualisations from Strava data. More information can be found below.

Reason for the separate creation of this git repository is due to the package taken from github.com/colcarroll/strava_calendar.git being unable to work. 

Files from bulk export from Strava comes in .gpx file format instead of the .gzip file format handled in the original package, which could be as sensor data from Garmins etc may be exported in .gzip but phone GPS data is exported in .gpx.

Changes in the code are to account for handling of data provided in the .gpx file format.

Further commit has implemented the option to display daily mileage in the calendar.

Below is the original README at github.com/colcarroll/strava_calendar.git
_______________________________________________________________________________________________________________________________
# Strava Calendar

A project to make beautiful visualizations from Strava data. Heavily inspired by the [wonderful R library by Markus Volz](https://github.com/marcusvolz/strava).

## Install

```python
pip install git+git://github.com/colcarroll/strava_calendar.git
```

## Use

First download your data from Strava (see below for how). The last step gives you a `zip_path` to the archive with all the data. ***This is quite slow the first time you run it for a zip file and year (~5mins), but quite fast after that (~5s).***

```python
from strava_calendar import plot_calendar

plot_calendar(zip_path=zip_path, year=2018)
```

![default plot](https://github.com/colcarroll/strava_calendar/blob/master/samples/sample_1.png "Default plot")


You can control how many columns there are, the spacing between months and columns, and the label in the top left:

```python
plot_calendar(zip_path=zip_path, year=2017, n_cols=6, month_gap=1.5, col_gap=1, label='')
```

![custom plot](https://github.com/colcarroll/strava_calendar/blob/master/samples/sample_2.png "Custom Plot")

You can also plot a single column of weeks, which is pleasant.

```python
plot_calendar(zip_path=zip_path, year=2017, n_cols=1)
```

![strip plot](https://github.com/colcarroll/strava_calendar/blob/master/samples/sample_3.png "Strip Plot")

If you want to write more custom code, you can give that a shot, too:

```python
import datetime

import matplotlib.pyplot as plt

from strava_calendar import Plotter, get_data

data = get_data(zip_path, 'running', datetime.datetime(2018, 1, 1), datetime.datetime(2019, 1, 1))

plotter = Plotter(data)

fig, ax = plt.subplots(figsize=(9, 6))

fig, ax, offset = plotter.plot_month(year=2018, month=6, fig=fig, ax=ax)
ax.text(0, offset + 4.2, 'Weeee!', fontdict={'fontsize': 32, 'fontweight': 'heavy'}, alpha=0.5)
```

![month plot](https://github.com/colcarroll/strava_calendar/blob/master/samples/sample_4.png "Month Plot")

## Bulk export from Strava

The process for downloading data is also [described on the Strava website](https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export#Bulk):

1. After logging into Strava, select "[Settings](https://www.strava.com/settings/profile)" from the main drop-down menu at top right of the screen.
2. Select "[My Account](https://www.strava.com/account)" from the navigation menu to the left of the screen.
3. Under the "[Download or Delete Your Account](https://www.strava.com/athlete/delete_your_account)" heading, click the "Get Started" button.
4. Under the "Download Request", heading, click the "Request Your Archive" button. ***Be careful not to delete your account here!***
5. The archive takes a while to be sent. Download the zipped file to a location whose path you know.
