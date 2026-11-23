import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import publishing from "../../services/publishing";
import engagement from "../../services/engagement";
import CommentSection from "../../components/content/CommentSection";
import { useAuth } from "../../context/AuthContext";





export default function ContentDetails() {
    const { id } = useParams();
    const { isAuthenticated } = useAuth();

    const [item, setItem] = useState(null);
    const [error, setError] = useState("");
    const [liked, setLiked] = useState(false);
    const [bookmarked, setBookmarked] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await publishing.getContent(id);

                setItem(data);

                await publishing.recordView(data.id);
            } catch {
                setError("Unable to load this content.");
            }
        };

        load();
    }, [id]);

    const handleLike = async () => {

    try {

        const data = await engagement.like(content.id);

        setEngagementData(previous => ({
            ...previous,
            liked: data.liked,
            likes_count: data.likes_count,
        }));

    } catch (error) {

        console.error(
            "Unable to update like.",
            error
        );

    }

};

    const handleBookmark = async () => {

    try {

        const data = await engagement.bookmark(content.id);

        setEngagementData(previous => ({
            ...previous,
            bookmarked: data.bookmarked,
        }));

    } catch (error) {

        console.error(
            "Unable to update bookmark.",
            error
        );

    }

};


const [engagementData, setEngagementData] = useState({
    likes_count: 0,
    comments_count: 0,
    shares_count: 0,
    liked: false,
    bookmarked: false,
});

const loadEngagement = async (contentId) => {

    try {

        const data = await engagement.summary(contentId);

        setEngagementData(data);

    } catch (error) {

        console.error(
            "Unable to load engagement information.",
            error
        );

    }

};


    const handleShare = async () => {
        try {
            await navigator.clipboard.writeText(window.location.href);
            await engagement.shareContent(item.id, "copy");
        } catch {
            setError("Unable to copy or record the share.");
        }
    };

    if (error && !item) {
        return <p className="p-8 text-red-600">{error}</p>;
    }

    if (!item) {
        return <p className="p-8">Loading content...</p>;
    }

    return (
        <main className="max-w-4xl mx-auto px-5 py-10">
            <h1 className="text-4xl font-bold mb-5">
                {item.title}
            </h1>

            {item.image && (
                <img
                    src={item.image}
                    alt={item.title}
                    className="w-full max-h-[450px] object-cover rounded-xl mb-6"
                />
            )}

            <p className="text-gray-500 mb-6">
                {item.author_username || "Author"} · {item.views || 0} views
            </p>

            <article className="prose max-w-none whitespace-pre-wrap">
                {item.body}
            </article>

            <div className="flex gap-3 mt-8">
                <button
                    onClick={handleLike}
                    disabled={!isAuthenticated}
                    className="border px-4 py-2 rounded-lg disabled:opacity-50"
                >
                    {liked ? "Liked" : "Like"}
                </button>

                <button
                    onClick={handleBookmark}
                    disabled={!isAuthenticated}
                    className="border px-4 py-2 rounded-lg disabled:opacity-50"
                >
                    {bookmarked ? "Bookmarked" : "Bookmark"}
                </button>

                <button
                    onClick={handleShare}
                    className="border px-4 py-2 rounded-lg"
                >
                    Share
                </button>
            </div>

            {error && (
                <p className="text-red-600 mt-4">{error}</p>
            )}

            <CommentSection contentId={item.id} />
        </main>
    );
}