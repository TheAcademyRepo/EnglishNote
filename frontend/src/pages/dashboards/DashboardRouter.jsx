import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

import StudentDashboard from "./StudentDashboard";
import ContributorDashboard from "./ContributorDashboard";
import AuthorDashboard from "./AuthorDashboard";
import EditorDashboard from "./EditorDashboard";
import AdministratorDashboard from "./AdministratorDashboard";

export default function DashboardRouter() {
    const { user } = useAuth();

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    switch (user.role) {
        case "student":
            return <StudentDashboard />;

        case "contributor":
            return <ContributorDashboard />;

        case "author":
            return <AuthorDashboard />;

        case "editor":
            return <EditorDashboard />;

        case "administrator":
        case "super_administrator":
            return <AdministratorDashboard />;

        default:
            return <Navigate to="/login" replace />;
    }
}