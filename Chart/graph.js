//using fetch API to fetch the data from app.py
async function fetchData(){
    let response = await fetch('http://127.0.0.1:5000/data');
    let data = await response.json();
    let result = JSON.stringify(data);
    return result;
}
let data = fetchData()
data.then(response=>{
    plotGraph(response)
});
console.log(ChartZoom.version)
function plotGraph(data){
    //converting string back to json object
    data = JSON.parse(data);
    let X = data[0]//the time values
    let Y = data[1]//the flux values
    const ctx = document.getElementById('chart-1').getContext('2d');
    const zoomGestures = {
        pan: {
          enabled: true,
          modifierKey: 'ctrl',
        },
        zoom: {
          drag: {
            enabled: true
          },
          mode: 'xy',
        },
      };
    const chart_1 = new Chart(ctx, 
        {
            type:'line',
            data :{
                // give the x values here
                labels :X,
                datasets:[
                    { 
                        label : 'flux',
                        //give the y values here
                        data:Y,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth : 1
                    }
                ]
            },
            options:{
                responsive : true,
                scales:{
                    x:{
                        title : {
                            display: true,
                            text : "Time"
                        }
                    },
                    y:{
                        title: {
                            display : true,
                            text: "Flux"
                        }
                    }
                },
                plugins: {
                    zoom: zoomGestures
                }
            }
        }
    );
    const panStatus = () => zoomOptions.pan.enabled ? 'enabled' : 'disabled';
    const zoomStatus = () => zoomOptions.zoom.drag.enabled ? 'enabled' : 'disabled';
    document.getElementById("reset-zoom").addEventListener('click',()=>{
        chart_1.resetZoom();
    })
}