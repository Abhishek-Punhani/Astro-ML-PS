import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

const MailSuccess = () => {
  const { access } = useAuth();
  const navigate = useNavigate();
  if (access == null) {
    navigate("/");
  }
  return (
    <>
      <div className="py-20 h-screen w-screen flex flex-col items-center justify-center fadein">
        <div className="container mx-auto">
          <div className="flex justify-center">
            <div className="lg:w-1/2 w-full">
              {/* Success Inner */}
              <div className="text-center p-10 border rounded-lg text-white font-unic shadow-md">
                <h1 className="text-6xl font-bold text-white">
                  <i className="fa fa-envelope"></i>
                  <span className="block text-xl font-semibold text-white mt-5">
                    {access === "link"
                      ? "Password Reset Link Sent!"
                      : "Password Reset Successfully!"}
                  </span>
                </h1>
                <p className="py-6 text-white">
                  {access === "link"
                    ? "Please check your email for a link to reset your password. If you don't receive it in a few minutes, check your spam folder or try again."
                    : "Your password has been reset successfully. You can now log in with your new password."}
                </p>
                <div className="mx-auto h-[8rem] w-[8rem] rounded-full">
                  {access === "link" ? (
                    <img
                      src="/images/check.svg"
                      className="h-full w-full rounded-full "
                      alt="check"
                    />
                  ) : (
                    <a
                      type="button"
                      href="/login"
                      className="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center">
                      Login
                    </a>
                  )}
                </div>
              </div>
              {/* End Success Inner */}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default MailSuccess;
