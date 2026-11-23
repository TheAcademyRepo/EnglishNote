import {
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import VerifyEmail from "./pages/auth/VerifyEmail";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import ChangePassword from "./pages/auth/ChangePassword";
import AcceptInvitation from "./pages/auth/AcceptInvitation";
import PublicContent from "./pages/content/PublicContent";
import CreateContent from "./pages/content/CreateContent";
import ContentDetails from "./pages/content/ContentDetails";

import DashboardRouter from "./pages/dashboards/DashboardRouter";
import SearchResults from "./pages/content/SearchResults";

export default function App() {
    return (
        <Routes>
            {/* Public authentication routes */}

            <Route path="/login" element={<Login />} />

            <Route path="/register" element={<Register />} />

            <Route
                path="/verify-email"
                element={<VerifyEmail />}
            />

            <Route
                path="/forgot-password"
                element={<ForgotPassword />}
            />

            <Route
                path="/reset-password"
                element={<ResetPassword />}
            />

            {/* Authenticated routes */}

            <Route element={<ProtectedRoute />}>
                <Route
                    path="/dashboard"
                    element={<DashboardRouter />}
                />

                <Route
                    path="/change-password"
                    element={<ChangePassword />}
                />

                <Route
                    path="/accept-invitation"
                    element={<AcceptInvitation />}
                />
            </Route>

            <Route
                path="/"
                element={<Navigate to="/dashboard" replace />}
            />

            <Route
                path="*"
                element={<Navigate to="/" replace />}
            />
            <Route
    path="/explore"
    element={<PublicContent />}
/>

<Route
    path="/content/:id"
    element={<ContentDetails />}
/>
<Route
    path="/search"
    element={<SearchResults />}
/>

<Route element={<ProtectedRoute />}>
    <Route
        path="/create-content"
        element={<CreateContent />}
    />
</Route>
        </Routes>
    );
}