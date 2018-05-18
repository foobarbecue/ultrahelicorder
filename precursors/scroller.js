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

setInterval(setTimeRange, 1000)