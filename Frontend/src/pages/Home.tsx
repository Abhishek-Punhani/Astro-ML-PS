import HomePage from "../components/HomePage"
import Navbar from "../components/Navbar"
import Sidebar from "../components/Sidebar"

export const Home : React.FC =()=> {
  return (
   <>
   <div>
    <Navbar/>
   <div className="flex justify-center items-center">
    <div className="w-[25%]">
    <Sidebar/>
    </div>
    <HomePage/>
    </div>
   </div>
   </>
  )
}

export default Home