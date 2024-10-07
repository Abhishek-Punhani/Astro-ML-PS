import { useEffect, useState } from "react";
import { useAuth } from "../AuthContext";
import { useNavigate } from "react-router-dom";

interface SidebarProps {
  SidebarStatus: boolean;
}

const Sidebar = ({ SidebarStatus }: SidebarProps) => {
  const { user, getData, setData } = useAuth();
  const array = user?.project_names || [];
  const navigate = useNavigate();

  const [BarOpen, setBarOpen] = useState(false);

  useEffect(() => {
    setBarOpen(SidebarStatus);
  }, [SidebarStatus]);

  const handleChange = async (id: string) => {
    setBarOpen(!BarOpen);
    const res: any = await getData(user?.token as string, id);
    console.log(res);
    const X = res["x"];
    const Y = res["y"];
    const MF = res["time_of_occurances"];
    const TOC = res["time_corresponding_peak_flux"];
    const left = res["left"];
    const right = res["right"];
    const leftx: number[] = [];
    const lefty: number[] = [];
    const rightx: number[] = [];
    const righty: number[] = [];

    left.forEach((ele: number) => {
      if (ele >= 0 && ele < X.length && ele < Y.length) {
        // Ensure index is valid
        leftx.push(X[ele]);
        lefty.push(Y[ele]);
      } else {
        console.warn(`Invalid index ${ele} in left array`);
      }
    });
    right.forEach((ele: number) => {
      if (ele >= 0 && ele < X.length && ele < Y.length) {
        // Ensure index is valid
        rightx.push(X[ele]);
        righty.push(Y[ele]);
      } else {
        console.warn(`Invalid index ${ele} in left array`);
      }
    });

    const plotData = [
      X,
      Y,
      MF,
      TOC,
      leftx,
      lefty,
      rightx,
      righty,
      left,
      right,
    ] as any[];
    setData(plotData);
    navigate(`history/${id}`);
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
