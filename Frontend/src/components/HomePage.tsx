import React, {useRef, useState,useEffect} from 'react'
import {useForm} from 'react-hook-form'
declare const astro: any;
const HomePage = () => {
  const [header, setHeader] = useState(null);
  const [imageData, setImageData] = useState(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const script = document.createElement('script');
    script.src = '/fits.js';  // Path where fits.js is located
    script.onload = () => {
      if ((window as any).astro && (window as any).astro.FITS) {
        console.log('astro.FITS loaded and ready');
      } else {
        console.error('astro.FITS is not available');
      }
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);
  const handleFileChange = (selectedFile: File | null) => {
    const file = selectedFile;
    const extension = file?.name.split('.').pop();
    if(extension == 'lc'){
    if (file && (window as any).astro?.FITS) {
      const fits = new (window as any).astro.FITS(file, () => {
        const hdu = fits.getHDU();
        const header = hdu.header;   // Full header object
        const imageData = hdu.data; 
        setHeader(header);
        setImageData(imageData);
        console.log(header);
        console.log(imageData)
        let table = fits.getDataUnit(1);
        table.getRows(0, imageData.rows, function(rows : any) {
          console.log(rows);
        });
      });
    }
      
    }
    else if (extension == 'txt' || extension == 'asc'){
      let reader = new FileReader();
      reader.onload = function(){
        let data = reader.result;
        console.log(data);
      }
      reader.readAsText(file as Blob);
    }
  };
  const {register, handleSubmit} = useForm();
  const fileInput = useRef<HTMLInputElement>(null)
  const [fileName, setFileName] = useState(fileInput.current?.files?.[0]?.name ?? 'Select File');
  const onsubmit = (data: any) => {
    console.log(data)
    handleFileChange(fileInput.current?.files?.[0] ?? null)
  }
  return (
    <div className='flex flex-col items-center justify-center h-screen w-screen'>
    <form  className='flex flex-col gap-12  justify-center items-center font-unic text-white fadein' onSubmit={handleSubmit(onsubmit)}>
        <h1 className='text-4xl font-bold'>
            ANALYSE THE COSMOS
        </h1>
      
        <input type="text" placeholder='Project Name' className='border text-lg px-2 py-2 sm:w-[500px] w-[300px] rounded-lg outline-none bg-transparent text-center' {...register("projectName",{required:true})}/>
        <div  className='block border p-2 rounded-lg text-lg cursor-pointer sm:w-[500px] w-[300px] text-center hover:bg-slate-500' onClick={()=>{fileInput.current?.click()}}>{fileName}</div>
            <input type='file' id="getFile" className='hidden' ref={fileInput} onChange={() => {setFileName(fileInput.current?.files?.[0]?.name ?? 'Select File')}} />
    
<div className="btn-container">
  
  
  <button className="btn" type='submit'>Analyse</button>
</div>
    </form>
    </div>
  )
} 

export default HomePage