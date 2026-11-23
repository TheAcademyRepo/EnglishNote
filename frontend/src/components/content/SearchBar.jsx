import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function SearchBar() {
    const [query, setQuery] = useState("");
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!query.trim()) return;

        navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="flex gap-2 w-full max-w-xl"
        >
            <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search articles, posts and lessons..."
                className="flex-1 border p-3 rounded-lg"
            />

            <button className="bg-blue-600 text-white px-5 rounded-lg">
                Search
            </button>
        </form>
    );
}