'use client'

import Navbar from "./component/navbar";
import FeedTray from "./component/feedTray";


// key = key123

export default function Home() {
	return (
		<div className="w-full">
			<Navbar />
			<FeedTray />
		</div>
	);
}
