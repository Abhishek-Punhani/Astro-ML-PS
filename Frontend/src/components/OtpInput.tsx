import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../AuthContext";
import { useNavigate, useParams } from "react-router-dom";
import { PulseLoader } from "react-spinners";
const OTPForm: React.FC = () => {
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);
  const [otp, setOtp] = useState<string[]>(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [timer, setTimer] = useState<number>(60);
  const { verify, resendOtp, reftoken } = useAuth();
  const { vtoken } = useParams<{ vtoken: string }>();
  const navigate = useNavigate();

  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer((prevTimer) => prevTimer - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timer]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    index: number
  ) => {
    const { value } = e.target;
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);

    if (value && index < inputsRef.current.length - 1) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>,
    index: number
  ) => {
    if (
      !/^[0-9]{1}$/.test(e.key) &&
      e.key !== "Backspace" &&
      e.key !== "Delete" &&
      e.key !== "Tab" &&
      !e.metaKey
    ) {
      e.preventDefault();
    }

    if (e.key === "Delete" || e.key === "Backspace") {
      if (index > 0) {
        const newOtp = [...otp];
        newOtp[index] = "";
        setOtp(newOtp);
        inputsRef.current[index - 1]?.focus();
      }
    }
    if (e.key === "Enter") {
      const form = document.getElementById("otp-form") as HTMLFormElement;
      form.requestSubmit(); // Submit the form
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").trim();

    // If the pasted data is 6 digits, split across inputs
    if (/^\d{6}$/.test(pastedData)) {
      const pastedOtp = pastedData.split("");
      setOtp(pastedOtp);
      inputsRef.current[5]?.focus(); // Focus on the last input field after pasting
    }
  };
  const handleresend = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>
  ) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await resendOtp(reftoken as string);
      navigate(`/auth/verify/${res}`);
      setOtp(["", "", "", "", "", ""]);
      setMsg("OTP sent Successfully!,check your mail");
    } catch (error: any) {
      setError(error.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    setError(null);

    try {
      await verify(Number(otp.join("")), vtoken as string);
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
      <div className="relative font-inter antialiased fadein">
        <div className="relative min-h-screen flex flex-col justify-center overflow-hidden">
          <div className="w-full max-w-5xl mx-auto px-6 md:px-8 py-28">
            <div className="flex justify-center">
              <div className="max-w-lg mx-auto text-center border text-white font-unic px-6 sm:px-10 py-12 rounded-2xl shadow-lg">
                <header className="mb-10">
                  <h1 className="text-3xl font-bold mb-5">OTP Verification</h1>
                  <p className="text-[16px] text-slate-500">
                    Enter the 6-digit verification code that was sent to your
                    email.
                  </p>
                </header>

                <form id="otp-form" onSubmit={handleSubmit}>
                  <div className="flex items-center justify-center gap-4">
                    {otp.map((digit, index) => (
                      <input
                        key={index}
                        ref={(el) => (inputsRef.current[index] = el)}
                        type="text"
                        className="w-16 h-16 text-center text-3xl font-extrabold text-white border bg-transparent hover:border-slate-200 appearance-none rounded-lg p-4 outline-none"
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
                  {msg && <p className="text-green-500">{msg}</p>}
                  <div className="max-w-[280px] mx-auto mt-6">
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full inline-flex justify-center whitespace-nowrap rounded-xl bg-transparent hover:bg-[rgb(0,0,0,0.4)] border px-4 py-3 text-lg font-medium text-white shadow-md shadow-indigo-950/10  transition-colors duration-150">
                      {loading ? (
                        <PulseLoader color="#9e9b9b" size={12} />
                      ) : (
                        "Proceed"
                      )}
                    </button>
                  </div>
                </form>

                <div className="text-sm text-slate-500 mt-6 mr-2">
                  Didn't receive code?{" "}
                  <button
                    className={`font-medium text-white ${timer > 0 || loading ? "text-gray-600" : "cursor-pointer hover:underline"}`}
                    type="button"
                    onClick={(e) => {
                      handleresend(e);
                      setTimer(60); // Reset the timer when OTP is resent
                    }}
                    disabled={loading || timer > 0}>
                    Resend
                  </button>
                  <span className="ml-3 text-gray-300">
                    {" "}
                    {timer > 0 && ` After ${timer} seconds`}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default OTPForm;
