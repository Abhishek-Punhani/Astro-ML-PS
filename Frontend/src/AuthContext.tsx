import React, { createContext, useContext, useEffect, useState } from "react";
// import Cookies from 'js-cookie';


export interface User {
  id: string;
  email: string;
  username: string;
  token:string
}

interface AuthContextType {
  vtoken:string|null,
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  googleLogin: (email: string, username: string, googleId: string) => Promise<void>;
  logout: () => void;
  verify:(otp:number,token:string)=>Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null);

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

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setUser(JSON.parse(localStorage.getItem("user") || "null"));
    }
  }, []);

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
     return data.token;
    } else {
      throw new Error(data.error);
    }
  };


  const verify = async (otp: number, token: string) => {
    const response = await fetch("http://localhost:8080/auth/verify-otp", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ otp, token}),
    });
    const data = await response.json();
    if (response.ok && vtoken) {
      SetVtoken(null);
      localStorage.setItem("token", data.user.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
    } else {
      throw new Error(data.error);
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string,
  ) => {
    const response = await fetch(
      "http://localhost:8080/auth/register",
      {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      },
    );
    const data = await response.json();
    if (response.ok) {
      SetVtoken(data.token);
      return data.token;
    } else {
      throw new Error(data.error);
    }
  };

  const googleLogin = async (email: string, username: string, googleId: string) => {
    const response = await fetch("http://localhost:8080/auth/google-login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, username, googleId }),
    });
    const data = await response.json();
    console.log(data)
    if (response.ok) {
      SetVtoken(data.token);
      return data.token;
    } else {
      throw new Error(data.error);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ vtoken,user, login, register, logout ,googleLogin ,verify}}>
      {children}
    </AuthContext.Provider>
  );
};
