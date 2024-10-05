import { useEffect, useState } from "react";
import { useAuth } from "../AuthContext";

interface SidebarProps {
  SidebarStatus: boolean;
}

const Sidebar = ({ SidebarStatus }: SidebarProps) => {
  const { user, getData } = useAuth();
  let array = user?.project_names || [];

  const [BarOpen, setBarOpen] = useState(false);

  useEffect(() => {
    setBarOpen(SidebarStatus);
  }, [SidebarStatus]);

  const handleChange = async (id: string) => {
    setBarOpen(!BarOpen);
    const res = await getData(user?.token as string, id);
    console.log(res);
  };

  return (
    <div
      className={`${
        BarOpen ? "translate-x-0" : "sm:-translate-x-80 -translate-x-full"
      } sm:w-80 w-full top-0 h-screen pb-4 flex flex-col font-unic font-bold overflow-scroll fixed transition-all ease-in-out delay-150 text-white z-10 lg:bg-transparent bg-[rgb(0,0,0,0.8)]`}>
      <div className="px-[20px] py-4 h-[81px] flex flex-row justify-between items-center pt-4"></div>
      <div className="py-8 px-4">
        <h1 className="text-2xl">Previous Projects</h1>
        <div className="list my-4 flex flex-col gap-2 ">
          {array.length === 0 ? (
            <h3 className="text-gray-400">Your Saved Results Appear Here</h3>
          ) : (
            array.map((item: any, index: any) => {
              return (
                <div
                  key={index}
                  className="w-full border py-2 px-2 rounded-lg cursor-pointer hover:bg-slate-600"
                  onClick={() => handleChange(item?.id)}>
                  Project: {item?.project_name}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
