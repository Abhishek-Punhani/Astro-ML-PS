import React,{useState} from 'react'
import Sidebar from './Sidebar'
const Navbar = () => {
  const [Menuopen, setMenuopen] = useState(false)
  const [SideBarOpen, setSideBarOpen] = useState(false)
  return (
    <>
    <Sidebar SidebarStatus={`${SideBarOpen}`}/>
    <div className='navbar h-20  w-full flex justify-between items-center px-4 border-b border-slate-100 fixed top-0 transition-width ease-in-out delay-150 right-0 '>
        
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="icon-lg mx-2 text-token-text-secondary cursor-pointer hover:bg-slate-100 rounded-full p-2 block " onClick={()=>{setSideBarOpen(!SideBarOpen)}}><path fill-rule="evenodd" clip-rule="evenodd" d="M3 8C3 7.44772 3.44772 7 4 7H20C20.5523 7 21 7.44772 21 8C21 8.55228 20.5523 9 20 9H4C3.44772 9 3 8.55228 3 8ZM3 16C3 15.4477 3.44772 15 4 15H14C14.5523 15 15 15.4477 15 16C15 16.5523 14.5523 17 14 17H4C3.44772 17 3 16.5523 3 16Z" fill="currentColor"></path></svg>
            <h1 className='font-bold text-3xl'>Astro + SDE</h1>
        
        
        <img src="/images/dummy-profile-pic.png" className=' h-5/6 rounded-full border-2 border-slate-400 hover:border-black cursor-pointer' onClick={()=>{setMenuopen(!Menuopen)}}/>
        <div className={`absolute right-0 top-20 w-64 flex flex-col  border ${Menuopen ? '' : 'hidden'} p-4 rounded-sm shadow-lg`}>
          <div className='text-lg border-b p-4 hover:bg-slate-50 cursor-pointer'>Profile</div>
          <div className='text-lg p-4 hover:bg-slate-50 cursor-pointer'>Logout</div>

        </div>
        

    </div>
    </>
  )
}

export default Navbar