import api from "./api";

const publishing = {

    publicList: async (params = {}) => {

        const response = await api.get(
            "/publishing/public/",
            { params }
        );

        return response.data;
    },

    manage: async (params = {}) => {

        const response = await api.get(
            "/publishing/manage/",
            { params }
        );

        return response.data;
    },

    create: async (data) => {

        const response = await api.post(
            "/publishing/manage/",
            data
        );

        return response.data;
    },

    detail: async (slug) => {

        const response = await api.get(
            `/publishing/manage/${slug}/`
        );

        return response.data;
    },

    update: async (slug, data) => {

        const response = await api.patch(
            `/publishing/manage/${slug}/`,
            data
        );

        return response.data;
    },

    delete: async (slug) => {

        const response = await api.delete(
            `/publishing/manage/${slug}/`
        );

        return response.data;
    },

    submit: async (id) => {

        const response = await api.post(
            `/publishing/${id}/submit/`
        );

        return response.data;
    },

    review: async (id, data) => {

        const response = await api.post(
            `/publishing/${id}/review/`,
            data
        );

        return response.data;
    },

    publish: async (id) => {

        const response = await api.post(
            `/publishing/${id}/publish/`
        );

        return response.data;
    },

    recordView: async (id) => {

        const response = await api.post(
            `/publishing/${id}/view/`
        );

        return response.data;
    },

    versions: async (id) => {

        const response = await api.get(
            `/publishing/${id}/versions/`
        );

        return response.data;
    },

};

export default publishing;