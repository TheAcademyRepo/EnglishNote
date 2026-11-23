import ContentList from "../../components/content/ContentList";
import SearchBar from "../../components/content/SearchBar";

export default function PublicContent() {
    return (
        <main className="max-w-7xl mx-auto px-5 py-10">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-3">
                    Explore Learning Resources
                </h1>

                <p className="text-gray-500 mb-5">
                    Discover articles, educational posts and learning resources.
                </p>

                <SearchBar />
            </div>

            <ContentList />
        </main>
    );
}