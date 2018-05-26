function waitForAddedNode(params) {
    new MutationObserver(function(mutations) {
        var el = document.getElementsByClassName(params.class).length;
        if (el) {
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
    fig.y_range.setv({'start':-5000, 'end':5000})
    setInterval(setTimeRange,100)
}