import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import auth from "../../services/auth";

export default function VerifyEmail() {
    const [params] = useSearchParams();

    const [message, setMessage] = useState("Verifying your email...");
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        const verify = async () => {
            const user_id = params.get("user_id");
            const token = params.get("token");

            if (!user_id || !token) {
                setMessage("Invalid verification link.");
                return;
            }

            try {
                await auth.verifyEmail({ user_id, token });

                setSuccess(true);
                setMessage("Your email has been verified successfully.");

            } catch (error) {
                setMessage(
                    error.response?.data?.detail ||
                    "This verification link is invalid or has expired."
                );
            }
        };

        verify();
    }, [params]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
            <div className="bg-white p-8 rounded-xl shadow max-w-md w-full text-center">
                <h1 className="text-2xl font-bold mb-4">
                    Email Verification
                </h1>

                <p className={success ? "text-green-600" : "text-gray-600"}>
                    {message}
                </p>

                <Link
                    to="/login"
                    className="inline-block mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg"
                >
                    Continue to Login
                </Link>
            </div>
        </div>
    );
}