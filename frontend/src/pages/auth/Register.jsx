import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Register() {
    const { register } = useAuth();

    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        password_confirmation: "",
    });

    const [message, setMessage] = useState("");
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

        setMessage("");
        setError("");
        setLoading(true);

        try {
            await register(form);

            setMessage(
                "Your account has been created. Check your email to verify your account."
            );

            setForm({
                username: "",
                email: "",
                password: "",
                password_confirmation: "",
            });

        } catch (err) {
            const data = err.response?.data;

            setError(
                typeof data === "object"
                    ? Object.entries(data)
                        .map(([field, messages]) =>
                            `${field}: ${
                                Array.isArray(messages)
                                    ? messages.join(", ")
                                    : messages
                            }`
                        )
                        .join(" | ")
                    : "Registration failed. Please try again."
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
                    Create Account
                </h1>

                <p className="text-gray-500 mb-6">
                    Join our learning community.
                </p>

                {message && (
                    <div className="bg-green-100 text-green-700 p-3 rounded-lg mb-4">
                        {message}
                    </div>
                )}

                {error && (
                    <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
                        {error}
                    </div>
                )}

                {[
                    ["username", "Username", "text"],
                    ["email", "Email address", "email"],
                    ["password", "Password", "password"],
                    [
                        "password_confirmation",
                        "Confirm password",
                        "password",
                    ],
                ].map(([name, label, type]) => (
                    <div key={name} className="mb-4">
                        <label className="block mb-2 font-medium">
                            {label}
                        </label>

                        <input
                            name={name}
                            type={type}
                            value={form[name]}
                            onChange={handleChange}
                            required
                            className="w-full border rounded-lg p-3"
                        />
                    </div>
                ))}

                <button
                    disabled={loading}
                    className="w-full bg-blue-600 text-white p-3 rounded-lg disabled:opacity-50"
                >
                    {loading ? "Creating account..." : "Register"}
                </button>

                <p className="mt-5 text-sm text-center">
                    Already registered?{" "}
                    <Link to="/login" className="text-blue-600">
                        Login
                    </Link>
                </p>
            </form>
        </div>
    );
}