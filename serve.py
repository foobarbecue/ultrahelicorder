from bokeh.server.server import Server
import slurp
from bokeh.layouts import layout
from bokeh.models.callbacks import CustomJS
#from bokeh.plotting import curdoc
import holoviews as hv
from functools import partial
import pandas as pd
import pytz


renderer = hv.renderer('bokeh')

# need to add some CustomJS that runs
# Bokeh.document[0].correct_model.x_range.setv({"start": a_while_ago, "end": a_while_inthefuture})

def make_document(doc):
    # Create a curve element with all options except for data
    blank_data = pd.DataFrame({'counts': [None], 'timestamp': [pd.datetime.now(tz=pytz.utc)]})
    seis_stream = hv.streams.Buffer(blank_data, index=False, length=100000)
    def plot_seis(data):
        curve = hv.Curve(data=data, kdims='timestamp', vdims='counts', label='HV.WOOD.EHZ')
        return curve
    seis_dmap = hv.DynamicMap(plot_seis, streams=[seis_stream])
    seis_dmap = seis_dmap.options({'Curve': {'width': 1200}})
    #seis_dmap = seis_dmap.redim.range(timestamp=(0,10000))
    #seis_dmap = seis_dmap.opts({'norm':{'framewise':'True'}})
    seis_dmap.redim.range(timestamp=(1426366659275,1526366659275))
    plot = renderer.get_plot(seis_dmap)
    print(plot.id)

    def set_x_range():
        print('setting xrange')
        now = pd.datetime.now()
        time_extent = pd.Timedelta('1s')
        plot.x_range = (now - time_extent, now + time_extent)

    doc.add_root(layout([plot.state]))
    doc.seis_stream = seis_stream
     # this only happens once
    slurp.session_list.append(doc)
    return doc


server = Server(make_document, port=5008)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()