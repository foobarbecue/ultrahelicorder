from bokeh.server.server import Server
from numpy import random
import holoviews as hv
import pandas as pd

renderer = hv.renderer('bokeh')


def make_document(doc):
    seis_data = pd.DataFrame({'time': [1, 2, 3, 1, 2, 3, 1, 2, 3], 'counts': random.random(9),
                              'channel': ['LEH'] * 3 + ['CON'] * 3 + ['E1S'] * 3})
    plot_seis = lambda channel: hv.Curve(data=seis_data[seis_data.channel == channel])
    seis_dmap = hv.DynamicMap(plot_seis, kdims=hv.Dimension('channel', values=['LEH', 'CON', 'E1S']))
    layout = seis_dmap.layout('channel')
    doc.add_root(renderer.get_plot(layout).state)
    return doc

server = Server(make_document)
server.start()

if __name__ == '__main__':
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
