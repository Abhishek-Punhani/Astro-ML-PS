import { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { RegisterSchema } from "../utils/validation";
import { useNavigate } from "react-router-dom";
import { useAuth } from '../AuthContext'; // Import the AuthContext
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { Link } from "react-router-dom";
interface GoogleUser {
  username:string,
  email : string,
  googleId:string
}

export const RegisterForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { register: registerUser ,googleLogin } = useAuth();
  const clientid = import.meta.env.REACT_APP_GOOGLE_CLIENT_ID as string;

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(RegisterSchema),
  });
  const handleLogin=async(user : GoogleUser)=>{
   
    setLoading(true);
    setError(null);

    try {
      const vtoken= await googleLogin(user.email,user.username,user.googleId);
      navigate(`/auth/verify/${vtoken}`); 
    } catch (error: any) {
      setError(error.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  const onSubmit = async (data: any) => {
    setError(null);
    try {
      const vtoken=await registerUser(data.username, data.email, data.password); 
      navigate(`/auth/verify/${vtoken}`); 
    } catch (error: any) {
      setError(error.message || "Registration failed.");
    }
  };

  return (
    <>
    
    <div className="flex items-start justify-center h-screen">
      <div className="w-full max-w-md bg-transparent text-white border font-unic p-8 shadow mt-[10rem] rounded-xl fadein">
        <h2 className="text-center text-2xl font-bold mb-6">Register</h2>
      
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Full Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium">Full Name</label>
            <input
              id="name"
              type="text"
              {...register("username")}
              className="w-full border border-gray-300 p-2 rounded bg-transparent text-white outline-none"
            />
            <p className="text-red-500 text-sm">{errors.username?.message}</p>
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium">Email Address</label>
            <input
              id="email"
              type="email"
              {...register("email")}
              className="w-full border border-gray-300 p-2 rounded bg-transparent text-white outline-none"
            />
            <p className="text-red-500 text-sm">{errors.email?.message}</p>
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium">Password</label>
            <input
              id="password"
              type="password"
              {...register("password")}
              className="w-full border border-gray-300 p-2 rounded bg-transparent text-white outline-none"
            />
            <p className="text-red-500 text-sm">{errors.password?.message}</p>
          </div>
          

          <button type="submit" className="w-full hover:bg-[rgb(0,0,0,0.4)] bg-transparent border text-white p-2 rounded">
          {loading ? "Loading..." : "Register"}
          </button>
        </form>
        {error && <><br /><p className="text-red-500 text-center">{error}</p></>}

          {/* Google login button */}
          <br />
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

        <p className="text-center mt-4">
          Already have an account? <Link to="/login" className="text-white underline">Login</Link>
        </p>
      </div>
    </div>
</>  );
};
