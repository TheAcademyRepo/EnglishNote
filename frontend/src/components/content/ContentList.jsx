import { useEffect, useState } from "react";
import publishing from "../../services/publishing";
import ContentCard from "./ContentCard";

export default function ContentList({ filters = {} }) {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;

        const loadContent = async () => {
            setLoading(true);
            setError("");

            try {
                const data = await publishing.getPublicContent(filters);

                const results = Array.isArray(data)
                    ? data
                    : data.results || [];

                if (active) {
                    setItems(results);
                }

            } catch {
                if (active) {
                    setError("Unable to load content.");
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        };

        loadContent();

        return () => {
            active = false;
        };
    }, [JSON.stringify(filters)]);

    if (loading) {
        return <p className="p-6">Loading content...</p>;
    }

    if (error) {
        return <p className="p-6 text-red-600">{error}</p>;
    }

    if (!items.length) {
        return <p className="p-6">No content available yet.</p>;
    }

    return (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item) => (
                <ContentCard key={item.id} item={item} />
            ))}
        </div>
    );
}