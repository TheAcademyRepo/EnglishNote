import { useState } from "react";
import publishing from "../../services/publishing";

export default function ContentEditor() {
    const [form, setForm] = useState({
        content_content_type: "blog",
        title: "",
        excerpt: "",
        body: "",
    });

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setMessage("");
        setError("");
        setLoading(true);

        try {
            await publishing.createContent(form);

            setMessage("Content saved successfully.");

            setForm({
                content_content_type: "blog",
                title: "",
                excerpt: "",
                body: "",
            });

        } catch (err) {
            const data = err.response?.data;

            setError(
                data?.detail ||
                "Unable to save content. Check your permissions and form fields."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="bg-white p-6 rounded-xl shadow space-y-5"
        >
            <h2 className="text-2xl font-bold">
                Create Content
            </h2>

            {message && (
                <p className="bg-green-100 text-green-700 p-3 rounded">
                    {message}
                </p>
            )}

            {error && (
                <p className="bg-red-100 text-red-700 p-3 rounded">
                    {error}
                </p>
            )}

            <select
                name="content_type"
                value={form.content_type}
                onChange={handleChange}
                className="w-full border p-3 rounded-lg"
            >
                <option value="blog">Blog Article</option>
                <option value="post">Post</option>
                <option value="daily">Daily Post</option>
            </select>

            <input
                name="title"
                value={form.title}
                onChange={handleChange}
                placeholder="Content title"
                required
                className="w-full border p-3 rounded-lg"
            />

            <textarea
                name="excerpt"
                value={form.excerpt}
                onChange={handleChange}
                placeholder="Short description"
                rows="3"
                className="w-full border p-3 rounded-lg"
            />

            <textarea
                name="body"
                value={form.body}
                onChange={handleChange}
                placeholder="Write your content..."
                rows="12"
                required
                className="w-full border p-3 rounded-lg"
            />

            <button
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg disabled:opacity-50"
            >
                {loading ? "Saving..." : "Save Content"}
            </button>
        </form>
    );
}