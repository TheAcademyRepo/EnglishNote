import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
    const navigate = useNavigate();
    const { login } = useAuth();

    const [form, setForm] = useState({
        username: "",
        password: "",
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError("");
        setLoading(true);

        try {
            await login(form);
            navigate("/dashboard", { replace: true });

        } catch (err) {
            const data = err.response?.data;

            setError(
                data?.detail ||
                data?.non_field_errors?.[0] ||
                "Unable to log in. Check your credentials and try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
            <form
                onSubmit={handleSubmit}
                className="w-full max-w-md bg-white p-8 rounded-2xl shadow"
            >
                <h1 className="text-3xl font-bold mb-2">
                    Welcome Back
                </h1>

                <p className="text-gray-500 mb-6">
                    Sign in to continue learning.
                </p>

                {error && (
                    <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
                        {error}
                    </div>
                )}

                <label className="block mb-2 font-medium">
                    Username
                </label>

                <input
                    type="text"
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    required
                    className="w-full border rounded-lg p-3 mb-4"
                    placeholder="Enter your username"
                />

                <label className="block mb-2 font-medium">
                    Password
                </label>

                <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    required
                    className="w-full border rounded-lg p-3 mb-5"
                    placeholder="Enter your password"
                />

                <button
                    disabled={loading}
                    className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                    {loading ? "Signing in..." : "Login"}
                </button>

                <div className="flex justify-between text-sm mt-5">
                    <Link to="/forgot-password" className="text-blue-600">
                        Forgot password?
                    </Link>

                    <Link to="/register" className="text-blue-600">
                        Create account
                    </Link>
                </div>
            </form>
        </div>
    );
}