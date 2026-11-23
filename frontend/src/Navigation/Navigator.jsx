import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Hero from "../assets/hero.png";
import { useAuth } from "../context/AuthContext";

export default function Navigator() {
    const [open, setOpen] = useState(false);

    const {
        user,
        loading,
        isAuthenticated,
        logout,
    } = useAuth();

    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();

        setOpen(false);
        navigate("/login");
    };

    return (
        <div>
            {!open && (
                <div
                    onClick={() => setOpen(true)}
                    className="text-white text-4xl bg-white/15 px-2 rounded-xl cursor-pointer"
                >
                    =
                </div>
            )}

            {open && (
                <div className="fixed inset-0 bg-blue-900 w-full h-full z-[10000]">

                    {/* CLOSE BUTTON */}

                    <div
                        onClick={() => setOpen(false)}
                        className="absolute right-5 top-5 text-gray-100 text-3xl bg-gray-200/50 p-2 rounded-xl cursor-pointer"
                    >
                        X
                    </div>


                    {/* USER */}

                    <div className="flex flex-col justify-center items-center gap-6 mt-10 text-gray-100">

                        <div className="flex flex-col justify-center items-center gap-2">

                            <img
                                src={Hero}
                                className="rounded-full bg-gray-200 w-[5rem] h-[5rem] object-cover"
                                alt="Profile"
                            />

                            {loading ? (
                                <div className="text-sm">
                                    Loading...
                                </div>
                            ) : isAuthenticated ? (
                                <div className="flex flex-col justify-center items-center leading-tight">

                                    <span className="font-bold text-xl">
                                        {user?.username}
                                    </span>

                                    <span className="text-sm">
                                        {user?.email}
                                    </span>

                                    {user?.email_verified && (
                                        <span className="text-green-300 text-sm mt-1">
                                            ✓ Email verified
                                        </span>
                                    )}

                                </div>
                            ) : (
                                <div className="flex flex-col justify-center items-center leading-tight">

                                    <span className="font-bold text-xl">
                                        Welcome
                                    </span>

                                    <span className="text-sm">
                                        Guest
                                    </span>

                                </div>
                            )}

                        </div>


                        {/* NAVIGATION */}

                        <div>
                            <ul className="flex flex-col items-center gap-5 text-lg">

                                <li>
                                    <Link
                                        to="/"
                                        onClick={() => setOpen(false)}
                                    >
                                        Home
                                    </Link>
                                </li>

                                <li>
                                    <Link
                                        to="/about"
                                        onClick={() => setOpen(false)}
                                    >
                                        About
                                    </Link>
                                </li>


                                {!isAuthenticated && (
                                    <>
                                        <li>
                                            <Link
                                                to="/login"
                                                onClick={() => setOpen(false)}
                                            >
                                                Login
                                            </Link>
                                        </li>

                                        <li>
                                            <Link
                                                to="/register"
                                                onClick={() => setOpen(false)}
                                            >
                                                Register
                                            </Link>
                                        </li>
                                    </>
                                )}


                                {isAuthenticated && (
                                    <>
                                        <li>
                                            <Link
                                                to="/Note"
                                                onClick={() => setOpen(false)}
                                            >
                                                My Notes
                                            </Link>
                                        </li>

                                        <li>
                                            <Link
                                                to="/change-password"
                                                onClick={() => setOpen(false)}
                                            >
                                                Change Password
                                            </Link>
                                        </li>

                                        <li>
                                            <button
                                                onClick={handleLogout}
                                                className="text-red-300"
                                            >
                                                Logout
                                            </button>
                                        </li>
                                    </>
                                )}

                            </ul>
                        </div>

                    </div>
                </div>
            )}
        </div>
    );
}