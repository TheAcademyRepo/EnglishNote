import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

let refreshing = false;
let waitingRequests = [];

const processQueue = (error, token = null) => {
    waitingRequests.forEach((request) => {
        if (error) {
            request.reject(error);
        } else {
            request.resolve(token);
        }
    });

    waitingRequests = [];
};

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

api.interceptors.response.use(
    (response) => response,

    async (error) => {
        const originalRequest = error.config;

        if (
            error.response?.status !== 401 ||
            originalRequest._retry ||
            originalRequest.url?.includes("/auth/login/") ||
            originalRequest.url?.includes("/auth/refresh/") ||
            originalRequest.url?.includes("/auth/register/")
        ) {
            return Promise.reject(error);
        }

        const refreshToken = localStorage.getItem("refresh_token");

        if (!refreshToken) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.dispatchEvent(new Event("auth:logout"));

            return Promise.reject(error);
        }

        if (refreshing) {
            return new Promise((resolve, reject) => {
                waitingRequests.push({ resolve, reject });
            }).then((newToken) => {
                originalRequest.headers.Authorization =
                    `Bearer ${newToken}`;

                return api(originalRequest);
            });
        }

        originalRequest._retry = true;
        refreshing = true;

        try {
            const response = await axios.post(
                `${import.meta.env.VITE_API_BASE_URL}/auth/refresh/`,
                { refresh: refreshToken }
            );

            const newAccessToken = response.data.access;

            localStorage.setItem("access_token", newAccessToken);

            if (response.data.refresh) {
                localStorage.setItem(
                    "refresh_token",
                    response.data.refresh
                );
            }

            processQueue(null, newAccessToken);

            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;

            return api(originalRequest);

        } catch (refreshError) {
            processQueue(refreshError);

            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");

            window.dispatchEvent(new Event("auth:logout"));

            return Promise.reject(refreshError);

        } finally {
            refreshing = false;
        }
    }
);

export default api;