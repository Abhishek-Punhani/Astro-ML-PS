import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export const GitHubCallback: React.FC = () => {
  const { githubLogin } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");

    if (code) {
      const handleCallback = async () => {
        const vtoken = await githubLogin(code);
        navigate(`/auth/verify/${vtoken}`);
      };

      handleCallback();
    } else {
      navigate("/login");
    }
  }, []);

  return (
    <div className="text-white flex items-center justify-center">
      Processing GitHub login...
    </div>
  );
};
