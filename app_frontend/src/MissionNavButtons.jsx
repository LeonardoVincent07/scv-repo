import React from "react";
import logo from "./assets/m7_single_client_view.png";

/* 
  Base button layout + animation.
  Font is controlled by the custom .font-fjalla class.
*/

const baseButtonClasses = `
  inline-flex items-center justify-center
  px-8 py-2.5 rounded-md border
  text-base text-gray-900
  shadow-sm
  transition
  transform
  hover:-translate-y-0.5 hover:shadow-md
  active:translate-y-0 active:shadow-sm
  font-fjalla
`;

export default function MissionNavButtons() {
  return (
    <header className="bg-white border-b">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">

        {/* Logo */}
        <div className="flex items-center">
          <img
            src={logo}
            alt="M7 Single Client View"
            className="h-10"
          />
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-4">

          {/* MissionSmith */}
          <button
            type="button"
            className={`${baseButtonClasses}
              bg-[rgb(189,199,155)]
              border-[rgb(158,170,121)]
              hover:bg-[rgb(176,186,142)]
            `}
            onClick={() => {}}
          >
            MissionSmith
          </button>

          {/* MissionAtlas */}
          <button
            type="button"
            className={`${baseButtonClasses}
              bg-[rgb(241,205,86)]
              border-[rgb(214,182,75)]
              hover:bg-[rgb(232,196,80)]
            `}
            onClick={() => {}}
          >
            MissionAtlas
          </button>

          {/* MissionLog */}
          <button
            type="button"
            className={`${baseButtonClasses}
              bg-[rgb(167,198,223)]
              border-[rgb(142,172,195)]
              hover:bg-[rgb(157,187,210)]
            `}
            onClick={() => {}}
          >
            MissionLog
          </button>
        </div>

      </div>
    </header>
  );
}

