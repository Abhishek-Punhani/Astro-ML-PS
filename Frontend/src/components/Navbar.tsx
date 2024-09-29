
import React,{useRef, useState} from 'react'
import Sidebar from './Sidebar'
import { useNavigate } from "react-router-dom"
import { useAuth } from "../AuthContext"
import { RefObject, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useLocation } from 'react-router-dom'

const useClickOutside = (
  ref: RefObject<HTMLElement | undefined>,
  ref2: RefObject<HTMLElement | undefined>,
  callback: () => void
) => {
  const handleClick = (event: MouseEvent) => {
    if (ref.current && !ref.current.contains(event.target as HTMLElement) && ref2.current && !ref2.current.contains(event.target as HTMLElement)) {
      callback()
    }
  }

  useEffect(() => {
    document.addEventListener('click', handleClick)

    return () => {
      document.removeEventListener('click', handleClick)
    }
  })
}

const Navbar = () => {
  const location = useLocation();
  const path = location.pathname;
  const [Menuopen, setMenuopen] = useState(false)
  const [SideBarOpen, setSideBarOpen] = useState(false)
  const [navmenu, setnavmenu] = useState(false)
  const navigate=useNavigate();
  const {logout}=useAuth();
  const SidebarRef = useRef<HTMLDivElement>(null);
  const SidebarRef2 = useRef<HTMLImageElement>(null);
  const NavMenueRef = useRef<HTMLDivElement>(null);
  const MenuBurgerRef = useRef<HTMLDivElement>(null);
  useClickOutside(SidebarRef,SidebarRef2, () => {
    setMenuopen(false)
  });
  useClickOutside(NavMenueRef,MenuBurgerRef,()=>{
    setnavmenu(false);
  })
  const handleLogout=()=>{
    logout();
    navigate("/")
  }
  return (
    <>
    {useAuth().user && path == "/analyser"&&<Sidebar SidebarStatus={SideBarOpen}/>}
    <div className='navbar h-20 w-full bg-[rgb(0,0,0,0.2)] flex justify-between items-center px-4  fixed top-0 transition-width ease-in-out delay-150 z-10 right-0  text-white font-unic'>

        
        

        <div className='flex flex-row gap-4'>
        {useAuth().user && path == "/analyser"&&<svg width="44" height="44" viewBox="0 0 24 24" fill="#FFFFFF" xmlns="http://www.w3.org/2000/svg" className="icon-lg mx-2 text-token-text-secondary cursor-pointer hover:bg-slate-900 rounded-full p-2 block " onClick={()=>{setSideBarOpen(!SideBarOpen)}}><path fill-rule="evenodd" clip-rule="evenodd" d="M3 8C3 7.44772 3.44772 7 4 7H20C20.5523 7 21 7.44772 21 8C21 8.55228 20.5523 9 20 9H4C3.44772 9 3 8.55228 3 8ZM3 16C3 15.4477 3.44772 15 4 15H14C14.5523 15 15 15.4477 15 16C15 16.5523 14.5523 17 14 17H4C3.44772 17 3 16.5523 3 16Z" fill="#FFFFFF"></path></svg>}
            <h1 className='font-bold text-4xl text-white font-unic'>MOONANALYSER</h1>
        
            </div>
  
        <div className='flex flex-row h-full items-center gap-4'>
        <div className='lg:flex flex-row gap-8 px-4 justify-between items-center hidden'>
          <Link to='/' className='text-xl cursor-pointer hover:underline'>Home</Link>
          <Link to='/analyser' className='text-xl cursor-pointer hover:underline'>Analyser</Link>
          <Link to='/about' className='text-xl cursor-pointer hover:underline'>About Us</Link></div>
        
        <div className='lg:hidden block cursor-pointer hover:bg-slate-900 rounded-full'  onClick={()=>{setnavmenu(!navmenu)}} ref={MenuBurgerRef}>
        <svg viewBox="0 0 24 24" width='44' height='44' fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0" className=''></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M5 8H13.75M5 12H19M10.25 16L19 16" stroke="#eeeeec" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg></div>
        {useAuth().user ?<><img src="/images/Profile2.svg" className=' h-14 rounded-full cursor-pointer' onClick={()=>{setMenuopen(!Menuopen)}} ref={SidebarRef2}/>
        
        <div className={`absolute right-0 top-20 w-64 flex flex-col ${Menuopen ? '' : 'hidden'} flex-col absolute top-20 w-56 items-center justify-around py-4 rounded-lg px-4 z-20 right-0 gap-2 bg-[rgb(0,0,0,0.4)]`} ref={SidebarRef}>

        

          <Link to={path == '/settings'?'/':'/settings'} className='text-lg border-b p-4  cursor-pointer hover:underline'>Settings</Link>
          <div className='text-lg p-4 hover:underline cursor-pointer' onClick={handleLogout}>Logout</div>

        </div></>:<Link to = '/login'><button className='text-lg w-28 py-2 px-4 rounded-full border bg-white text-black hover:bg-transparent hover:text-white'>Login</button></Link>}</div>
        <div className={`lg:hidden ${navmenu?'flex':'hidden'} flex-col absolute top-20 w-56 items-center justify-around py-4 rounded-lg px-4 z-20 right-0 bg-[rgb(0,0,0,0.4)]`} ref={NavMenueRef}>
        <Link to='/' className='text-xl cursor-pointer hover:underline w-2/3 border-b text-center py-4'>Home</Link>
          <Link to='/analyser' className='text-xl cursor-pointer hover:underline w-2/3 border-b  text-center py-4'>Analyser</Link>
          <Link to='/about' className='text-xl cursor-pointer hover:underline w-2/3 text-center py-4'>About Us</Link></div>
       
        
    </div>
    
    </>

 

  )
}

export default Navbar