#Collects seismic data and sends it to streams attached to bokeh documents that are being served by serve.py

import pandas as pd
from threading import Thread
from tornado import gen
from functools import partial
from obspy.clients.seedlink.easyseedlink import create_client
import xml.etree.ElementTree as ET
import asyncio

bokeh_tornado = None

async def update(data, doc):
    doc.seis_stream.send(data)

def handle_trace(trace):
    # Have obspy give the times in POSIX format and convert using pandas' to_datetime. Couldn't find a way to use obspy
    # UTCDateTime directly.
    times = pd.to_datetime(trace.times('timestamp'), origin='unix', unit='s', utc=True)
    data = pd.DataFrame({'timestamp': times, 'counts': trace.data, 'channel': trace.id})

    for session in bokeh_tornado.get_sessions('/'):
        session.document.add_next_tick_callback(partial(update, data=data, doc=session.document))

def obspy_worker(network='HV'):
    client = create_client('rtserve.iris.washington.edu', on_data=handle_trace)
    station_xml = client.get_info('STREAMS') # should be async
    station_xml = ET.fromstring(station_xml)
    stations = station_xml.findall("./*/[@network='{}']".format(network))
    for station in stations[0:3]:
        station_name = station.attrib['name']
        channels = station.getchildren()
        for channel in channels:
            channel_name = channel.attrib['seedname']
            client.select_stream(network, station_name, channel_name)
    client.run()

obspy_thread = Thread(target=obspy_worker)
obspy_thread.start()
