import { useState } from "react";
import { useAuth } from "../AuthContext";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
const Settings = () => {
  const [Page, setPage] = useState("Account");
  const { user } = useAuth();
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm();
  const onsubmit = (data: any) => {
    if (data.username != user?.username || data.email != user?.email) {
      console.log(data);
    }
  };
  const handleChangePassword = () => {
    navigate("/settings/change-password");
  };
  return (
    <div>
      <div className=" mt-20 w-full flex justify-center items-center py-8 font-unic text-white fadein">
        <div
          className="w-4/6 rounded-xl border shadow flex flex-row"
          style={{ height: "80vh" }}>
          <div className="h-full w-1/4 border-r flex flex-col gap-2 py-2 px-2">
            <div
              className={`w-full py-4 px-4 text-lg  rounded-lg ${
                Page == "Account" ? "border-b" : "border-b border-white"
              } cursor-pointer`}
              onClick={() => setPage("Account")}>
              Account and Security
            </div>
            {/* <div className={`w-full py-4 px-4 text-lg  rounded-lg ${Page == 'Theme'? 'bg-slate-50 border-b':'border-b border-white'} cursor-pointer`} onClick={()=>{setPage('Theme')}}>Theme</div> */}
          </div>

          {Page == "Account" && (
            <form
              className="flex flex-col justify-between h-full w-3/4 items-center"
              onSubmit={handleSubmit(onsubmit)}>
              {" "}
              <div className="h-full w-full flex flex-col">
                <div className="flex flex-row items-center w-full justify-between py-6 px-8 border-b">
                  <h1 className="text-white">Username:</h1>
                  <input
                    type="text"
                    className="w-2/5 text-center border p-2 bg-transparent outline-none rounded-lg text-lg"
                    defaultValue={user?.username}
                    {...register("username")}
                  />
                </div>
                <div className="flex flex-row items-center w-full justify-between py-6 px-8 border-b">
                  <h1 className="text-white">Email:</h1>
                  <input
                    type="text"
                    className="w-2/5 text-center border p-2 rounded-lg outline-none bg-transparent text-lg bg-slate-50"
                    defaultValue={user?.email}
                    {...register("email")}
                  />
                </div>
                <div className="flex flex-row items-center w-full justify-between py-6 px-8 border-b">
                  <h1 className="text-white">Password:</h1>
                  <div
                    className="w-2/5 text-center text-lg border p-2 rounded-lg bg-transparent shadow cursor-pointer"
                    onClick={handleChangePassword}>
                    Change Password
                  </div>
                </div>
              </div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="my-6 border shadow rounded-lg p-2 w-28 ">
                Save
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
