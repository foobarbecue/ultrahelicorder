from bokeh.server.server import Server
import slurp
from bokeh.layouts import layout
from bokeh.plotting import curdoc
import holoviews as hv
from functools import partial
import pandas as pd
import pytz

renderer = hv.renderer('bokeh')

def make_document(doc):

    # Create a curve element with all options except for data
    blank_data = pd.DataFrame({'counts': [None], 'timestamp': [pd.datetime.now(tz=pytz.utc)]})
    seis_stream = hv.streams.Buffer(blank_data, index=False, length=100000)
    curve = partial(hv.Curve, kdims='timestamp', vdims='counts', label='HV.WOOD.EHZ')
    seis_dmap = hv.DynamicMap(curve, streams=[seis_stream])
    seis_dmap = seis_dmap.options({'Curve': {'width': 1200}})
    plot = renderer.get_plot(seis_dmap)
    doc.add_root(layout([plot.state]))
    doc.seis_stream = seis_stream
    slurp.session_list.append(doc)
    return doc


server = Server(make_document, port=5008)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()