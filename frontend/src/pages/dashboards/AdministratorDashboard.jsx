import { useAuth } from "../../context/AuthContext";

export default function AdministratorDashboard() {
    const { user } = useAuth();

    const isSuperAdmin =
        user?.role === "super_administrator";

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-3">
                {isSuperAdmin
                    ? "Super Administrator Dashboard"
                    : "Administrator Dashboard"}
            </h1>

            <p>Welcome, {user?.username}.</p>

            <p className="text-gray-500 mt-2">
                Manage users, roles, categories, subjects and platform content.
            </p>

            {isSuperAdmin && (
                <div className="mt-6 p-4 bg-purple-100 rounded-lg">
                    <h2 className="font-bold">
                        Super Administrator Access
                    </h2>

                    <p>
                        You have access to system-wide administration and security controls.
                    </p>
                </div>
            )}
        </div>
    );
}