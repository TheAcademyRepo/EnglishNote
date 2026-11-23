import api from "./api";

const notifications = {

    getAll: async (params = {}) => {
        const response = await api.get(
            "/notifications/",
            { params }
        );

        return response.data;
    },

    getUnreadCount: async () => {
        const response = await api.get(
            "/notifications/unread-count/"
        );

        return response.data;
    },

    markRead: async (notificationId) => {
        const response = await api.post(
            `/notifications/${notificationId}/read/`
        );

        return response.data;
    },

    markAllRead: async () => {
        const response = await api.post(
            "/notifications/read-all/"
        );

        return response.data;
    },

    delete: async (notificationId) => {
        const response = await api.delete(
            `/notifications/${notificationId}/delete/`
        );

        return response.data;
    },

};

export default notifications;