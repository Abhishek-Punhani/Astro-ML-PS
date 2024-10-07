import React, { useEffect } from "react";
import { useRef, useState } from "react";
import { plotGraph1, plotGraph2, plotGraph3 } from "../utils/graph.ts";
import { Chart } from "chart.js";
import zoomPlugin from "chartjs-plugin-zoom";
import { FaBackward } from "react-icons/fa";
import "../utils/graph.css";
Chart.register(zoomPlugin);
interface GraphProps {
  plotData: any;
  remove: () => void;
}
const Graph: React.FC<GraphProps> = React.memo(({ plotData, remove }) => {
  const [GraphData1, setGraphData1] = useState<Chart | null>(null);
  const [GraphData2, setGraphData2] = useState<Chart | null>(null);
  const [GraphData3, setGraphData3] = useState<Chart | null>(null);
  const ctxRef = useRef<HTMLCanvasElement | null>(null);
  const ctxRef1 = useRef<HTMLCanvasElement | null>(null);
  const ctxRef2 = useRef<HTMLCanvasElement | null>(null);
  const tableRef = useRef<HTMLDivElement | null>(null);
  const tabContainerRef = useRef<HTMLDivElement | null>(null);
  const resetZoomRef = useRef<HTMLButtonElement | null>(null);
  const loaderAnimationResetRef = useRef<HTMLDivElement | null>(null);
  const [currentTab, setCurrentTab] = useState("Peak Flux");

  useEffect(() => {
    if (GraphData1) GraphData1.destroy();
    if (GraphData2) GraphData2.destroy();
    if (GraphData3) GraphData3.destroy();
    const ctx = ctxRef.current?.getContext("2d");
    const ctx1 = ctxRef1.current?.getContext("2d");
    const ctx2 = ctxRef2.current?.getContext("2d");
    setCurrentTab("Peak Flux");
    if (ctx && ctx1 && ctx2 && plotData) {
      // Ensure the canvas context is available
      console.log("Creating new chart instances");
      const resetZoom = resetZoomRef.current;
      const loaderAnimationReset = loaderAnimationResetRef.current;

      const chart1 = plotGraph1(
        plotData,
        ctx,
        resetZoom as HTMLElement,
        loaderAnimationReset as HTMLElement
      );
      const chart2 = plotGraph2(
        plotData,
        ctx1 as CanvasRenderingContext2D,
        resetZoom as HTMLElement,
        loaderAnimationReset as HTMLElement
      );
      const chart3 = plotGraph3(
        plotData,
        ctx2 as CanvasRenderingContext2D,
        resetZoom as HTMLElement,
        loaderAnimationReset as HTMLElement
      );
      const table = tableRef.current;
      if (table) {
        table.innerHTML = `<table style="border-collapse: collapse; width: 100%; height: 100%;" className="table-auto mt-4 text-white"> 
          <thead>
        <tr>
          <th style="border: 1px solid white; padding: 8px;">S.no.</th>
          <th style="border: 1px solid white; padding: 8px;">Peak Flare occurrence time</th>
          <th style="border: 1px solid white; padding: 8px;">Count/s</th>
          <th style="border: 1px solid white; padding: 8px;">Starting Time</th>
          <th style="border: 1px solid white; padding: 8px;">Ending Time</th>
          <th style="border: 1px solid white; padding: 8px;">Rise Time</th>
          <th style="border: 1px solid white; padding: 8px;">Decay Time</th>
          <th style="border: 1px solid white; padding: 8px;">Total Time</th>
        </tr>
          </thead>
          <tbody>
        ${plotData[2]
          .map(
            (mf: number, index: number) =>
              `<tr key=${index}>
            <td style="border: 1px solid white; padding: 8px;">${index + 1}</td>
            <td style="border: 1px solid white; padding: 8px;">${mf}</td>
            <td style="border: 1px solid white; padding: 8px;">${plotData[3][index]}</td>
            <td style="border: 1px solid white; padding: 8px;">${plotData[4][index]}</td>
            <td style="border: 1px solid white; padding: 8px;">${plotData[6][index]}</td>
            <td style="border: 1px solid white; padding: 8px;">${plotData[8][index]}</td>
            <td style="border: 1px solid white; padding: 8px;">${plotData[9][index]}</td>
            <td style="border: 1px solid white; padding: 8px;">${plotData[9][index] + plotData[8][index]}</td>
          </tr>`
          )
          .join("")}
          </tbody>
        </table>`;
      }
      setGraphData1(chart1);
      setGraphData2(chart2);
      setGraphData3(chart3);
    } else {
      console.error("Canvas context is not available");
    }
    document.querySelectorAll(".tab-button").forEach((button) => {
      button.addEventListener("click", () => {
        const activeTab = (button as HTMLButtonElement).dataset.tab;

        document.querySelectorAll(".tab-button").forEach((btn) => {
          btn.classList.remove("active");
        });
        button.classList.add("active");

        const chart1 = document.getElementById("chart-1");
        if (chart1) {
          chart1.style.display = activeTab === "chart-1" ? "block" : "none";
        }
        const chart2 = document.getElementById("chart-2");
        if (chart2) {
          chart2.style.display = activeTab === "chart-2" ? "block" : "none";
        }
        const chart3 = document.getElementById("chart-3");
        if (chart3) {
          chart3.style.display = activeTab === "chart-3" ? "block" : "none";
        }
        const table = document.getElementById("table");
        if (table) {
          table.style.display = activeTab === "table" ? "block" : "none";
        }
      });
    });
    return () => {
      if (GraphData1) GraphData1.destroy();
      if (GraphData2) GraphData2.destroy();
      if (GraphData3) GraphData3.destroy();
    };
    // eslint-disable-next-line
  }, [plotData]);
  const RemoveGraph = () => {
    if (GraphData1) {
      GraphData1.destroy();
    }
    if (GraphData2) {
      GraphData2.destroy();
    }
    if (GraphData3) {
      GraphData3.destroy();
    }
    remove();
  };
  function downloadCSV(): void {
    if (!plotData || !plotData[2] || !plotData[2].length) {
      console.error("No data available to download");
      return;
    }

    const headers = [
      "S.no.",
      "Peak Flare occurrence time",
      "Count/s",
      "Starting Time",
      "Ending Time",
      "Rise Time",
      "Decay Time",
      "Total Time",
    ];

    const rows = plotData[2].map((mf: number, index: number) => [
      index + 1,
      mf,
      plotData[3][index],
      plotData[4][index],
      plotData[6][index],
      plotData[8][index],
      plotData[9][index],
      plotData[9][index] + plotData[8][index],
    ]);

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((row: number[]) => row.join(","))].join(
        "\n"
      );

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "plot_data.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  return (
    <>
      <div className="w-full flex justify-between items-center mt-16">
        <button
          className="p-2 rounded-full h-10 border text-white "
          onClick={RemoveGraph}>
          <div className="flex justify-center items-center w-full gap-x-4">
            <span className="flex items-center gap-2">
              <FaBackward />
            </span>
            <span>Back</span>
          </div>
        </button>
        <div
          className="tab-container gap-4 flex items-center justify-evenly "
          ref={tabContainerRef}>
          <button
            className="tab-button p-2 rounded-lg border text-white"
            data-tab="chart-1"
            onClick={() => setCurrentTab("Peak Flux")}>
            Peak Flux
          </button>
          <button
            className="tab-button p-2 rounded-lg border text-white"
            data-tab="chart-2"
            onClick={() => setCurrentTab("Rising Time")}>
            Rising Time
          </button>
          <button
            className="tab-button p-2 rounded-lg border text-white"
            data-tab="chart-3"
            onClick={() => setCurrentTab("Decay Time")}>
            Decay Time
          </button>
          <button
            className="tab-button p-2 rounded-lg border text-white"
            data-tab="table"
            onClick={() => setCurrentTab("Table")}>
            Table
          </button>
        </div>
      </div>

      <div className="graph-container">
        <canvas id="chart-1" ref={ctxRef} className="w-[70vw]"></canvas>
        <canvas id="chart-2" ref={ctxRef1} style={{ display: "none" }}></canvas>
        <canvas id="chart-3" ref={ctxRef2} style={{ display: "none" }}></canvas>
        <div
          id="table"
          ref={tableRef}
          style={{ display: "none", color: "white" }}
          className={`${currentTab !== "Table" && "hidden"} w-[70vw]`}></div>
        <div
          className={`button-container ${currentTab == "Table" && "hidden"}`}>
          <button
            className="reset-button p-2 rounded-lg border text-white"
            id="reset-zoom"
            ref={resetZoomRef}>
            Reset Zoom
          </button>
          <div
            className="loader hidden"
            id="loader-animation-reset"
            ref={loaderAnimationResetRef}></div>
        </div>
        <div
          className={`button-container ${currentTab !== "Table" && "hidden"}`}>
          <button
            className="p-2 rounded-lg border text-white"
            onClick={downloadCSV}>
            Download Csv
          </button>
        </div>
      </div>
    </>
  );
});

export default Graph;
