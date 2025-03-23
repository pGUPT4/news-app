'use client';

import Navbar from "./component/navbar";
import FeedTray from "./component/feedTray";

export default function Home() {
  const navLinks = [
    { name: "News", path: "/" },
    { name: "Profile", path: "/routings/profile", highlight: true },
  ];

  return (
    <div className="w-full">
      <Navbar links={navLinks} />
      <FeedTray />
    </div>
  );
}