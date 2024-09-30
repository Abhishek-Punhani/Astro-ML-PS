import { useEffect, useState } from "react";

interface SidebarProps {
  SidebarStatus: boolean;
}

const Sidebar = ({ SidebarStatus }: SidebarProps) => {
  let array = [1, 2, 3, 4, 5, 6];
  const [BarOpen, setBarOpen] = useState(false);
  useEffect(() => {
    setBarOpen(SidebarStatus);
  }, [SidebarStatus]);

  return (
    <>
      <div
        className={`${
          BarOpen ? "translate-x-0" : "sm:-translate-x-80 -translate-x-full"
        }  sm:w-80 w-full top-0 h-screen pb-4 flex flex-col font-unic font-bold overflow-scroll fixed transition-all ease-in-out delay-150 text-white z-10 lg:bg-transparent bg-[rgb(0,0,0,0.8)]`}>
        <div className=" px-[20px] py-4  h-[81px] flex flex-row justify-between items-center pt-4"></div>
        <div className="py-8 px-4">
          <h1>Previous Projects</h1>
          <div className="list my-4 flex flex-col gap-2 ">
            {array.map((item, index) => {
              return (
                <div
                  key={index}
                  className="w-full border py-2 px-2 rounded-lg cursor-pointer hover:bg-slate-600">
                  Project {item}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
