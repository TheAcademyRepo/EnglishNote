import api from "./api";

const engagement = {

    like: async (id) => {

        const response = await api.post(
            `/engagement/content/${id}/like/`
        );

        return response.data;
    },

    bookmark: async (id) => {

        const response = await api.post(
            `/engagement/content/${id}/bookmark/`
        );

        return response.data;
    },

    myBookmarks: async () => {

        const response = await api.get(
            "/engagement/bookmarks/"
        );

        return response.data;
    },

    share: async (id, platform = "link") => {

        const response = await api.post(
            `/engagement/content/${id}/share/`,
            { platform }
        );

        return response.data;
    },

    comments: async (id) => {

        const response = await api.get(
            `/engagement/content/${id}/comments/`
        );

        return response.data;
    },

    createComment: async (id, body, parent = null) => {

        const response = await api.post(
            `/engagement/content/${id}/comments/`,
            {
                body,
                parent
            }
        );

        return response.data;
    },

    replies: async (commentId) => {

        const response = await api.get(
            `/engagement/comments/${commentId}/replies/`
        );

        return response.data;
    },

    updateComment: async (commentId, body) => {

        const response = await api.patch(
            `/engagement/comments/${commentId}/`,
            { body }
        );

        return response.data;
    },

    deleteComment: async (commentId) => {

        const response = await api.delete(
            `/engagement/comments/${commentId}/`
        );

        return response.data;
    },

    summary: async (id) => {

        const response = await api.get(
            `/engagement/content/${id}/summary/`
        );

        return response.data;
    },

    report: async (data) => {

        const response = await api.post(
            "/engagement/reports/create/",
            data
        );

        return response.data;
    },

};

export default engagement;