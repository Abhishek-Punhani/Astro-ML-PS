import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { LoginSchema } from "../utils/validation";
import { useAuth } from "../AuthContext";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { Link } from "react-router-dom";
import { GithubLoginButton } from "react-social-login-buttons";

interface GoogleUser {
  username: string;
  email: string;
  googleId: string;
}

export const LoginForm: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { login, googleLogin } = useAuth();
  const clientid = import.meta.env.REACT_APP_GOOGLE_CLIENT_ID as string;
  const gitclientID = import.meta.env.REACT_APP_GITHUB_CLIENT_ID as string;
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(LoginSchema),
  });

  const handleLogin = async (user: GoogleUser) => {
    setLoading(true);
    setError(null);

    try {
      const vtoken = await googleLogin(
        user.email,
        user.username,
        user.googleId
      );
      navigate(`/auth/verify/${vtoken}`);
    } catch (error: any) {
      setError(error.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  const GitHubLoginButton: React.FC = () => {
    const loginWithGitHub = () => {
      const redirectURI = "http://localhost:5173/auth/github/callback";
      window.location.href = `https://github.com/login/oauth/authorize?client_id=${gitclientID}&redirect_uri=${redirectURI}`;
    };

    return <GithubLoginButton onClick={loginWithGitHub}></GithubLoginButton>;
  };

  const onSubmit = async (data: any) => {
    setLoading(true);
    setError(null);

    try {
      const vtoken = await login(data.email, data.password);
      navigate(`/auth/verify/${vtoken}`);
    } catch (error: any) {
      setError(error.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="min-h-screen flex items-start justify-center text-white font-unic">
        <div className="w-full max-w-md p-8 space-y-6 border border-gray-300 fadein rounded-lg shadow-lg mt-[10rem]">
          <h2 className="text-center text-2xl font-bold">Login</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <div>
              <label className="block text-sm font-medium">Email</label>
              <input
                type="email"
                {...register("email")}
                className="w-full p-2 mt-1 border border-gray-300 rounded bg-transparent outline-none"
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
                className="w-full p-2 mt-1 border border-gray-300 rounded bg-transparent outline-none"
                placeholder="Enter your password"
              />
              {errors.password && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.password.message}
                </p>
              )}
            </div>
            {error && <p className="text-red-500">{error}</p>}
            <div>
              <a href="/auth/forgot-password">Forgot Password?</a>
            </div>
            <button
              type="submit"
              className="w-full p-2 text-white border rounded hover:bg-[rgb(0,0,0,0.4)]"
              disabled={loading}>
              {loading ? "Loading..." : "Login"}
            </button>
          </form>
          {/* Google login button */}
          <div className="w-full flex items-center justify-center">
            <GoogleOAuthProvider clientId={clientid}>
              <GoogleLogin
                onSuccess={(credentialResponse) => {
                  let decode = jwtDecode<any>(
                    credentialResponse.credential as string
                  );
                  let user: GoogleUser = {
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
          <div>
            <GitHubLoginButton />
          </div>
          <div className="text-center">
            <p>
              Don't have an account?{" "}
              <Link to="/register" className="text-white underline">
                Register
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
