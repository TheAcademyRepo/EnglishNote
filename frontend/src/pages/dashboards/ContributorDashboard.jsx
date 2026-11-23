import { useAuth } from "../../context/AuthContext";

export default function ContributorDashboard() {
    const { user } = useAuth();

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-3">
                Contributor Dashboard
            </h1>

            <p>Welcome, {user?.username}.</p>

            <p className="text-gray-500 mt-2">
                Create articles and submit them for editorial review.
            </p>
        </div>
    );
}