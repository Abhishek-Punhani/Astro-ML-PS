import React,{useEffect, useState} from 'react'

const Sidebar = ({SidebarStatus}:any) => {
  let array = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
  const [BarOpen, setBarOpen] = useState(true)
  const[smBarOpen, setSmBarOpen] = useState(false)
  useEffect(()=>{
    if(SidebarStatus){
      setBarOpen(true)
      if(window.innerWidth < 1024){
        setSmBarOpen(true)
      }
    }
  },[SidebarStatus])

  return (
    
    <div className={`${BarOpen?'lg:w-1/5':'lg:w-0'} ${smBarOpen?'w-64':'w-0'} h-screen py-4 border-r flex flex-col overflow-scroll fixed transition-width ease-in-out delay-150 bg-white z-10`}>
        <div className='border-b border-slate-100 px-4 pb-4 flex flex-row justify-between items-center'> 
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="icon-lg mx-2 text-token-text-secondary cursor-pointer hover:bg-slate-100 rounded-full p-2 block " onClick={()=>{setBarOpen(false);setSmBarOpen(false)}}><path fill-rule="evenodd" clip-rule="evenodd" d="M3 8C3 7.44772 3.44772 7 4 7H20C20.5523 7 21 7.44772 21 8C21 8.55228 20.5523 9 20 9H4C3.44772 9 3 8.55228 3 8ZM3 16C3 15.4477 3.44772 15 4 15H14C14.5523 15 15 15.4477 15 16C15 16.5523 14.5523 17 14 17H4C3.44772 17 3 16.5523 3 16Z" fill="currentColor"></path></svg>
        <button className='border px-4 py-2 h-12 rounded-lg hover:bg-slate-100 z-20'>+</button>
        </div>
        <div className='py-8 px-4'>
            <h1>Previous Projects</h1>
            <div className="list my-4 flex flex-col gap-2 ">
                {array.map((item, index) => {
                    return (<div key={index} className='w-full border py-2 px-2 rounded-lg cursor-pointer hover:bg-slate-50'>
                        Project {item}
                    </div>
                    )
                }

                )}
            </div>
        </div>

    </div>
  )
}

export default Sidebar