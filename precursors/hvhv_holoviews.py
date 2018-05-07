"""
Run this with: bokeh serve --show hvhv_holoviews.py

It should open a browser window and stream seismic data to a plot.

"""

import time
import pandas as pd
import holoviews as hv
from bokeh.io import curdoc
from bokeh.layouts import layout
from threading import Thread
from tornado import gen
from functools import partial

renderer = hv.renderer('bokeh')


# Set up StreamingDataFrame and add async callback
blank_data = pd.DataFrame({'counts': []})
seis_stream = hv.streams.Buffer(blank_data, length=100, index=False)

# Define DynamicMaps and display plot

seis_dmap = hv.DynamicMap(hv.Curve, streams=[seis_stream])
plot = renderer.get_plot(seis_dmap)

#doc = hv.renderer('bokeh').server_doc(seis_dmap)
doc = curdoc()
doc.add_root(layout([plot.state]))

from obspy.clients.seedlink.easyseedlink import create_client

@gen.coroutine
def update(data):
    seis_stream.send(data)

def handle_trace(trace):
    data = pd.DataFrame({'counts': trace.data})
    print(trace)
    time.sleep(1)
    doc.add_next_tick_callback(partial(update, data=data))

def obspy_worker():
    client = create_client('rtserve.iris.washington.edu', on_data=handle_trace)
    client.select_stream('HV', 'WOOD', 'EHZ')
    client.run()

obspy_thread = Thread(target=obspy_worker)
obspy_thread.start()