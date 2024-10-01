import { useRef, useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../AuthContext";
declare const astro: any;
const HomePage = () => {
  const [error, setError] = useState<string | null>(null);
  const { analyze, user } = useAuth();
  useEffect(() => {
    const script = document.createElement("script");
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
      } else if (extension === "txt" || extension === "asc") {
        const reader = new FileReader();
        reader.onload = function () {
          const data = reader.result;
          if (data == null) {
            reject(new Error("Invalid File"));
          } else {
            resolve(data);
          }
        };
        reader.onerror = function () {
          reject(new Error("Error reading the file"));
        };
        reader.readAsArrayBuffer(file as File); // Use appropriate method based on your data type
      } else {
        reject(new Error("Unsupported file type"));
      }
    });
  };

  const { register, handleSubmit } = useForm();
  const fileInput = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState(
    fileInput.current?.files?.[0]?.name ?? "Select File"
  );
  const onsubmit = async () => {
    try {
      let res = await handleFileChange(fileInput.current?.files?.[0] ?? null);
      await analyze(res, user?.token as string);
    } catch (error) {
      setError("Something Went Wrong!");
      console.log(error);
    }
  };
  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen">
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
    </div>
  );
};

export default HomePage;
