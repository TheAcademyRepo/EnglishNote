import { useAuth } from "../../context/AuthContext";

export default function StudentDashboard() {
    const { user } = useAuth();

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-3">
                Student Dashboard
            </h1>

            <p>Welcome, {user?.username}.</p>

            <p className="text-gray-500 mt-2">
                Explore lessons, read articles, bookmark resources and follow authors.
            </p>
        </div>
    );
}