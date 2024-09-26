import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Home from "./pages/Home";
import { LoginForm } from "./pages/Login";
import { RegisterForm } from "./pages/Register";
import { AuthProvider, useAuth } from './AuthContext';
import { useEffect } from "react";
import Settings from "./pages/Settings";
import OtpInput from "./components/OtpInput";


const  AppContent : React.FC=()=> {
const {user}=useAuth();
const {vtoken}=useAuth();
const token  =user?.token;
  useEffect(()=>{},[user])
  

  return (
    
      <Router>
        <Routes>
          <Route path="/" element={token ? <Home/> : <LoginForm/>} />
          <Route path="/login" element={token ?  <Navigate to="/" />  :<LoginForm />} />
          <Route path="/register" element={token ? <Navigate to="/" /> :<RegisterForm />} />
          <Route path="/settings" element={token ? <Settings/>:<LoginForm/>} />
          <Route path="/auth/verify/:vtoken" element={!token && vtoken ? <OtpInput/> : <Navigate to={"/"}/>} />

        </Routes>
      </Router>
    
  );
}

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
