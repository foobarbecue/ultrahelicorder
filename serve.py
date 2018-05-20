from bokeh.server.server import Server
import slurp
from bokeh.layouts import layout
import holoviews as hv
import pandas as pd
import pytz
from jinja2 import Template
# Template and javascript ignominiously pasted from scroller.js until I figure out a multi-file framework
template = Template("""
</html>
<script src="http://cdn.pydata.org/bokeh/release/bokeh-0.12.15.js"></script>
<script src="http://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.15.js"></script>
<script src="http://cdn.pydata.org/bokeh/release/bokeh-tables-0.12.15.js"></script>
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
        childList: true,
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
        for (obj in Bokeh.documents[0]._all_models) {
            if (Bokeh.documents[0]._all_models[obj]._subtype == "Figure"){
                return Bokeh.documents[0]._all_models[obj]
            }
        }
    }

    fig = findFigure();
    x_time_extent = 1000000; // Should be argument?
    function setTimeRange() {
        var now = Date.now();
        fig.x_range.setv({'start': now - x_time_extent, 'end':Date.now()});
    }
    fig.y_range.setv({'start':-500000, 'end':500000})
    //setInterval(setTimeRange,100)
}

</script>
{{ plot_script }}
<body>
{{ plot_div }}
<body> 
</html>
""")

renderer = hv.renderer('bokeh')


def make_document(doc):
    # Create a curve element with all options except for data
    blank_data = pd.DataFrame({'counts': [0]*2,
                               'timestamp': [pd.datetime.now(tz=pytz.utc)]*2,
                               'channel': ['HV.WOOD..EHZ','HV.WOOD..EHN']})
    seis_stream = hv.streams.Buffer(blank_data, index=False, length=100000)

    def plot_seis(data, channel):
        curve = hv.Curve(data=data[data.channel == channel],
                         kdims=['timestamp'], vdims='counts', label='HV.WOOD.EHZ')
        return curve
    seis_dmap = hv.DynamicMap(plot_seis, streams=[seis_stream], kdims=hv.Dimension('channel',
                        values=['HV.WOOD..EHZ','HV.WOOD..EHN']))
    seis_dmap = seis_dmap.options({'Curve': {'width': 1200, 'apply_ranges': True}})
    # layout = seis_dmap
    layout = seis_dmap.layout(['channel']).cols(1)
    doc.seis_stream = seis_stream
    # Add this user to the list of sessions to generate new data callbacks in slurp.py
    slurp.session_list.append(doc)
    doc_root = renderer.get_plot(layout).state
    doc.template = template
    doc.add_root(doc_root)
    return doc


server = Server(make_document, port=81, host='0.0.0.0', allow_websocket_origin=["*"])
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
