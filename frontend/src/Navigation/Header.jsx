import React, { useState } from "react";

import Navs from "../Navigation/Navigator";

import {
    SlidersHorizontal,
    Search,
} from "lucide-react";

import NotificationBell from "../components/notifications/NotificationBell";

export default function Header({ onSearch = () => {} }) {

    const [text, setText] = useState("");

    const handleSearch = (value) => {

        setText(value);

        onSearch(value);

    };

    return (

        <div className="bg-blue-900 px-4 pt-4 pb-6 rounded-b-3xl">

            <div className="px-4 py-2 flex justify-between items-center">

                <Navs />

                <span className="font-poppins text-2xl font-bold text-white">
                    EnglishNote
                </span>

                <div className="flex items-center gap-3">

                    <Search
                        size={25}
                        className="text-white"
                    />

                    <NotificationBell />

                </div>

            </div>

            <div className="px-4 py-10 flex justify-between items-center gap-2">

                <div className="flex items-center text-white bg-white p-2 rounded-xl w-full">

                    <Search
                        size={30}
                        className="text-blue-900 px-2"
                    />

                    <input
                        id="user-input"
                        type="text"
                        value={text}
                        onChange={(e) =>
                            handleSearch(e.target.value)
                        }
                        placeholder="Search posts..."
                        className="focus:outline-none border-none rounded-xl text-blue-900 h-10 w-full"
                    />

                </div>

                <SlidersHorizontal
                    size={45}
                    className="text-white bg-white/15 p-2 rounded-xl"
                />

            </div>

        </div>

    );

}