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
            // fig.y_range.setv({'start':-100000, 'end':100000});
        }
    }
    setInterval(setTimeRange,100)
}
