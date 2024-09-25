import { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { RegisterSchema } from "../utils/validation";
import { useNavigate } from "react-router-dom";
import { useAuth } from '../AuthContext'; // Import the AuthContext

export const RegisterForm = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const { register: registerUser } = useAuth(); // Use the register function from AuthContext

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(RegisterSchema),
  });

  const onSubmit = async (data: any) => {
    setError(null);
    try {
      await registerUser(data.username, data.email, data.password); // Call the register function
      navigate("/"); // Redirect after successful registration
    } catch (error: any) {
      setError(error.message || "Registration failed.");
    }
  };

  return (
    <div className="flex items-start justify-center h-screen">
      <div className="w-full max-w-md bg-white p-8 shadow mt-[6rem] rounded-xl">
        <h2 className="text-center text-2xl font-bold mb-6">Register</h2>
        {error && <p className="text-red-500 text-center">{error}</p>}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Full Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium">Full Name</label>
            <input
              id="name"
              type="text"
              {...register("username")}
              className="w-full border border-gray-300 p-2 rounded"
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
              className="w-full border border-gray-300 p-2 rounded"
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
              className="w-full border border-gray-300 p-2 rounded"
            />
            <p className="text-red-500 text-sm">{errors.password?.message}</p>
          </div>

          <button type="submit" className="w-full bg-black text-white p-2 rounded">
            Register
          </button>
        </form>

        <p className="text-center text-sm mt-4">
          Already have an account? <a href="/login" className="text-blue-500">Login</a>
        </p>
      </div>
    </div>
  );
};
