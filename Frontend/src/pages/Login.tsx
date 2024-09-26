import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { LoginSchema } from '../utils/validation';
import { useAuth } from '../AuthContext';
import Navbar from "../components/Navbar";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";

interface GoogleUser {
  username:string,
  email : string,
  googleId:string
}

export const LoginForm: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { login ,googleLogin} = useAuth(); 
  const clientid = "75797648124-eiu57qr3appp3c9lpq5a7kufret0tjo9.apps.googleusercontent.com";
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(LoginSchema),
  });

  const handleLogin=async(user : GoogleUser)=>{
    await googleLogin(user.email,user.username,user.googleId);
  }

  const onSubmit = async (data: any) => {
    setLoading(true);
    setError(null);

    try {
      await login(data.email, data.password); // Call the login function
      navigate("/"); // Redirect after successful login
    } catch (error: any) {
      setError(error.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
   <>
   <Navbar/>
    <div className="min-h-screen flex items-start justify-center bg-white text-black">
      <div className="w-full max-w-md p-8 space-y-6 border border-gray-300 rounded-lg shadow-lg mt-[10rem]" >
        <h2 className="text-center text-2xl font-bold">Login</h2>
        {error && <p className="text-red-500">{error}</p>}
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium">Email</label>
            <input
              type="email"
              {...register("email")}
              className="w-full p-2 mt-1 border border-gray-300 rounded"
              placeholder="Enter your email"
            />
            {errors.email && (
              <p className="text-red-500 text-xs mt-1">
                {errors.email.message}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium">Password</label>
            <input
              type="password"
              {...register("password")}
              className="w-full p-2 mt-1 border border-gray-300 rounded"
              placeholder="Enter your password"
            />
            {errors.password && (
              <p className="text-red-500 text-xs mt-1">
                {errors.password.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            className="w-full p-2 text-white bg-black rounded hover:bg-gray-800"
            disabled={loading}
          >
            {loading ? "Loading..." : "Login"}
          </button>
        </form>
           {/* Google login button */}
        <div className="w-full flex items-center justify-center">
          <GoogleOAuthProvider clientId={clientid}>
            <GoogleLogin
              onSuccess={(credentialResponse) => {
                let decode = jwtDecode<any>(credentialResponse.credential as string);
                let user : GoogleUser = {
                  username: decode.name,
                  email: decode.email,
                  googleId: decode.sub.toString(),
                };
                handleLogin(user);
              }}
              onError={() => {
                console.log("Login Failed");
              }}
            />
          </GoogleOAuthProvider>
        </div>
        <div className="text-center">
          <p>
            Don't have an account?{" "}
            <a href="/register" className="text-black underline">
              Register
            </a>
          </p>
        </div>
      </div>
    </div></>
  );
};
