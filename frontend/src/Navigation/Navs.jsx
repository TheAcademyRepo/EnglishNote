import { Home, LibraryBig } from "lucide-react";

function Navs({ active, setActive }) {
  return (
    <div className="flex justify-between items-center py-6 px-10">

      {/* HOME */}
      <button
        onClick={() => setActive("home")}
        className="relative w-[10rem] flex flex-col items-center gap-1"
      >
        <Home size={35} />

        {active === "home" && (
          <span className="absolute -bottom-2 h-[2px] w-[10rem] bg-black" />
        )}
      </button>


      {/* NOTES */}
      <button
        onClick={() => setActive("notes")}
        className="relative w-[10rem] flex flex-col items-center gap-1"
      >
        <LibraryBig size={35} />

        {active === "notes" && (
          <span className="absolute -bottom-2 h-[2px] w-[10rem] bg-black" />
        )}
      </button>

    </div>
  );
}

export default Navs;