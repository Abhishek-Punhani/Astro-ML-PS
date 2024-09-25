import React, {useRef, useState} from 'react'

const HomePage = () => {
  const fileInput = useRef<HTMLInputElement>(null)
  const [fileName, setFileName] = useState(fileInput.current?.files?.[0]?.name ?? 'Select File');
  return (
    <div className='flex flex-col gap-6 h-screen w-full justify-center items-center'>
        <h1 className='text-3xl font-bold'>
            Analyse The Cosmos
        </h1>

        <input type="text" placeholder='Project Name' className='border w-96 px-2 py-2 rounded-lg'/>
        <button  className='block w-96 border p-2 rounded-lg' onClick={()=>{fileInput.current?.click()}}>{fileName}</button>
            <input type='file' id="getFile" className='hidden' ref={fileInput} onChange={()=>{setFileName(fileInput.current?.files?.[0]?.name ?? 'Select File')}}/>
        <button className='w-36 cursor-pointer p-2 rounded-lg border'>Analyse</button>
    </div>
  )
} 

export default HomePage