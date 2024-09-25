import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import {LoginSchema} from '../utils/validation'

export const LoginForm: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(LoginSchema),
  });

  const onSubmit = async (data: any) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8080/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
        credentials: "include",
      });

      const result = await response.json();
      console.log(result);

      if (response.ok) {
        navigate("/");
      } else {
        setError(result.error || "Login failed.");
      }
    } catch (error) {
      setError("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-start justify-center bg-white text-black">
      <div className="w-full max-w-md p-8 space-y-6 border border-gray-300 rounded-lg shadow-lg mt-[6rem]" >
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

        <div className="text-center">
          <p>
            Don't have an account?{" "}
            <a href="/register" className="text-black underline">
              Register
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};
