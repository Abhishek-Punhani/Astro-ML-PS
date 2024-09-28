async function fetchData(){
    let response = await fetch('http://127.0.0.1:5000/data');
    let data = await response.json();
    let result = JSON.stringify(data);
    return result;
}

let data = fetchData()
data.then(response => {
    plotGraph(response);
});

function plotGraph(data){
    data = JSON.parse(data);
    let X = data[0];
    let Y = data[1];
    let MF = data[2]
    let TOC = data[3]
    const ctx = document.getElementById('chart-1').getContext('2d');
    
    const zoomGestures = {
        pan: {
            enabled: true,
            modifierKey: 'ctrl',
        },
        zoom: {
            wheel: {
                enabled: true
            },
            mode: 'xy',
        },
        limits: {
            x: { min: 0, max: X.length - 1 },
            y: { min: Math.min(...Y) - 10, max: Math.max(...Y) + 10 },
        }
    };

    const chart_1 = new Chart(ctx, {
        type: 'line',
        data: {
            labels: X,
            datasets: [
                {
                    label: 'Flux',  // Line chart for flux vs time
                    data: Y,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 0.5,
                    radius: 1.4,
                    type: 'line',  // Explicitly set to line
                },
                {
                    label: 'Peak Flux',
                    data: MF.map((mf, index) => ({ x: mf, y: TOC[index] })),
                    backgroundColor: 'rgba(255, 80, 132, 1)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    pointRadius:6, 
                    pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                    type: 'scatter',
                    showLine: false 
                }
            ]
        },
        options: {
            responsive: true,
            animation:false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Time"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)'
                    },
                    ticks: {
                        maxTicksLimit: 5
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: "Flux"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)', 
                    },
                    ticks: {
                        stepSize: 1000
                    }
                }
            },
            plugins: {
                zoom: zoomGestures
            }
        }
    });

    document.getElementById("reset-zoom").addEventListener('click', () => {
        chart_1.resetZoom();
    });
}
