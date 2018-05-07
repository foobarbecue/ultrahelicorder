import time
import pandas as pd
import holoviews as hv
from obspy.clients.seedlink.easyseedlink import create_client

#This almost works, but client.run seems to block bokeh

hv.extension('bokeh')

def handle_trace(trace):
    data = pd.DataFrame({'counts': trace.data})
    print(trace)
    time.sleep(1)
    seis_stream.send(data)


client = create_client('rtserve.iris.washington.edu', on_data=handle_trace)
client.select_stream('HV','WOOD','EHZ')

# Set up StreamingDataFrame and add async callback
blank_data = pd.DataFrame({'counts': [1,3,5,6]})
seis_stream = hv.streams.Buffer(blank_data, length=100, index=False)

# Define DynamicMaps and display plot

seis_dmap = hv.DynamicMap(hv.Curve, streams=[seis_stream])

# Render plot and attach periodic callback

doc = hv.renderer('bokeh').server_doc(seis_dmap)
seis_stream.send(pd.DataFrame({'counts': [8, 15, 12, 13]}))
time.sleep(3)
client.run()