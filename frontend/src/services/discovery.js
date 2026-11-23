import api from "./api";

const discovery = {

    search: async (params = {}) => {

        const response = await api.get(
            "/discovery/search/",
            { params }
        );

        return response.data;
    },

    trending: async (params = {}) => {

        const response = await api.get(
            "/discovery/trending/",
            { params }
        );

        return response.data;
    },

    getFilters: async () => {

        const response = await api.get(
            "/discovery/filters/"
        );

        return response.data;
    },

};

export default discovery;