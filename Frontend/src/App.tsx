import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Home from "./pages/Home";
import { LoginForm } from "./pages/Login";
import { RegisterForm } from "./pages/Register";
import { AuthProvider, useAuth } from "./AuthContext";
import { useEffect } from "react";
import Settings from "./pages/Settings";
import Landing from "./pages/Landing";
import "./App.css";
import Navbar from "./components/Navbar";
import OtpInput from "./components/OtpInput";

import ForgotPasswordEmail from "./pages/ForgotPassword";
import MailSuccess from "./pages/mailsent";
import ResetPassword from "./pages/ResetPassword";
import ChangePassword from "./pages/ChangePassword";

const AppContent: React.FC = () => {
  const { user, vtoken, access } = useAuth();
  const token = user?.token;
  useEffect(() => {}, [user]);

  return (
    <div
      className="h-screen fixed w-screen bg-no-repeat bg-cover bg-center"
      style={{ backgroundImage: "url('/images/homeBg1.jpg')" }}>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/analyser" element={token ? <Home /> : <LoginForm />} />
          <Route
            path="/login"
            element={token ? <Navigate to="/" /> : <LoginForm />}
          />
          <Route
            path="/register"
            element={token ? <Navigate to="/" /> : <RegisterForm />}
          />
          <Route
            path="/settings"
            element={token ? <Settings /> : <LoginForm />}
          />
          <Route
            path="/auth/verify/:vtoken"
            element={vtoken ? <OtpInput /> : <Navigate to={"/"} />}
          />
          <Route
            path="/auth/newcredentials/:id/:token"
            element={<ResetPassword />}
          />
          <Route
            path="/auth/forgot-password"
            element={<ForgotPasswordEmail />}
          />
          <Route
            path="/auth/mail-sent"
            element={access ? <MailSuccess /> : <Navigate to="/" />}
          />
          <Route
            path="/settings/change-password"
            element={token ? <ChangePassword /> : <Navigate to={"/"} />}
          />
        </Routes>
      </Router>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
