import { useEffect, useState } from "react";

import { useSearchParams, Link } from "react-router-dom";

import discovery from "../../services/discovery";

export default function SearchResults() {

    const [searchParams, setSearchParams] = useSearchParams();

    const [results, setResults] = useState([]);

    const [filters, setFilters] = useState({
        content_types: [],
        categories: [],
        topics: [],
        ordering: []
    });

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    const query = searchParams.get("q") || "";

    const currentPage = Number(
        searchParams.get("page") || 1
    );

    const contentType = searchParams.get("type") || "";

    const category = searchParams.get("category") || "";

    const topic = searchParams.get("topic") || "";

    const ordering = searchParams.get("ordering") || "newest";

    const [pagination, setPagination] = useState({
        count: 0,
        next: null,
        previous: null
    });

    useEffect(() => {

        discovery.getFilters()
            .then(setFilters)
            .catch(() => {
                setError("Unable to load search filters.");
            });

    }, []);

    useEffect(() => {

        let active = true;

        const loadResults = async () => {

            setLoading(true);
            setError("");

            try {

                const data = await discovery.search({

                    q: query,

                    page: currentPage,

                    type: contentType || undefined,

                    category: category || undefined,

                    topic: topic || undefined,

                    ordering,

                    page_size: 12

                });

                if (!active) return;

                setResults(
                    data.results || []
                );

                setPagination({

                    count: data.count || 0,

                    next: data.next,

                    previous: data.previous

                });

            } catch (error) {

                if (active) {

                    setError(
                        error.response?.data?.detail ||
                        "Unable to search content."
                    );

                }

            } finally {

                if (active) {
                    setLoading(false);
                }

            }

        };

        loadResults();

        return () => {
            active = false;
        };

    }, [
        query,
        currentPage,
        contentType,
        category,
        topic,
        ordering
    ]);

    const updateFilter = (key, value) => {

        const next = new URLSearchParams(searchParams);

        if (value) {
            next.set(key, value);
        } else {
            next.delete(key);
        }

        next.delete("page");

        setSearchParams(next);

    };

    const changePage = (page) => {

        const next = new URLSearchParams(searchParams);

        next.set("page", String(page));

        setSearchParams(next);

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    };

    return (

        <main className="max-w-7xl mx-auto px-5 py-10">

            <h1 className="text-3xl font-bold mb-2">
                Search Results
            </h1>

            <p className="text-gray-500 mb-7">
                Results for: {query || "All content"}
            </p>

            <div className="grid md:grid-cols-4 gap-3 mb-8">

                <select
                    value={contentType}
                    onChange={e =>
                        updateFilter("type", e.target.value)
                    }
                    className="border p-3 rounded-lg"
                >

                    <option value="">
                        All content types
                    </option>

                    {filters.content_types.map(item => (

                        <option
                            key={item.value}
                            value={item.value}
                        >
                            {item.label}
                        </option>

                    ))}

                </select>

                <select
                    value={category}
                    onChange={e =>
                        updateFilter("category", e.target.value)
                    }
                    className="border p-3 rounded-lg"
                >

                    <option value="">
                        All categories
                    </option>

                    {filters.categories.map(item => (

                        <option
                            key={item.id}
                            value={item.slug}
                        >
                            {item.name}
                        </option>

                    ))}

                </select>

                <select
                    value={topic}
                    onChange={e =>
                        updateFilter("topic", e.target.value)
                    }
                    className="border p-3 rounded-lg"
                >

                    <option value="">
                        All topics
                    </option>

                    {filters.topics.map(item => (

                        <option
                            key={item.id}
                            value={item.slug}
                        >
                            {item.name}
                        </option>

                    ))}

                </select>

                <select
                    value={ordering}
                    onChange={e =>
                        updateFilter("ordering", e.target.value)
                    }
                    className="border p-3 rounded-lg"
                >

                    <option value="newest">
                        Newest
                    </option>

                    <option value="oldest">
                        Oldest
                    </option>

                    <option value="most_viewed">
                        Most viewed
                    </option>

                    <option value="title">
                        Title A-Z
                    </option>

                </select>

            </div>

            {loading && (

                <p className="py-10 text-center">
                    Searching...
                </p>

            )}

            {error && (

                <p className="text-red-600 py-5">
                    {error}
                </p>

            )}

            {!loading && !error && results.length === 0 && (

                <p className="text-center py-10 text-gray-500">
                    No matching content was found.
                </p>

            )}

            {!loading && results.length > 0 && (

                <>

                    <p className="text-sm text-gray-500 mb-5">
                        {pagination.count} result(s) found
                    </p>

                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">

                        {results.map(item => (

                            <article
                                key={item.id}
                                className="border rounded-xl overflow-hidden shadow-sm"
                            >

                                {item.image && (

                                    <img
                                        src={item.image}
                                        alt={item.title}
                                        className="w-full h-48 object-cover"
                                    />

                                )}

                                <div className="p-5">

                                    <span className="text-xs uppercase text-blue-600">
                                        {item.content_type}
                                    </span>

                                    <h2 className="font-bold text-xl mt-2">
                                        {item.title}
                                    </h2>

                                    <p className="text-gray-500 mt-2 line-clamp-3">
                                        {item.excerpt}
                                    </p>

                                    <div className="text-sm text-gray-400 mt-3">
                                        By {item.author_username}
                                    </div>

                                    <div className="mt-4">

                                        <Link
                                            to={`/content/${item.id}`}
                                            className="text-blue-600 font-semibold"
                                        >
                                            Read more →
                                        </Link>

                                    </div>

                                </div>

                            </article>

                        ))}

                    </div>

                    <div className="flex justify-center items-center gap-5 mt-10">

                        <button
                            disabled={!pagination.previous}
                            onClick={() =>
                                changePage(currentPage - 1)
                            }
                            className="px-5 py-2 rounded-lg bg-gray-200 disabled:opacity-40"
                        >
                            Previous
                        </button>

                        <span>
                            Page {currentPage}
                        </span>

                        <button
                            disabled={!pagination.next}
                            onClick={() =>
                                changePage(currentPage + 1)
                            }
                            className="px-5 py-2 rounded-lg bg-blue-600 text-white disabled:opacity-40"
                        >
                            Next
                        </button>

                    </div>

                </>

            )}

        </main>

    );

}