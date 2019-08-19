import bokeh
from bokeh.server.server import Server
import slurp
from bokeh.layouts import layout
from bokeh.settings import settings
import holoviews as hv
import pandas as pd
import numpy as np
import pytz
from jinja2 import Template
# Template and javascript ignominiously pasted from scroller.js until I figure out a multi-file framework
template = Template("""
<html>
{{ bokeh_css }}
{{ bokeh_js }}
<script>
function waitForAddedNode(params) {
    new MutationObserver(function(mutations) {
        var el = document.getElementsByClassName(params.class).length;
        if (el) {
            console.log(el)
            this.disconnect();
            params.done(el);
        }
    }).observe(params.parent || document, {
        subtree: !!params.recursive,
        childList: true
    });
}

waitForAddedNode({
    class: "bk-canvas",
    done: onload,
    recursive: true,
    parent: document.body
});

function onload(){
    function findFigure(){
        var figs = [];
        for (obj in Bokeh.documents[0]._all_models) {
            if (Bokeh.documents[0]._all_models[obj].type == "Plot"){
                figs.push(Bokeh.documents[0]._all_models[obj]);
            }
        }
        return figs
    }

    figs = findFigure();
    x_time_extent = 500000; // Should be argument?
    time_delay = 50000;
    function setTimeRange() {
        var now = Date.now();
        for (fig_ind in figs){
            var fig = figs[fig_ind];
            fig.x_range.setv({'start': now - x_time_extent, 'end':Date.now()-time_delay});
            //fig.y_range.setv({'start':-100000, 'end':100000});
        }
    }
    setInterval(setTimeRange,100)
}

</script>
{{ plot_script }}
<body>
<h1>Live seismic display concept</h1>
By <a href=https://aaroncurt.is>Aaron Curtis</a>
<br/>
<a href=https://github.com/foobarbecue/ultrahelicorder>source code is here</a>
{{ plot_div }}
</body> 
</html>
""")

renderer = hv.renderer('bokeh')


def plot_seis(data, channel):
    curve = hv.Curve(data=data[data.channel == channel],
                     kdims=['timestamp'], vdims='counts')
    return curve

def make_document(doc):
    blank_data = pd.DataFrame({'timestamp': [pd.datetime.now(tz=pytz.utc)]*4,
                               'counts': [np.nan]*4,
                               'channel': ['HV.ALEP..EHE',
                                           'HV.ALEP..EHN',
                                           'HV.AHUD..EHE',
                                           'HV.AHUD..EHN',]})
    # blank_data = pd.DataFrame({'channel':[],'counts':[],'timestamp':[]},
    #                           columns=['channel','counts','timestamp'])
    # blank_data.astype({'counts': 'float64','timestamp': 'datetime64[ns]', 'channel':str})
    # blank_data.set_index('timestamp', inplace=True)
    seis_stream = hv.streams.Buffer(blank_data, index=False, length=1000000)

    # Triggers https://github.com/ioam/holoviews/issues/2705
    seis_dmap = hv.DynamicMap(plot_seis, streams=[seis_stream], kdims=[hv.Dimension('channel',
                                    values=['HV.ALEP..EHE',
                                           'HV.ALEP..EHN',
                                           'HV.AHUD..EHE',
                                           'HV.AHUD..EHN'])])
    seis_dmap = seis_dmap.options({'Curve': {'apply_xrange': False, 'apply_yrange': True,
                                             'width': 1200, 'shared_axes':False}})
    # layout = seis_dmap
    layout = seis_dmap.layout(['channel']).cols(1)
    doc.seis_stream = seis_stream
    # Add this user to the list of sessions to generate new data callbacks in slurp.py
    doc_root = renderer.get_plot(layout).state
    doc.template = template
    doc.add_root(doc_root)
    return doc


server = Server(make_document, port=8121, host='localhost', allow_websocket_origin=["*"])
slurp.bokeh_tornado = server._tornado
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:8121/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
