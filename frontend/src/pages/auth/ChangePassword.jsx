import { useState } from "react";
import auth from "../../services/auth";

export default function ChangePassword() {
    const [form, setForm] = useState({
        old_password: "",
        new_password: "",
        new_password_confirmation: "",
    });

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        setMessage("");
        setError("");

        try {
            await auth.changePassword(form);

            setMessage("Your password has been changed.");

            setForm({
                old_password: "",
                new_password: "",
                new_password_confirmation: "",
            });

        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to change your password."
            );
        }
    };

    return (
        <div className="max-w-lg mx-auto p-6">
            <h1 className="text-2xl font-bold mb-6">
                Change Password
            </h1>

            {message && <p className="text-green-600 mb-4">{message}</p>}
            {error && <p className="text-red-600 mb-4">{error}</p>}

            <form onSubmit={handleSubmit} className="space-y-4">
                {[
                    ["old_password", "Current password"],
                    ["new_password", "New password"],
                    [
                        "new_password_confirmation",
                        "Confirm new password",
                    ],
                ].map(([name, label]) => (
                    <input
                        key={name}
                        type="password"
                        required
                        placeholder={label}
                        value={form[name]}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                [name]: e.target.value,
                            })
                        }
                        className="w-full border p-3 rounded-lg"
                    />
                ))}

                <button className="bg-blue-600 text-white px-6 py-3 rounded-lg">
                    Update Password
                </button>
            </form>
        </div>
    );
}