import { useEffect, useState } from "react";
import engagement from "../../services/engagement";
import { useAuth } from "../../context/AuthContext";

export default function CommentSection({ contentId }) {
    const { isAuthenticated } = useAuth();

    const [comments, setComments] = useState([]);
    const [body, setBody] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadComments = async () => {
        try {
            const data = await engagement.getComments(contentId);

            setComments(
                Array.isArray(data) ? data : data.results || []
            );
        } catch {
            setError("Unable to load comments.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadComments();
    }, [contentId]);

    const submitComment = async (e) => {
        e.preventDefault();

        if (!body.trim()) return;

        try {
            await engagement.createComment(contentId, body);

            setBody("");
            await loadComments();

        } catch {
            setError("Unable to submit your comment.");
        }
    };

    if (loading) {
        return <p>Loading comments...</p>;
    }

    return (
        <section className="mt-10">
            <h2 className="text-2xl font-bold mb-5">
                Comments
            </h2>

            {error && (
                <p className="text-red-600 mb-4">{error}</p>
            )}

            {isAuthenticated ? (
                <form onSubmit={submitComment} className="mb-8">
                    <textarea
                        value={body}
                        onChange={(e) => setBody(e.target.value)}
                        placeholder="Write a comment..."
                        rows="4"
                        className="w-full border p-3 rounded-lg"
                    />

                    <button className="mt-3 bg-blue-600 text-white px-5 py-2 rounded-lg">
                        Post Comment
                    </button>
                </form>
            ) : (
                <p className="text-gray-500 mb-6">
                    Log in to comment.
                </p>
            )}

            <div className="space-y-4">
                {comments.map((comment) => (
                    <div
                        key={comment.id}
                        className="border-b pb-4"
                    >
                        <p className="font-semibold">
                            {comment.username || "Student"}
                        </p>

                        <p className="text-gray-700 mt-2">
                            {comment.body}
                        </p>
                    </div>
                ))}

                {!comments.length && (
                    <p className="text-gray-500">
                        No comments yet.
                    </p>
                )}
            </div>
        </section>
    );
}