    import { useAuth } from "../../context/AuthContext";

export default function EditorDashboard() {
    const { user } = useAuth();

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-3">
                Editor Dashboard
            </h1>

            <p>Welcome, {user?.username}.</p>

            <p className="text-gray-500 mt-2">
                Manage topics and lessons, review comments and handle reports.
            </p>
        </div>
    );
}