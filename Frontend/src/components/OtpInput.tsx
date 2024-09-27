import React, { useState, useEffect, useRef } from 'react';
import Navbar from './Navbar';
import { useAuth } from '../AuthContext';
import { useNavigate, useParams } from 'react-router-dom';

const OTPForm: React.FC = () => {
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);
  const [otp, setOtp] = useState<string[]>(['', '', '', '','','']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const {verify}=useAuth();
  const {vtoken}=useParams<{vtoken:string}>();
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
    const { value } = e.target;
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1); // Accept only one digit
    setOtp(newOtp);

    if (value && index < inputsRef.current.length - 1) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (
      !/^[0-9]{1}$/.test(e.key) &&
      e.key !== 'Backspace' &&
      e.key !== 'Delete' &&
      e.key !== 'Tab' &&
      !e.metaKey
    ) {
      e.preventDefault();
    }

    if (e.key === 'Delete' || e.key === 'Backspace') {
      if (index > 0) {
        const newOtp = [...otp];
        newOtp[index] = '';
        setOtp(newOtp);
        inputsRef.current[index - 1]?.focus();
      }
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    if (/^\d{4}$/.test(pastedData)) {
      const pastedOtp = pastedData.split('');
      setOtp(pastedOtp);
      inputsRef.current[3]?.focus(); // focus last input
    }
  };

  const handleSubmit = async(e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
        await verify(Number(otp.join('')),vtoken as string);
        navigate("/");
    } catch (error: any) {
        setError(error.message || "Login failed.");
      } finally {
        setLoading(false);
      }
  };

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.select();
  };

  useEffect(() => {
    inputsRef.current[0]?.focus();
  }, []);

  return (
    <>
    <Navbar/>
    <div className="relative font-inter antialiased">
      <div className="relative min-h-screen flex flex-col justify-center bg-slate-50 overflow-hidden">
        <div className="w-full max-w-5xl mx-auto px-6 md:px-8 py-28">
          <div className="flex justify-center">
            <div className="max-w-lg mx-auto text-center bg-white px-6 sm:px-10 py-12 rounded-2xl shadow-lg">
              <header className="mb-10">
                <h1 className="text-3xl font-bold mb-5">OTP Verification</h1>
                <p className="text-[16px] text-slate-500">
                  Enter the 4-digit verification code that was sent to your email.
                </p>
              </header>

              <form id="otp-form" onSubmit={handleSubmit}>
                <div className="flex items-center justify-center gap-4">
                  {otp.map((digit, index) => (
                    <input
                      key={index}
                      ref={(el) => (inputsRef.current[index] = el)}
                      type="text"
                      className="w-16 h-16 text-center text-3xl font-extrabold text-slate-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-lg p-4 outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                      value={digit}
                      maxLength={1}
                      onChange={(e) => handleInputChange(e, index)}
                      onKeyDown={(e) => handleKeyDown(e, index)}
                      onFocus={handleFocus}
                      onPaste={handlePaste}
                      pattern="\d*"
                    />
                  ))}
                </div>
                {error && <p className="text-red-500">{error}</p>}
                <div className="max-w-[280px] mx-auto mt-6">
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full inline-flex justify-center whitespace-nowrap rounded-xl bg-indigo-500 px-4 py-3 text-base font-medium text-white shadow-md shadow-indigo-950/10 hover:bg-indigo-600 focus:outline-none focus:ring focus:ring-indigo-300 focus-visible:outline-none focus-visible:ring focus-visible:ring-indigo-300 transition-colors duration-150"
                  >
                   Proceed
                  </button>
                </div>
              </form>

              <div className="text-sm text-slate-500 mt-6">
                Didn't receive code?{' '}
                <a className="font-medium text-indigo-500 hover:text-indigo-600" href="#0">
                  Resend
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</>  );
};

export default OTPForm;
