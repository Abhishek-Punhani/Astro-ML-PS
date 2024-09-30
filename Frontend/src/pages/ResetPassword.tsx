import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import Navbar from '../components/Navbar';

const ResetPassword: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { token, id } = useParams<{ token: string; id: string }>();
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const { forgotPassword } = useAuth();
  const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%&*?])[A-Za-z\d!@#$%&*?]{6,}$/;

  // Redirect if token or id is empty
  useEffect(() => {
    if (!token?.trim() || !id?.trim()) {
      navigate("/");
    }
  }, [token, id, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Check if the passwords match
    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match!");
      return;
    }

    if(regex.test(password)){
      setErrorMessage("");
    }else{
      setErrorMessage("Password must contain at least 6 characters, 1 uppercase, 1 lowercase, 1 number, and 1 special character");
      return;
    }

    // Reset error message if passwords match
    
    setLoading(true);

    try {
      await forgotPassword(token as string, password);
      navigate("/auth/mail-sent");
    } catch (error: any) {
      setErrorMessage(error.message || "Password reset failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
   <>
    <div className="h-full w-full flex items-center justify-center fadein">
      <div className="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0 min-w-[40%]">
        <div className="w-full p-6 border text-white font-unic rounded-lg shadow md:mt-0 sm:max-w-md sm:p-8">
          <h2 className="mb-1 text-xl text-center font-bold leading-tight tracking-tight md:text-2xl">
            Change Password
          </h2>
          <form className="mt-4 space-y-4 lg:mt-5 md:space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="password" className="block mb-2 text-sm font-medium">New Password</label>
              <input 
                type="password" 
                name="password" 
                id="password" 
                placeholder="••••••••" 
                className="border bg-transparent outline-none text-sm rounded-lg block w-full p-2.5" 
                required 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="confirm-password" className="block mb-2 text-sm font-medium ">Confirm Password</label>
              <input 
                type="password" 
                name="confirm-password" 
                id="confirm-password" 
                placeholder="••••••••" 
                className="border bg-transparent outline-none text-sm rounded-lg block w-full p-2.5" 
                required 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
            {errorMessage && <p className="text-red-500">{errorMessage}</p>}
            <button 
              type="submit" 
              disabled={loading}
              className="w-full text-white border hover:bg-rgb[(0,0,0,0.4)] bg-transparent font-medium rounded-lg text-sm px-5 py-2.5 text-center"
            >
              Reset Password
            </button>
          </form>
        </div>
      </div>
    </div></>
  );
};

export default ResetPassword;
