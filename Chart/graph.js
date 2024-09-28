async function fetchData(url) {
    let response = await fetch(url);
    let data = await response.json();
    let result = JSON.stringify(data);
    return result;
}

function plotGraph1(data) {
    let X = data[0];
    let Y = data[1];
    let MF = data[2];
    let TOC = data[3];

    const ctx = document.getElementById('chart-1').getContext('2d');

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
                }
            ]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Time"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)'
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
                }
            },
            plugins: {
                zoom: zoomGestures
            }
        }
    });

    document.getElementById("reset-zoom").addEventListener('click', () => {
        chart1.resetZoom();
    });
}


function plotGraph2() {
    // Example data; replace with your actual second graph data fetching logic
    const X = [1, 2, 3, 4, 5];
    const Y = [10, 15, 12, 18, 14];

    const ctx = document.getElementById('chart-2').getContext('2d');

    const chart2 = new Chart(ctx, {
        type: 'line',
        data: {
            labels: X,
            datasets: [
                {
                    label: 'Example Data',
                    data: Y,
                    backgroundColor: 'rgba(255, 205, 86, 0.2)',
                    borderColor: 'rgba(255, 205, 86, 1)',
                    borderWidth: 0.5,
                    radius: 1.4,
                }
            ]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "X-Axis"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)'
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: "Y-Axis"
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.5)', 
                    },
                }
            }
        }
    });

    document.getElementById("reset-zoom").addEventListener('click', () => {
        chart2.resetZoom();
    });
}

let g1Data =  fetchData('http://127.0.0.1:5000/data');
g1Data.then(response => {
    response = JSON.parse(response);
    plotGraph1(response);
    plotGraph2();
})

// Handling tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const activeTab = button.dataset.tab;

        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        document.getElementById('chart-1').style.display = (activeTab === 'chart-1') ? 'block' : 'none';
        document.getElementById('chart-2').style.display = (activeTab === 'chart-2') ? 'block' : 'none';
    });
});
