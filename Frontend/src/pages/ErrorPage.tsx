import { Link } from "react-router-dom";

const ErrorPage = () => {
  return (
    <div className="text-white h-screen w-screen flex flex-col items-center justify-center font-unic gap-4">
      <h1 className="text-9xl font-bold">404</h1>
      <h2 className="text-3xl font-semibold">Page not found</h2>
      <Link
        to="/"
        className="p-4 text-2xl text-black bg-white my-10 rounded-full">
        Go to Home
      </Link>
    </div>
  );
};

export default ErrorPage;
