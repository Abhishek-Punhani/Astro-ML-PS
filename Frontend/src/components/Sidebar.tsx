const Sidebar = () => {
  let array = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
  return (
    
    <div className='w-full h-screen py-4 border-r flex flex-col overflow-scroll'>
        <div className='border-b border-slate-100 px-4 pb-4 mx-auto'>
        <button className='border px-4 py-2 h-12 rounded-lg'>+ New Project</button>
        </div>
        <div className='py-8 px-4'>
            <h1>Previous Projects</h1>
            <div className="list my-4 flex flex-col gap-2">
                {array.map((item, index) => {
                    return (<div key={index} className='w-full border py-2 px-2 rounded-lg'>
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