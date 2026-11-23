import api from "./api";

const content = {
    // Subjects
    getSubjects: async (params = {}) => {
        const response = await api.get("/subjects/", { params });
        return response.data;
    },

    // Topics under a subject
    getTopics: async (subjectId, params = {}) => {
        const response = await api.get(
            `/subjects/${subjectId}/topics/`,
            { params }
        );

        return response.data;
    },

    // Lessons under a topic
    getLessons: async (topicId, params = {}) => {
        const response = await api.get(
            `/topics/${topicId}/lessons/`,
            { params }
        );

        return response.data;
    },

    // Single lesson
    getLesson: async (lessonId) => {
        const response = await api.get(
            `/lessons/${lessonId}/`
        );

        return response.data;
    },

    // Existing posts
    getPosts: async (params = {}) => {
        const response = await api.get("/posts/", { params });
        return response.data;
    },

    // Existing categories
    getCategories: async () => {
        const response = await api.get("/categories/");
        return response.data;
    },
};

export default content;