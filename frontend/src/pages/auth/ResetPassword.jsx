import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import auth from "../../services/auth";

export default function ResetPassword() {
    const [params] = useSearchParams();

    const [form, setForm] = useState({
        password: "",
        password_confirmation: "",
    });

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError("");
        setMessage("");

        try {
            await auth.resetPassword({
                user_id: params.get("user_id"),
                token: params.get("token"),
                ...form,
            });

            setMessage("Your password has been changed successfully.");

        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to reset your password. The link may have expired."
            );
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
            <form
                onSubmit={handleSubmit}
                className="bg-white p-8 rounded-xl shadow max-w-md w-full"
            >
                <h1 className="text-2xl font-bold mb-6">
                    Reset Password
                </h1>

                {message && (
                    <p className="text-green-600 mb-4">{message}</p>
                )}

                {error && (
                    <p className="text-red-600 mb-4">{error}</p>
                )}

                <input
                    type="password"
                    placeholder="New password"
                    required
                    value={form.password}
                    onChange={(e) =>
                        setForm({ ...form, password: e.target.value })
                    }
                    className="w-full border p-3 rounded-lg mb-4"
                />

                <input
                    type="password"
                    placeholder="Confirm new password"
                    required
                    value={form.password_confirmation}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            password_confirmation: e.target.value,
                        })
                    }
                    className="w-full border p-3 rounded-lg mb-4"
                />

                <button className="w-full bg-blue-600 text-white p-3 rounded-lg">
                    Reset Password
                </button>

                <Link to="/login" className="block mt-5 text-blue-600 text-center">
                    Back to Login
                </Link>
            </form>
        </div>
    );
}