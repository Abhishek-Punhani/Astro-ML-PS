import React, { createContext, useContext, useEffect, useState } from "react";
import { useToast } from "./components/toast-context";
export interface Project {
  id: string;
  project_name: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  token: string;
  project_names: Project[];
}

interface AuthContextType {
  data: any;
  setData: React.Dispatch<any>;
  vtoken: string | null;
  reftoken: string | null;
  user: User | null;
  access: "link" | "reset" | null;
  setAccess: React.Dispatch<React.SetStateAction<"link" | "reset" | null>>;
  login: (email: string, password: string) => Promise<void>;
  register: (
    username: string,
    email: string,
    password: string
  ) => Promise<void>;
  googleLogin: (
    email: string,
    username: string,
    authId: string
  ) => Promise<void>;
  logout: () => void;
  verify: (otp: number, token: string) => Promise<void>;
  sendOtp: (email: string) => Promise<void>;
  forgotPassword: (token: string, password: string) => Promise<void>;
  changePassword: (
    current_password: string,
    new_password: string,
    token: string
  ) => Promise<void>;
  verifyUserOtp: (otp: number, rtoken: string, token: string) => Promise<void>;
  resendOtp: (rtoken: string) => Promise<void>;
  analyze: (data: any, token: string) => Promise<void>;
  githubLogin: (code: string) => Promise<void>;
  saveResult: (data: any, token: string) => Promise<void>;
  getData: (token: string, id: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

// eslint-disable-next-line
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [vtoken, SetVtoken] = useState<string | null>(null);
  const [reftoken, SetReftoken] = useState<string | null>(null);
  const [access, setAccess] = useState<"link" | "reset" | null>(null);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setUser(JSON.parse(localStorage.getItem("user") || "null"));
    }
  }, []);
  const { open } = useToast();
  const SuccessfulToast = (messsage: string) => {
    console.log(messsage);
    open({
      message: {
        heading: "Success",
        content: messsage,
      },
      duration: 3000,
      position: "top-center",
      color: "success",
    });
  };
  const FailedToast = (messsage: string) => {
    console.log(messsage);
    open({
      message: {
        heading: "Failed",
        content: messsage,
      },
      duration: 3000,
      position: "top-center",
      color: "error",
    });
  };
  const InfoToast = (messsage: string) => {
    console.log(messsage);
    open({
      message: {
        heading: "Info",
        content: messsage,
      },
      duration: 3000,
      position: "top-center",
      color: "info",
    });
  };

  const login = async (email: string, password: string) => {
    const response = await fetch("http://localhost:8080/auth/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (response.ok) {
      SetVtoken(data.token);
      SetReftoken(data.rtoken);
      InfoToast("Otp sent check Your Mail");
      return data.token;
    } else {
      FailedToast(data.error);
      throw new Error(data.error);
    }
  };

  const verify = async (otp: number, token: string) => {
    if (user?.token) {
      return verifyUserOtp(otp, token, user.token);
    }
    const response = await fetch("http://localhost:8080/auth/verify-otp", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ otp, token }),
    });
    const data = await response.json();
    if (response.ok && vtoken) {
      SetVtoken(null);
      SetReftoken(null);
      localStorage.setItem("token", data.user.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      SuccessfulToast("Login Successfull");
      setUser(data.user);
    } else {
      FailedToast(data.error);
      throw new Error(data.error);
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string
  ) => {
    const response = await fetch("http://localhost:8080/auth/register", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });
    const data = await response.json();
    if (response.ok) {
      SetVtoken(data.token);
      SetReftoken(data.rtoken);
      InfoToast("Otp sent check Your Mail");
      return data.token;
    } else {
      FailedToast(data.error);
      throw new Error(data.error);
    }
  };

  const googleLogin = async (
    email: string,
    username: string,
    authId: string
  ) => {
    const response = await fetch("http://localhost:8080/auth/google-login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, username, authId }),
    });
    const data = await response.json();
    if (response.ok) {
      SetVtoken(data.token);
      SetReftoken(data.rtoken);
      InfoToast("Otp sent check Your Mail");
      return data.token;
    } else {
      FailedToast(data.error);
      throw new Error(data.error);
    }
  };

  const sendOtp = async (email: string) => {
    const response = await fetch("http://localhost:8080/auth/send-otp", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const data = await response.json();
    if (response.ok) {
      setAccess("link");
      InfoToast("Link sent check Your Mail");
      return;
    } else {
      FailedToast(data.error);
      throw new Error(data.error);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    SuccessfulToast("Logout Successfull");
    setUser(null);
  };

  const forgotPassword = async (token: string, password: string) => {
    const response = await fetch("http://localhost:8080/auth/forgot-password", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password }),
    });
    const data = await response.json();
    console.log(data);
    if (response.ok) {
      setAccess("reset");
    } else {
      throw new Error(data.error);
    }
  };

  const changePassword = async (
    current_password: string,
    new_password: string,
    token: string
  ) => {
    console.log(current_password, new_password, token);
    const response = await fetch("http://localhost:5000/user/change-password", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ current_password, new_password }),
    });
    const data = await response.json();
    console.log(data);
    if (response.ok) {
      SetVtoken(data.token);
      SetReftoken(data.rtoken);
      InfoToast("Otp sent check Your Mail");
      return data.token;
    } else {
      FailedToast(data.error);
      throw new Error(data.error);
    }
  };

  const verifyUserOtp = async (otp: number, rtoken: string, token: string) => {
    const response = await fetch(
      "http://localhost:5000/user/verify-change-password",
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ otp, rtoken }),
      }
    );
    const data = await response.json();
    if (response.ok && vtoken) {
      SuccessfulToast("Password Changed Successfully");
      SetVtoken(null);
    } else {
      FailedToast(data.error);
      throw new Error(data.error);
    }
  };

  const analyze = async (data: any, token: string) => {
    const response = await fetch("http://localhost:5000/user/analyze", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ data }),
    });
    const res = await response.json();
    if (response.ok) {
      return res;
    } else {
      throw new Error(res.error);
    }
  };

  const resendOtp = async (ref_token: string) => {
    if (user?.token) {
      const response = await fetch(
        "http://localhost:5000/user/resend-change-otp",
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${user?.token}`,
          },
          body: JSON.stringify({ ref_token }),
        }
      );
      const data = await response.json();
      if (response.ok && vtoken && reftoken) {
        SetVtoken(data.token);
        SetReftoken(data.rtoken);
        InfoToast("Otp sent check Your Mail");
        return data.token;
      } else {
        FailedToast("Something Went Wrong !");
        throw new Error("Something Went Wrong !");
      }
    }
    const response = await fetch("http://localhost:8080/auth/resend-otp", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ref_token }),
    });
    const data = await response.json();
    if (response.ok && vtoken && reftoken) {
      SetVtoken(data.token);
      SetReftoken(data.rtoken);
      return data.token;
    } else {
      throw new Error("Something Went Wrong !");
    }
  };

  const githubLogin = async (code: string) => {
    const response = await fetch("http://localhost:8080/auth/github/callback", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await response.json();
    if (response.ok) {
      SetVtoken(data.token);
      SetReftoken(data.rtoken);
      InfoToast("Otp sent check Your Mail");
      return data.token;
    } else {
      FailedToast(data.error);
      throw new Error(data.error);
    }
  };

  const saveResult = async (data: any, token: string) => {
    const response = await fetch("http://localhost:5000/user/save", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ data }),
    });
    const res = await response.json();
    console.log(res);
    if (response.ok) {
      if (res?.data) {
        InfoToast(`Project is already saved as ${res.data}`);
      }
      if (user && res.project_name) {
        const user_projects = user?.project_names || [];
        const project_names = [...user_projects, res.project_name];
        setUser({ ...user, project_names });
        InfoToast("Project Saved Successfully!");
      }
      return res;
    } else {
      throw new Error(res.error);
    }
  };

  const getData = async (token: string, id: string) => {
    const response = await fetch(
      `http://localhost:5000/user/get-project/${id}`,
      {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      }
    );
    const res = await response.json();
    if (response.ok) {
      return res.data;
    } else {
      throw new Error(res.error);
    }
  };
  return (
    <AuthContext.Provider
      value={{
        reftoken,
        vtoken,
        user,
        access,
        setAccess,
        login,
        register,
        logout,
        googleLogin,
        verify,
        sendOtp,
        forgotPassword,
        changePassword,
        verifyUserOtp,
        resendOtp,
        analyze,
        githubLogin,
        saveResult,
        getData,
        data,
        setData,
      }}>
      {children}
    </AuthContext.Provider>
  );
};
