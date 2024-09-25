import { useNavigate } from "react-router-dom"
import { useAuth } from "../AuthContext"


const Navbar = () => {
  const navigate=useNavigate();
  const {logout}=useAuth()
  const handleLogout=()=>{
    logout();
    navigate("/")
  }
  return (
    <nav className='h-20 w-full flex justify-between items-center px-8 border-b border-slate-100'>
        
        
        
            <h1 className='font-bold text-3xl'>Astro + SDE</h1>
        
        
        <img src="/images/dummy-profile-pic.png" className=' h-5/6 rounded-full border-2 border-slate-400 '/>
        <button onClick={handleLogout}>Logout</button>

    </nav>
  )
}

export default Navbar