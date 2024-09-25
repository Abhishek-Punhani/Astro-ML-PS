import './App.css'
import HomePage from './components/HomePage'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'

function App() {


  return (
    <>
    <div className='flex flex-row fixed w-full -z-10'>
      <Sidebar/>
      <Navbar/>
      
      
      
     
      </div>
      <HomePage/>
    </>
  )
}

export default App
