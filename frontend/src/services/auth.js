import api from "./api";

const auth = {
    register: async (data) => {
        const response = await api.post("/auth/register/", data);
        return response.data;
    },

    login: async (data) => {
        const response = await api.post("/auth/login/", data);

        if (response.data.access) {
            localStorage.setItem(
                "access_token",
                response.data.access
            );
        }

        if (response.data.refresh) {
            localStorage.setItem(
                "refresh_token",
                response.data.refresh
            );
        }

        return response.data;
    },

    me: async () => {
        const response = await api.get("/auth/me/");
        return response.data;
    },

    logout: async () => {
        const refresh = localStorage.getItem("refresh_token");

        try {
            if (refresh) {
                await api.post("/auth/logout/", { refresh });
            }
        } finally {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
        }
    },

    verifyEmail: async (data) => {
        const response = await api.post(
            "/auth/verify-email/",
            data
        );

        return response.data;
    },

    resendVerification: async (data) => {
        const response = await api.post(
            "/auth/resend-verification/",
            data
        );

        return response.data;
    },

    forgotPassword: async (data) => {
        const response = await api.post(
            "/auth/forgot-password/",
            data
        );

        return response.data;
    },

    resetPassword: async (data) => {
        const response = await api.post(
            "/auth/reset-password/",
            data
        );

        return response.data;
    },

    changePassword: async (data) => {
        const response = await api.post(
            "/auth/change-password/",
            data
        );

        return response.data;
    },

    acceptInvitation: async (data) => {
        const response = await api.post(
            "/auth/invitations/accept/",
            data
        );

        return response.data;
    },

    createInvitation: async (data) => {
        const response = await api.post(
            "/auth/invitations/",
            data
        );

        return response.data;
    },
};

export default auth;