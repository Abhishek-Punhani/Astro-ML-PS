import { Link } from 'react-router-dom'
const Landing = () => {
  return (
    <div style={{backgroundImage:"url(/images/background.jpeg)"}} className='h-screen w-screen bg-no-repeat bg-cover bg-center flex flex-row items-end justify-end font-unic'>
       
        <div className='flex flex-col justify-center w-1/2 h-full gap-12 px-16 fadein'>
            
            <h2 className='text-5xl font-semibold text-white'>ANALYSE THE COSMOS</h2>
            <p className='text-white text-lg'>Lorem ipsum dolor sit amet consectetur adipisicing elit. Molestiae corrupti ad quam magnam voluptatum explicabo quasi voluptate, totam sapiente eum blanditiis fugiat nesciunt tenetur quisquam.</p>
            <Link to='/analyser'><button className='rounded-full w-48 p-2 text-xl text-white border-2 border-white'>Proceed</button></Link>
            </div>

    </div>
  )
}

export default Landing