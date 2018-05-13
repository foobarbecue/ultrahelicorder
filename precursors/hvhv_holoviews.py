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

renderer = hv.renderer('bokeh')
blank_data = pd.DataFrame({'counts': [None], 'timestamp':[pd.datetime.now(tz=pytz.utc)]})
seis_stream = hv.streams.Buffer(blank_data, index=False, length=100000)

# Create a curve element with all options except for data
curve = partial(hv.Curve, kdims='timestamp', vdims='counts', label='HV.WOOD.EHZ')

# Define DynamicMaps and display plot
seis_dmap = hv.DynamicMap(curve, streams=[seis_stream])
now = pd.datetime.now()
time_extent = pd.Timedelta('1 hour')
seis_dmap = seis_dmap.options({'Curve': {'width': 1200}})
seis_dmap.redim.range(timestamp=(now - time_extent, now + time_extent))

doc = renderer.server_doc(seis_dmap)

@gen.coroutine
def update(data):
    seis_stream.send(data)

def handle_trace(trace):
    # Have obspy give the times in POSIX format and convert using pandas' to_datetime. Couldn't find a way to use obspy
    # UTCDateTime directly.
    times = pd.to_datetime(trace.times('timestamp'), origin='unix', unit='s', utc=True)

    data = pd.DataFrame({'timestamp': times, 'counts': trace.data})
    print(trace)
    doc.add_next_tick_callback(partial(update, data=data))

def obspy_worker():
    client = create_client('rtserve.iris.washington.edu', on_data=handle_trace)
    client.select_stream('HV', 'WOOD', '???')
    client.run()

obspy_thread = Thread(target=obspy_worker)
obspy_thread.start()