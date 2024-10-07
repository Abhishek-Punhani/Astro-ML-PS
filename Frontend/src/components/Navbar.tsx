import { useRef, useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { Link, useLocation } from "react-router-dom";

const useClickOutside = (
  ref: React.RefObject<HTMLElement | undefined>,
  ref2: React.RefObject<HTMLElement | undefined>,
  callback: () => void
) => {
  const handleClick = (event: MouseEvent) => {
    if (
      ref.current &&
      !ref.current.contains(event.target as HTMLElement) &&
      ref2.current &&
      !ref2.current.contains(event.target as HTMLElement)
    ) {
      callback();
    }
  };

  useEffect(() => {
    document.addEventListener("click", handleClick);
    return () => {
      document.removeEventListener("click", handleClick);
    };
    // eslint-disable-next-line
  }, []);
};

const Navbar = () => {
  const location = useLocation();
  const path = location.pathname;
  const [menuOpen, setMenuOpen] = useState(false);
  const [sideBarOpen, setSideBarOpen] = useState(false);
  const [navMenuOpen, setNavMenuOpen] = useState(false);
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const profileMenuRef = useRef<HTMLDivElement>(null);
  const profileIconRef = useRef<HTMLImageElement>(null);
  const navMenuRef = useRef<HTMLDivElement>(null);
  const menuBurgerRef = useRef<HTMLDivElement>(null);
  const sideBarRef = useRef<HTMLDivElement>(null);
  const sideBarButtonRef = useRef<HTMLDivElement>(null);
  useClickOutside(profileMenuRef, profileIconRef, () => {
    setMenuOpen(false);
  });

  useClickOutside(navMenuRef, menuBurgerRef, () => {
    setNavMenuOpen(false);
  });
  useClickOutside(sideBarRef, sideBarButtonRef, () => {
    setSideBarOpen(false);
  });

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <>
      <div ref={sideBarRef}>
        {user && path === "/analyser" && (
          <Sidebar SidebarStatus={sideBarOpen} />
        )}
      </div>
      <div className="navbar h-20 w-full bg-[rgb(0,0,0,0.2)] flex justify-between items-center px-4 fixed top-0 z-10 text-white font-unic">
        <div className="flex flex-row gap-4">
          {user && path === "/analyser" && (
            <div ref={sideBarButtonRef}>
              <svg
                width="44"
                height="44"
                viewBox="0 0 24 24"
                fill="#FFFFFF"
                xmlns="http://www.w3.org/2000/svg"
                className="icon-lg mx-2 cursor-pointer hover:bg-slate-900 rounded-full p-2"
                onClick={() => setSideBarOpen(!sideBarOpen)}>
                <path
                  fillRule="evenodd"
                  clipRule="evenodd"
                  d="M3 8C3 7.44772 3.44772 7 4 7H20C20.5523 7 21 7.44772 21 8C21 8.55228 20.5523 9 20 9H4C3.44772 9 3 8.55228 3 8ZM3 16C3 15.4477 3.44772 15 4 15H14C14.5523 15 15 15.4477 15 16C15 16.5523 14.5523 17 14 17H4C3.44772 17 3 16.5523 3 16Z"
                  fill="#FFFFFF"></path>
              </svg>
            </div>
          )}
          <h1
            className="font-bold text-4xl cursor-pointer"
            onClick={() => navigate("/")}>
            MOONANALYSER
          </h1>
        </div>

        <div className="flex flex-row h-full items-center gap-4">
          <div className="lg:flex hidden flex-row gap-8 px-4">
            <Link to="/" className="text-xl cursor-pointer hover:underline">
              Home
            </Link>
            <Link
              to="/analyser"
              className="text-xl cursor-pointer hover:underline">
              Analyser
            </Link>
            <Link
              to="/about"
              className="text-xl cursor-pointer hover:underline">
              About Us
            </Link>
          </div>

          <div
            className="lg:hidden block cursor-pointer hover:bg-slate-900 rounded-full"
            onClick={() => setNavMenuOpen(!navMenuOpen)}
            ref={menuBurgerRef}>
            <svg
              viewBox="0 0 24 24"
              width="44"
              height="44"
              fill="none"
              xmlns="http://www.w3.org/2000/svg">
              <path
                d="M5 8H13.75M5 12H19M10.25 16L19 16"
                stroke="#eeeeec"
                strokeLinecap="round"
                strokeLinejoin="round"></path>
            </svg>
          </div>

          {user ? (
            <>
              <img
                src="/images/Profile2.svg"
                className="h-14 rounded-full cursor-pointer"
                onClick={() => setMenuOpen(!menuOpen)}
                ref={profileIconRef}
              />
              <div
                className={`absolute top-20 w-56 flex flex-col py-4 px-4 items-center justify-center gap-2 z-20 bg-[rgb(0,0,0,0.4)] rounded-lg right-0 ${
                  menuOpen ? "" : "hidden"
                }`}
                ref={profileMenuRef}>
                <div onClick={() => setMenuOpen(false)} className="p-4">
                  <Link
                    to={path === "/settings" ? "/" : "/settings"}
                    className="text-xl border-b p-4 hover:underline">
                    Settings
                  </Link>
                </div>
                <div
                  className="text-xl p-4 hover:underline cursor-pointer"
                  onClick={() => {
                    handleLogout();
                    setMenuOpen(false);
                    setNavMenuOpen(false);
                  }}>
                  Logout
                </div>
              </div>
            </>
          ) : (
            <Link to="/login">
              <button className="text-lg w-28 py-2 px-4 rounded-full border bg-white text-black hover:bg-transparent hover:text-white">
                Login
              </button>
            </Link>
          )}
        </div>

        <div
          className={`lg:hidden flex-col absolute top-20 w-56 py-4 px-4 gap-4 z-20 bg-[rgb(0,0,0,0.4)] rounded-lg right-0 ${
            navMenuOpen ? "flex" : "hidden"
          }`}
          ref={navMenuRef}>
          <Link to="/" className="text-xl border-b py-4 hover:underline">
            Home
          </Link>
          <Link
            to="/analyser"
            className="text-xl border-b py-4 hover:underline">
            Analyser
          </Link>
          <Link to="/about" className="text-xl py-4 hover:underline">
            About Us
          </Link>
        </div>
      </div>
    </>
  );
};

export default Navbar;
