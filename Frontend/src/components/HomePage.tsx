import { useRef, useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../AuthContext";
import "../utils/graph.css";
import * as XLSX from "xlsx";
import { plotGraph1, plotGraph2, plotGraph3 } from "../utils/graph";
import { Chart } from "chart.js";
import zoomPlugin from "chartjs-plugin-zoom";
import { FaBackward } from "react-icons/fa";
Chart.register(zoomPlugin);
declare const astro: any;
const HomePage = () => {
  const [error, setError] = useState<string | null>(null);
  const { analyze, user, saveResult } = useAuth();
  const [Data, setData] = useState<any>(null);
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "/fits.js";
    script.src = "/fits.js";
    script.onload = () => {
      if ((window as any).astro && (window as any).astro.FITS) {
        console.log("astro.FITS loaded and ready");
      } else {
        console.error("astro.FITS is not available");
      }
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);
  const handleFileChange = (selectedFile: File | null): Promise<any> => {
    return new Promise((resolve, reject) => {
      const file = selectedFile;
      const extension = file?.name.split(".").pop();

      if (extension === "lc") {
        if (file && (window as any).astro?.FITS) {
          const fits = new (window as any).astro.FITS(file, () => {
            const hdu = fits.getHDU();
            const imageData = hdu.data;
            const data: any = [];
            let table = fits.getDataUnit(1);
            table.getRows(0, imageData.rows, function (rows: any) {
              data.push(rows);
              resolve(data);
            });
          });
        } else {
          reject(new Error("FITS library not found or file is invalid"));
        }
      } else if (
        extension == "xls" ||
        extension == "xlsx" ||
        extension == "csv"
      ) {
        const file = selectedFile;
        const reader = new FileReader();

        reader.onload = (event) => {
          const binaryStr = event.target?.result;
          const workbook = XLSX.read(binaryStr, { type: "binary" });

          // Get the first sheet
          const sheetName = workbook.SheetNames[0];
          const sheet = workbook.Sheets[sheetName];

          // Convert sheet to JSON
          const sheetData = XLSX.utils.sheet_to_json(sheet);
          console.log(sheetData);
        };

        if (file) {
          reader.readAsBinaryString(file);
        }
      } else if (extension == "txt" || extension == "asc") {
        let reader = new FileReader();
        reader.onload = function () {
          let data = reader.result;
          let rows = typeof data === "string" ? data.split("\n") : [];
          let dataArray = rows.map((row: string) =>
            row.split(/\s+/).filter((element: string) => element !== "")
          );
          console.log(dataArray);
        };
        reader.readAsText(file as Blob);
      }
    });
  };
  const { register, handleSubmit, reset } = useForm();
  const fileInput = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState(
    fileInput.current?.files?.[0]?.name ?? "Select File"
  );
  const [isGraphReady, setisGraphReady] = useState(false);
  const [GraphData1, setGraphData1] = useState<Chart | null>(null);
  const [GraphData2, setGraphData2] = useState<Chart | null>(null);
  const [GraphData3, setGraphData3] = useState<Chart | null>(null);
  const ctxRef = useRef<HTMLCanvasElement | null>(null);
  const ctxRef1 = useRef<HTMLCanvasElement | null>(null);
  const ctxRef2 = useRef<HTMLCanvasElement | null>(null);
  const tabContainerRef = useRef<HTMLDivElement | null>(null);
  const resetZoomRef = useRef<HTMLButtonElement | null>(null);
  const loaderAnimationResetRef = useRef<HTMLDivElement | null>(null);
  const onsubmit = async (data: any) => {
    const projectName = data.projectName;
    try {
      let res = await handleFileChange(fileInput.current?.files?.[0] ?? null);
      let responseData: any = await analyze(res, user?.token as string);
      setData({ ...responseData.res, projectName, fileName });
      let X = responseData.res["x"];
      let Y = responseData.res["y"];
      let MF = responseData.res["time_of_occurances"];
      let TOC = responseData.res["time_corresponding_peak_flux"];
      let left = responseData.res["left"];
      let right = responseData.res["right"];
      let leftx: number[] = [];
      let lefty: number[] = [];
      let rightx: number[] = [];
      let righty: number[] = [];

      left.forEach((ele: number) => {
        if (ele >= 0 && ele < X.length && ele < Y.length) {
          // Ensure index is valid
          leftx.push(X[ele]);
          lefty.push(Y[ele]);
        } else {
          console.warn(`Invalid index ${ele} in left array`);
        }
      });
      right.forEach((ele: number) => {
        if (ele >= 0 && ele < X.length && ele < Y.length) {
          // Ensure index is valid
          rightx.push(X[ele]);
          righty.push(Y[ele]);
        } else {
          console.warn(`Invalid index ${ele} in left array`);
        }
      });

      let plotData = [X, Y, MF, TOC, leftx, lefty, rightx, righty];
      setisGraphReady(true);
      const ctx = ctxRef.current?.getContext("2d");
      const ctx1 = ctxRef1.current?.getContext("2d");
      const ctx2 = ctxRef2.current?.getContext("2d");
      if (ctx) {
        // Ensure the canvas context is available
        const resetZoom = resetZoomRef.current;
        const loaderAnimationReset = loaderAnimationResetRef.current;

        let chart1 = plotGraph1(
          plotData,
          ctx,
          resetZoom as HTMLElement,
          loaderAnimationReset as HTMLElement
        );
        let chart2 = plotGraph2(
          plotData,
          ctx1 as CanvasRenderingContext2D,
          resetZoom as HTMLElement,
          loaderAnimationReset as HTMLElement
        );
        let chart3 = plotGraph3(
          plotData,
          ctx2 as CanvasRenderingContext2D,
          resetZoom as HTMLElement,
          loaderAnimationReset as HTMLElement
        );
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
        });
      });
    } catch (error) {
      setError("Something Went Wrong!");
      console.log(error);
    }
  };
  const RemoveGraph = () => {
    setisGraphReady(false);
    if (GraphData1) {
      GraphData1.destroy();
    }
    if (GraphData2) {
      GraphData2.destroy();
    }
    if (GraphData3) {
      GraphData3.destroy();
    }
    reset();
    if (fileInput.current && fileInput.current.files) {
      fileInput.current.value = ""; // Clear the file input
    }
    setFileName("Select File");
  };
  const SaveProject = () => {
    console.log(Data);
    if (Data) {
      saveResult(Data, user?.token as string);
    }
  };
  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen">
      {!isGraphReady && (
        <form
          className="flex flex-col gap-12  justify-center items-center font-unic text-white fadein"
          onSubmit={handleSubmit(onsubmit)}>
          <h1 className="text-4xl font-bold">ANALYSE THE COSMOS</h1>
          <input
            type="text"
            placeholder="Project Name"
            className="border text-lg px-2 py-2 sm:w-[500px] w-[300px] rounded-lg outline-none bg-transparent text-center"
            {...register("projectName", { required: true })}
          />
          <div
            className="block border p-2 rounded-lg text-lg cursor-pointer sm:w-[500px] w-[300px] text-center hover:bg-slate-500"
            onClick={() => {
              fileInput.current?.click();
            }}>
            {fileName}
          </div>
          <input
            type="file"
            id="getFile"
            className="hidden"
            ref={fileInput}
            onChange={() => {
              setFileName(fileInput.current?.files?.[0]?.name ?? "Select File");
            }}
          />

          <div className="btn-container">
            {error && <p className="text-sm text-red-500">{error}</p>}
            <button className="btn" type="submit">
              Analyse
            </button>
          </div>
        </form>
      )}
      {
        <div className={`${!isGraphReady && "hidden"}`}>
          <div className="w-full flex justify-between items-center">
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
                className="tab-button active p-2 rounded-lg border text-white"
                data-tab="chart-1">
                Peak Flux
              </button>
              <button
                className="tab-button p-2 rounded-lg border text-white"
                data-tab="chart-2">
                Rising Time
              </button>
              <button
                className="tab-button p-2 rounded-lg border text-white"
                data-tab="chart-3">
                Decay Time
              </button>
            </div>
            <div>
              <button
                className=" p-2 rounded-lg border text-white"
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  SaveProject();
                }}>
                Save Project
              </button>
            </div>
          </div>

          <div className="graph-container">
            <canvas id="chart-1" ref={ctxRef} className="w-[70vw]"></canvas>
            <canvas
              id="chart-2"
              ref={ctxRef1}
              style={{ display: "none" }}></canvas>
            <canvas
              id="chart-3"
              ref={ctxRef2}
              style={{ display: "none" }}></canvas>
            <div className="button-container">
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
          </div>
        </div>
      }
    </div>
  );
};

export default HomePage;
