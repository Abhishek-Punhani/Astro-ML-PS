import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from 'yup';
import { useAuth } from "../AuthContext";
const ForgotPasswordEmail = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const {sendOtp}=useAuth();
    const {
        register,
        handleSubmit,
        formState: { errors },
      } = useForm({
        resolver: yupResolver(yup.object({
            email: yup.string()
              .required("Email is required")
              .email("Invalid email address!"),
          })),
      });
      const onSubmit = async (data: any) => {
        setLoading(true);
        setError(null);
        try {
          await sendOtp(data.email)
           navigate("/auth/mail-sent")
          
        } catch (error: any) {
          setError(error.message || "Login failed.");
        } finally {
          setLoading(false);
        }
      };
  return (
   <>
    <div className="flex justify-center items-center h-screen">
      <div className="w-full max-w-sm">
        <div className="border text-white font-unic shadow-lg rounded-lg p-6">
          <div className="text-center mb-6">
            <h3 className="text-4xl">
              <i className="fa fa-lock"></i>
            </h3>
            <h2 className="text-2xl font-bold">Forgot Password?</h2>
            <p className="text-gray-500 mt-5" >Please enter the email address that you used to register, and we will send you a link to reset your password via Email.</p>
          </div>
          <form  role="form"  className="space-y-6" onSubmit={handleSubmit(onSubmit)} >
            <div >
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                  <i className="fa fa-envelope text-white"></i>
                </span>
               <div>
               <input
                  id="email"
                  placeholder="Email address"
                  className="form-input w-full pl-10 p-2.5 border border-gray-300 rounded-md bg-transparent outline-none"
                  type="email"
                  {...register("email")}
                  required
                />
                {errors.email && (
              <p className="text-red-500 text-xs mt-1">
                {errors.email.message}
              </p>
            )}
                
               </div>
              </div>
            </div>
            {error && <p className="text-red-500">{error}</p>}
            <div>
              <button
                name="recover-submit"
                className="w-full text-white border hover:bg-rgb[(0,0,0,0.4)] bg-transparent font-medium rounded-lg text-sm px-5 py-2.5 text-center"
                type="submit"
                disabled={loading}
              >Reset Password</button>
            </div>

          </form>
        </div>
      </div>
    </div>
   </>
  );
};

export default ForgotPasswordEmail;
