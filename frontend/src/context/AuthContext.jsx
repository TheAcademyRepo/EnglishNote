import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import auth from "../services/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const isAuthenticated = Boolean(user);

    const loadUser = async () => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            setUser(null);
            setLoading(false);
            return;
        }

        try {
            const data = await auth.me();
            setUser(data);
        } catch {
            setUser(null);
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadUser();

        const handleLogout = () => {
            setUser(null);
        };

        window.addEventListener("auth:logout", handleLogout);

        return () => {
            window.removeEventListener(
                "auth:logout",
                handleLogout
            );
        };
    }, []);

    const login = async (credentials) => {
        const data = await auth.login(credentials);

        const currentUser = await auth.me();

        setUser(currentUser);

        return currentUser;
    };

    const register = async (data) => {
        return await auth.register(data);
    };

    const logout = async () => {
        try {
            await auth.logout();
        } finally {
            setUser(null);
        }
    };

    const refreshUser = async () => {
        const data = await auth.me();
        setUser(data);
        return data;
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                isAuthenticated,
                login,
                register,
                logout,
                refreshUser,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}