import HomePage from "../components/HomePage"
import Sidebar from "../components/Sidebar"

export const Home : React.FC =()=> {
  return (
   <>
    <div className="flex justify-center items-center">
    <div className="w-[25%]">
    <Sidebar/>
    </div>
    <HomePage/>
    </div>
   </>
  )
}

export default Home