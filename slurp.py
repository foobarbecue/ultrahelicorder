"""
Run this with: bokeh serve --show hvhv_holoviews.py

It should open a browser window and stream seismic data to a plot.

"""

import time
import pandas as pd
import holoviews as hv
#from bokeh.layouts import layout
from threading import Thread
from tornado import gen
from functools import partial
from obspy.clients.seedlink.easyseedlink import create_client
import pytz

session_list = []

# Define DynamicMaps and display plot

#now = pd.datetime.now()
#time_extent = pd.Timedelta('1 hour')

#seis_dmap.redim.range(timestamp=(now - time_extent, now + time_extent))

#doc = renderer.server_doc(seis_dmap)

@gen.coroutine
def update(data, doc):
    doc.seis_stream.send(data)

def handle_trace(trace):
    # Have obspy give the times in POSIX format and convert using pandas' to_datetime. Couldn't find a way to use obspy
    # UTCDateTime directly.
    times = pd.to_datetime(trace.times('timestamp'), origin='unix', unit='s', utc=True)
    data = pd.DataFrame({'timestamp': times, 'counts': trace.data})

    for doc in session_list:
        doc.add_next_tick_callback(partial(update, data=data, doc=doc))
    print(trace)

def obspy_worker():
    client = create_client('rtserve.iris.washington.edu', on_data=handle_trace)
    client.select_stream('HV', 'WOOD', '???')
    client.run()

obspy_thread = Thread(target=obspy_worker)
obspy_thread.start()