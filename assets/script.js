const checkElement = async selector => {
    while ( document.querySelector(selector) === null  || document.querySelector(selector).classList.contains('dash-graph--pending')) {
        await new Promise( resolve =>  requestAnimationFrame(resolve) )
    }
    return document.querySelector(selector);
};

checkElement('#sunburst_chart').then((sunburstChart) =>{
    var sunburstChartPlot = sunburstChart.querySelector('.js-plotly-plot');
    if (sunburstChartPlot) {
        sunburstChartPlot.on('plotly_sunburstclick', function(event) {
            console.log(event);
            hidden_button = document.getElementById("sunburst_chart_click")
            hidden_button.innerHTML = event.points[0].currentPath + event.points[0].label
            if (event.points[0].currentPath){
                hidden_button.click()
            }
            return false;
        });
    }
});
