import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import auth from "../../services/auth";
import { useAuth } from "../../context/AuthContext";

export default function AcceptInvitation() {
    const [params] = useSearchParams();
    const { refreshUser } = useAuth();

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleAccept = async () => {
        setMessage("");
        setError("");

        const token = params.get("token");

        if (!token) {
            setError("Invalid invitation link.");
            return;
        }

        try {
            await auth.acceptInvitation({ token });

            await refreshUser();

            setMessage("Your invitation has been accepted. Your role is now active.");

        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to accept this invitation."
            );
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
            <div className="bg-white p-8 rounded-xl shadow max-w-md w-full text-center">
                <h1 className="text-2xl font-bold mb-4">
                    Role Invitation
                </h1>

                {message && (
                    <p className="text-green-600 mb-4">{message}</p>
                )}

                {error && (
                    <p className="text-red-600 mb-4">{error}</p>
                )}

                <button
                    onClick={handleAccept}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg"
                >
                    Accept Invitation
                </button>

                <Link to="/dashboard" className="block mt-5 text-blue-600">
                    Return to Dashboard
                </Link>
            </div>
        </div>
    );
}