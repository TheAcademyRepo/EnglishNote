import { Link } from "react-router-dom";

export default function ContentCard({ item }) {
    return (
        <article className="bg-white border rounded-xl overflow-hidden shadow-sm hover:shadow-md transition">
            {item.image && <img src={item.image} alt={item.title} className="w-full h-48 object-cover" />}
            <div className="p-5">
                <p className="text-sm text-blue-600 mb-2">{item.content_type || "Article"}</p>
                <h2 className="text-xl font-bold mb-2">{item.title}</h2>
                <p className="text-gray-600 line-clamp-3">{item.excerpt || ""}</p>
                <div className="flex justify-between text-sm text-gray-500 mt-5">
                    <span>{item.author_username || "Author"}</span>
                    <span>{item.views || 0} views</span>
                </div>
                <Link to={`/content/${item.slug}`} className="inline-block mt-5 text-blue-600 font-medium">Read more →</Link>
            </div>
        </article>
    );
}
