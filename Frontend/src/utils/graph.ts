import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  ScatterController,
  Tooltip,
  ChartDataset,
} from "chart.js";
import zoomPlugin from "chartjs-plugin-zoom";

// Register the components you're using
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  ScatterController,
  Tooltip,
  zoomPlugin
);

interface Data {
  [index: number]: number[]; // Array of number arrays (X, Y, MF, TOC, leftx, lefty)
}

// Define

// Define the plotGraph1 function with proper types
function plotGraph1(
  data: Data,
  ctx: CanvasRenderingContext2D,
  resetZoom: HTMLElement,
  loaderAnimation: HTMLElement
): Chart {
  const X = data[0];
  const Y = data[1];
  const MF = data[2];
  const TOC = data[3];

  const zoomGestures = {
    pan: {
      enabled: true,
      modifierKey: "ctrl" as "ctrl",
      mode: "xy" as const,
    },
    zoom: {
      wheel: {
        enabled: true,
      },
      mode: "xy" as const,
    },
    limits: {
      x: { min: 0, max: X.length - 1 },
      y: { min: Math.min(...Y) - 10, max: Math.max(...Y) + 10 },
    },
  };

  const chart1 = new Chart(ctx, {
    type: "line",
    data: {
      labels: X,
      datasets: [
        {
          label: "Flux",
          data: Y,
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 0.5,
          radius: 1.4,
          order: 1, // Line chart first
          stepped: false,
          z: 1,
          dataSetIndex: 0,
        } as ChartDataset<"line">,
        {
          label: "Peak Flux",
          data: MF.map((mf, index) => ({ x: mf, y: TOC[index] })),
          backgroundColor: "rgba(255, 80, 132, 1)",
          borderColor: "rgba(255, 99, 132, 1)",
          pointRadius: 8, // Make points larger for visibility
          pointStyle: "circle", // Ensure circle points are used
          pointBackgroundColor: "rgba(255, 99, 132, 1)",
          type: "scatter",
          showLine: false,
          order: 2, // Scatter plot second, rendered on top
          z: 10,
          dataSetIndex: 1,
        } as ChartDataset<"scatter">,
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
          grid: {
            color: "rgba(255, 255, 255, 0.5)",
          },
          ticks: {
            maxTicksLimit: 5,
          },
        },
        y: {
          title: {
            display: true,
            text: "Flux",
          },
          grid: {
            color: "rgba(255, 255, 255, 0.5)",
          },
          ticks: {
            stepSize: 1000,
          },
        },
      },
      plugins: {
        zoom: zoomGestures,
      },
    },
  });

  resetZoom.addEventListener("click", () => {
    resetZoom.style.display = "none";
    loaderAnimation.style.display = "block";
    setTimeout(() => {
      chart1.resetZoom();
      resetZoom.style.display = "block";
      loaderAnimation.style.display = "none";
    }, 500);
  });

  return chart1;
}

