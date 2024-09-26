import React, { useState } from 'react'
import Navbar from '../components/Navbar'
import { useAuth } from '../AuthContext'
import {useForm} from 'react-hook-form'
const Settings = () => {
  const [Page, setPage] = useState('Account')
  const { user } = useAuth()
  const { register, handleSubmit, formState: { isSubmitting } } = useForm()
  const onsubmit=(data:any)=>{
    if(data.username != user?.username || data.email != user?.email){
    console.log(data)
  }
  }
  return (
    <>
    <Navbar/>
    <div className=' mt-20 w-full flex justify-center items-center py-8'>
      <div className='w-4/6 rounded-xl border shadow flex flex-row' style={{height:"80vh"}}>
         <div className='h-full w-1/4 border-r flex flex-col gap-2 py-2 px-2'>
         <div className={`w-full py-4 px-4 text-lg  rounded-lg ${Page == 'Account'? 'bg-slate-50 border-b':'border-b border-white'} cursor-pointer`} onClick={()=>setPage('Account')}>Account and Security</div>
         {/* <div className={`w-full py-4 px-4 text-lg  rounded-lg ${Page == 'Theme'? 'bg-slate-50 border-b':'border-b border-white'} cursor-pointer`} onClick={()=>{setPage('Theme')}}>Theme</div> */}
         </div>
         
         {Page == 'Account' &&<form className='flex flex-col justify-between h-full w-3/4 items-center'  onSubmit={handleSubmit(onsubmit)}> <div className='h-full w-full flex flex-col'><div className='flex flex-row items-center w-full justify-between py-6 px-8 border-b'>
            <h1>Username:</h1>
            <input type="text" className='w-2/5 border p-2 rounded-lg text-lg' defaultValue={user?.username} {...register("username")}/>
         </div>
         <div className='flex flex-row items-center w-full justify-between py-6 px-8 border-b'>
            <h1>Email:</h1>
            <input type="text" className='w-2/5 border p-2 rounded-lg text-lg bg-slate-50' defaultValue={user?.email} {...register("email")}/>
            </div>
            <div className='flex flex-row items-center w-full justify-between py-6 px-8 border-b'>
            <h1>Password:</h1>
            <div className='w-1/3 border p-2 rounded-lg bg-slate-50 shadow cursor-pointer'>Change Password</div>
            </div>
            
         </div>
         <button type='submit' disabled={isSubmitting} className='my-6 border shadow rounded-lg p-2 w-28 hover:bg-slate-50'>Save</button>
         </form>
         }
         </div>
      
    </div>
    </>
  )
}

export default Settings