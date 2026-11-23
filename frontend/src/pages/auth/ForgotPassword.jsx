import { useState } from "react";
import { Link } from "react-router-dom";
import auth from "../../services/auth";

export default function ForgotPassword() {
    const [email, setEmail] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        setMessage("");
        setError("");

        try {
            const data = await auth.forgotPassword({ email });

            setMessage(
                data.detail ||
                "If an account exists for this email, password reset instructions will be sent."
            );
        } catch {
            setError("Unable to process your request. Try again later.");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
            <form
                onSubmit={handleSubmit}
                className="bg-white p-8 rounded-xl shadow max-w-md w-full"
            >
                <h1 className="text-2xl font-bold mb-3">
                    Forgot Password?
                </h1>

                <p className="text-gray-500 mb-6">
                    Enter your email address to receive reset instructions.
                </p>

                {message && (
                    <p className="bg-green-100 text-green-700 p-3 rounded mb-4">
                        {message}
                    </p>
                )}

                {error && (
                    <p className="bg-red-100 text-red-700 p-3 rounded mb-4">
                        {error}
                    </p>
                )}

                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="Email address"
                    className="w-full border rounded-lg p-3 mb-4"
                />

                <button className="w-full bg-blue-600 text-white p-3 rounded-lg">
                    Send Reset Link
                </button>

                <Link to="/login" className="block mt-5 text-blue-600 text-center">
                    Back to Login
                </Link>
            </form>
        </div>
    );
}