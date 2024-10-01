import { Chart, CategoryScale, LinearScale, PointElement, LineElement, LineController,ScatterController,Tooltip } from 'chart.js';

// Register the components you're using
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, LineController,ScatterController,Tooltip);

async function fetchData(url) {
    let response = await fetch(url);
    let data = await response.json();
    let result = JSON.stringify(data);
    return result;
}
function plotGraph1(data,ctx,resetZoom,loaderAnimation) {
    let X = data[0];
    let Y = data[1];
    let MF = data[2];
    let TOC = data[3];
    
    const zoomGestures = {
        pan: {
            enabled: true,
            modifierKey: 'ctrl',
            mode:'xy'
        },
        zoom: {
            wheel: {
                enabled: true,
            },
            mode: 'xy',
        },
        limits: {
            x: { min: 0, max: X.length - 1 },
            y: { min: Math.min(...Y) - 10, max: Math.max(...Y) + 10 },
        }
    };

    const chart1 = new Chart(ctx, {
        type: 'line',
        data: {
            labels: X,
            datasets: [
                {
                    label: 'Flux',
                    data: Y,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 0.5,
                    radius: 1.4,
                    tension: 0,  
                    stepped: false, 
                    borderDash: []
                },
                {
                    label: 'Peak Flux',
                    data: MF.map((mf, index) => ({ x: mf, y: TOC[index] })),
                    backgroundColor: 'rgba(255, 80, 132, 1)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    pointRadius: 6,
                    pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                    type: 'scatter',
                    showLine: false,
                },
            ]
        },
        options: {
            responsive: true,
            //animation: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Time"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)'
                    },
                    ticks:{
                        maxTicksLimit: 5
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Flux"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)', 
                    },
                    ticks:{
                        stepSize: 1000
                    }
                }
            },
            plugins: {
                zoom: zoomGestures,
                
            }
        }
    });

    resetZoom.addEventListener('click', () => {
        resetZoom.style.display = "none";
        loaderAnimation.style.display = "block";
        setTimeout(() => {
            chart1.resetZoom();
            resetZoom.style.display = "block";
            loaderAnimation.style.display = "none";
        }, 500);
        
    });
}


function plotGraph2(data,ctx,resetZoom,loaderAnimation) {
    let X = data[0];
    let Y = data[1];
    let leftx = data[4];
    let lefty = data[5];
    const zoomGestures = {
        pan: {
            enabled: true,
            modifierKey: 'ctrl',
        },
        zoom: {
            wheel: {
                enabled: true,
            },
            mode: 'xy',
        },
        limits: {
            x: { min: 0, max: X.length - 1 },
            y: { min: Math.min(...Y) - 10, max: Math.max(...Y) + 10 },
        }
    };
    const chart2 = new Chart(ctx, {
        type: 'line',
        data: {
            labels: X,
            datasets: [
                {
                    label: 'Flux',
                    data: Y,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 0.5,
                    radius: 1.4,
                },
                {
                    label: 'rising time Flux',
                    data: leftx.map((xValue, index) => ({ x: xValue, y: lefty[index] })), 
                    backgroundColor: 'rgba(0, 255, 0, 1)',  
                    borderColor: 'rgba(0, 128, 0, 1)', 
                    pointRadius: 6,
                    pointBackgroundColor: 'rgba(0, 255, 0, 1)',
                    type: 'scatter',
                    showLine: false
                }
            ]
        },
        options: {
            responsive: true,
            //animation: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Time"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)'
                    },
                    ticks:{
                        maxTicksLimit: 5
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Flux"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)', 
                    },
                    ticks:{
                        stepSize: 1000
                    }
                }
            },
            plugins: {
                zoom: zoomGestures
            }
        }
    });

    resetZoom.addEventListener('click', () => {
        resetZoom.style.display="none";
        loaderAnimation.style.display="block";
        
        setTimeout(()=>{chart2.resetZoom();
        resetZoom.style.display="block";
        loaderAnimation.style.display="none";
        },500);
        
    });
}
export{plotGraph1,plotGraph2,fetchData}