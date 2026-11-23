import api from "./api";

export async function login(username, password) {
    const response = await api.post("/auth/login/", {
        username,
        password,
    });

    return response.data;
}

export async function getCurrentUser() {
    const response = await api.get("/auth/me/");
    return response.data;
}

export async function logout(refreshToken) {
    const response = await api.post("/auth/logout/", {
        refresh: refreshToken,
    });

    return response.data;
}

export async function register(username, email, password) {
    const response = await api.post("/auth/register/", {
        username,
        email,
        password,
    });

    return response.data;
}

export async function changePassword(oldPassword, newPassword) {
    const response = await api.post("/auth/change-password/", {
        old_password: oldPassword,
        new_password: newPassword,
    });

    return response.data;
}

export async function forgotPassword(email) {
    const response = await api.post("/auth/forgot-password/", {
        email,
    });

    return response.data;
}

export async function resetPassword(userId, token, newPassword) {
    const response = await api.post("/auth/reset-password/", {
        user_id: userId,
        token,
        new_password: newPassword,
    });

    return response.data;
}

export async function verifyEmail(userId, token) {
    const response = await api.post("/auth/verify-email/", {
        user_id: userId,
        token,
    });

    return response.data;
}