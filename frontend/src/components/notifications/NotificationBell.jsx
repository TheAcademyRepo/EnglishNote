import { useEffect, useState } from "react";
import { Bell, CheckCheck, X } from "lucide-react";

import notifications from "../../services/notifications";
import { useAuth } from "../../context/AuthContext";

export default function NotificationBell() {

    const { isAuthenticated } = useAuth();

    const [open, setOpen] = useState(false);
    const [items, setItems] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [loading, setLoading] = useState(false);

    const loadCount = async () => {

        try {

            const data = await notifications.getUnreadCount();

            setUnreadCount(data.unread_count || 0);

        } catch (error) {

            console.error("Unable to load notification count.");

        }
    };

    const loadNotifications = async () => {

        setLoading(true);

        try {

            const data = await notifications.getAll({
                page: 1,
                page_size: 15
            });

            setItems(
                Array.isArray(data)
                    ? data
                    : data.results || []
            );

            await loadCount();

        } catch (error) {

            console.error("Unable to load notifications.");

        } finally {

            setLoading(false);

        }
    };

    useEffect(() => {

        if (!isAuthenticated) {
            setItems([]);
            setUnreadCount(0);
            return;
        }

        loadCount();

        const interval = setInterval(
            loadCount,
            60000
        );

        return () => clearInterval(interval);

    }, [isAuthenticated]);

    const toggleNotifications = async () => {

        const nextState = !open;

        setOpen(nextState);

        if (nextState) {
            await loadNotifications();
        }

    };

    const handleRead = async (id) => {

        try {

            await notifications.markRead(id);

            setItems(previous =>
                previous.map(item =>
                    item.id === id
                        ? { ...item, is_read: true }
                        : item
                )
            );

            setUnreadCount(previous =>
                Math.max(0, previous - 1)
            );

        } catch (error) {

            console.error("Unable to mark notification as read.");

        }
    };

    const handleReadAll = async () => {

        try {

            await notifications.markAllRead();

            setItems(previous =>
                previous.map(item => ({
                    ...item,
                    is_read: true
                }))
            );

            setUnreadCount(0);

        } catch (error) {

            console.error("Unable to mark notifications as read.");

        }
    };

    const handleDelete = async (id) => {

        try {

            const notification = items.find(
                item => item.id === id
            );

            await notifications.delete(id);

            setItems(previous =>
                previous.filter(item => item.id !== id)
            );

            if (notification && !notification.is_read) {
                setUnreadCount(previous =>
                    Math.max(0, previous - 1)
                );
            }

        } catch (error) {

            console.error("Unable to delete notification.");

        }
    };

    if (!isAuthenticated) {
        return null;
    }

    return (

        <div className="relative">

            <button
                type="button"
                onClick={toggleNotifications}
                className="relative p-2 text-white"
                aria-label="Notifications"
            >

                <Bell size={28} />

                {unreadCount > 0 && (

                    <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full min-w-5 h-5 flex items-center justify-center px-1">

                        {unreadCount > 99
                            ? "99+"
                            : unreadCount}

                    </span>

                )}

            </button>

            {open && (

                <div className="absolute right-0 top-12 z-50 w-80 sm:w-96 bg-white text-gray-800 shadow-xl rounded-xl border overflow-hidden">

                    <div className="flex justify-between items-center p-4 border-b">

                        <h3 className="font-bold text-lg">
                            Notifications
                        </h3>

                        <div className="flex items-center gap-3">

                            <button
                                onClick={handleReadAll}
                                className="text-blue-600 text-sm flex items-center gap-1"
                            >
                                <CheckCheck size={16} />
                                Read all
                            </button>

                            <button
                                onClick={() => setOpen(false)}
                            >
                                <X size={20} />
                            </button>

                        </div>

                    </div>

                    <div className="max-h-96 overflow-y-auto">

                        {loading ? (

                            <p className="p-6 text-center">
                                Loading notifications...
                            </p>

                        ) : items.length === 0 ? (

                            <p className="p-6 text-center text-gray-500">
                                No notifications yet.
                            </p>

                        ) : (

                            items.map(item => (

                                <div
                                    key={item.id}
                                    className={`p-4 border-b flex gap-3 ${
                                        item.is_read
                                            ? "bg-white"
                                            : "bg-blue-50"
                                    }`}
                                >

                                    <div className="flex-1">

                                        <p className="text-sm">
                                            {item.message}
                                        </p>

                                        <p className="text-xs text-gray-400 mt-2">
                                            {new Date(
                                                item.created_at
                                            ).toLocaleString()}
                                        </p>

                                        {!item.is_read && (

                                            <button
                                                onClick={() =>
                                                    handleRead(item.id)
                                                }
                                                className="text-blue-600 text-xs mt-2"
                                            >
                                                Mark as read
                                            </button>

                                        )}

                                    </div>

                                    <button
                                        onClick={() =>
                                            handleDelete(item.id)
                                        }
                                        className="text-gray-400 hover:text-red-600"
                                        aria-label="Delete notification"
                                    >
                                        <X size={17} />
                                    </button>

                                </div>

                            ))

                        )}

                    </div>

                </div>

            )}

        </div>

    );

}