function plotGraph2(
  data: Data,
  ctx: CanvasRenderingContext2D,
  resetZoom: HTMLElement,
  loaderAnimation: HTMLElement
): Chart {
  const X = data[0];
  const Y = data[1];
  const leftx = data[4];
  const lefty = data[5];

  const zoomGestures = {
    pan: {
      enabled: true,
      modifierKey: "ctrl" as "ctrl",
    },
    zoom: {
      wheel: {
        enabled: true,
      },
      mode: "xy" as const,
    },
    limits: {
      x: { min: 0, max: X.length - 1 },
      // Adjust y limits to include both Y and lefty values
      y: {
        min: Math.min(...Y, ...lefty) - 10,
        max: Math.max(...Y, ...lefty) + 10,
      },
    },
  };

  const chart2 = new Chart(ctx, {
    type: "line",
    data: {
      labels: X,
      datasets: [
        {
          label: "Flux",
          data: Y,
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 0.5,
          radius: 1.4,
          order: 1, // Line chart first
          z: 1,
          dataSetIndex: 0,
        } as ChartDataset<"line">,
        {
          label: "Rising time Flux",
          data: leftx.map((xValue, index) => ({ x: xValue, y: lefty[index] })),
          backgroundColor: "rgba(0, 255, 0, 1)",
          borderColor: "rgba(0, 128, 0, 1)",
          pointRadius: 8, // Make points larger for visibility
          pointStyle: "circle",
          pointBackgroundColor: "rgba(0, 255, 0, 1)",
          type: "scatter",
          showLine: false,
          order: 2, // Scatter plot second, rendered on top
          z: 10,
          dataSetIndex: 1,
        } as ChartDataset<"scatter">,
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
          grid: {
            color: "rgba(255, 255, 255, 0.5)",
          },
          ticks: {
            maxTicksLimit: 5,
          },
        },
        y: {
          title: {
            display: true,
            text: "Flux",
          },
          grid: {
            color: "rgba(255, 255, 255, 0.5)",
          },
          ticks: {
            stepSize: 1000,
          },
        },
      },
      plugins: {
        zoom: zoomGestures,
      },
    },
  });

  resetZoom.addEventListener("click", () => {
    resetZoom.style.display = "none";
    loaderAnimation.style.display = "block";

    setTimeout(() => {
      chart2.resetZoom();
      resetZoom.style.display = "block";
      loaderAnimation.style.display = "none";
    }, 500);
  });

  return chart2;
}

function plotGraph3(
  data: Data,
  ctx: CanvasRenderingContext2D,
  resetZoom: HTMLElement,
  loaderAnimation: HTMLElement
): Chart {
  const X = data[0];
  const Y = data[1];
  const rightx = data[6];
  const righty = data[7];

  const zoomGestures = {
    pan: {
      enabled: true,
      modifierKey: "ctrl" as "ctrl",
    },
    zoom: {
      wheel: {
        enabled: true,
      },
      mode: "xy" as const,
    },
    limits: {
      x: { min: 0, max: X.length - 1 },
      // Adjust y limits to include both Y and lefty values
      y: {
        min: Math.min(...Y, ...righty) - 10,
        max: Math.max(...Y, ...righty) + 10,
      },
    },
  };

  const chart3 = new Chart(ctx, {
    type: "line",
    data: {
      labels: X,
      datasets: [
        {
          label: "Flux",
          data: Y,
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 0.5,
          radius: 1.4,
          order: 1, // Line chart first
          z: 1,
          dataSetIndex: 0,
        } as ChartDataset<"line">,
        {
          label: "Rising time Flux",
          data: rightx.map((xValue, index) => ({
            x: xValue,
            y: righty[index],
          })),
          backgroundColor: "rgba(0, 255, 0, 1)",
          borderColor: "rgba(0, 128, 0, 1)",
          pointRadius: 8, // Make points larger for visibility
          pointStyle: "circle",
          pointBackgroundColor: "rgba(0, 0, 255, 1)",
          type: "scatter",
          showLine: false,
          order: 2, // Scatter plot second, rendered on top
          z: 10,
          dataSetIndex: 1,
        } as ChartDataset<"scatter">,
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
          grid: {
            color: "rgba(255, 255, 255, 0.5)",
          },
          ticks: {
            maxTicksLimit: 5,
          },
        },
        y: {
          title: {
            display: true,
            text: "Flux",
          },
          grid: {
            color: "rgba(255, 255, 255, 0.5)",
          },
          ticks: {
            stepSize: 1000,
          },
        },
      },
      plugins: {
        zoom: zoomGestures,
      },
    },
  });

  resetZoom.addEventListener("click", () => {
    resetZoom.style.display = "none";
    loaderAnimation.style.display = "block";

    setTimeout(() => {
      chart3.resetZoom();
      resetZoom.style.display = "block";
      loaderAnimation.style.display = "none";
    }, 500);
  });

  return chart3;
}

export { plotGraph1, plotGraph2, plotGraph3 };
