import { useAuth } from "../../context/AuthContext";
import ContentEditor from "../../components/content/ContentEditor";

export default function AuthorDashboard() {
    const { user } = useAuth();

    return (
        <main className="max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-bold mb-3">
                Author Dashboard
            </h1>

            <p className="text-gray-500 mb-8">
                Welcome, {user?.username}.
            </p>

            <ContentEditor />
        </main>
    );
}