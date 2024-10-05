import { useRef, useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../AuthContext";
import "../utils/graph.css";
import * as XLSX from "xlsx";
import Graph from "./Graph";
declare const astro: any;
const HomePage = () => {
  const { analyze, user, saveResult } = useAuth() as unknown as {
    analyze: (data: any, token: string) => Promise<{ res: any }>;
    user: { token: string };
    saveResult: (data: any, token: string) => void;
  };
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
      } else {
        setError("root", { type: "manual", message: "Invalid File Type!" });
      }
    });
  };
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm();
  const fileInput = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState(
    fileInput.current?.files?.[0]?.name ?? "Select File"
  );
  const [isGraphReady, setisGraphReady] = useState(false);
  const [plotData, setPlotData] = useState<any[] | null>(null);
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

      setPlotData([X, Y, MF, TOC, leftx, lefty, rightx, righty] as any[]);
      setisGraphReady(true);
    } catch (error) {
      setError("root", {
        type: "manual",
        message: "Something Went Wrong!",
      });
      console.log(error);
    }
  };
  const RemoveGraph = () => {
    setisGraphReady(false);
    if (fileInput.current && fileInput.current.files) {
      fileInput.current.value = ""; // Clear the file input
    }
    reset();
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
          {errors.root && (
            <p className="text-sm text-red-500">{errors.root.message}</p>
          )}
          {errors.projectName?.message && (
            <p className="text-sm text-red-500">
              {errors.projectName.message as string}
            </p>
          )}
          <input
            type="text"
            placeholder="Project Name"
            className="border text-lg px-2 py-2 sm:w-[500px] w-[300px] rounded-lg outline-none bg-transparent text-center"
            {...register("projectName", {
              required: "Project Name is Required",
            })}
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
            <button className="btn" type="submit">
              Analyse
            </button>
          </div>
        </form>
      )}
      {isGraphReady && plotData && (
        <div>
          <Graph plotData={plotData} remove={RemoveGraph} />
          <div className="w-full">
            <button
              className=" p-2 rounded-lg border text-white w-full"
              type="button"
              onClick={(e) => {
                e.preventDefault();
                SaveProject();
              }}>
              Save Project
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
