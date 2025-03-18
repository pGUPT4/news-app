'use client'

import Link from "next/link"
import React from "react"


export default function Navbar() {
    return(
        <div className="flex-1 flex flex-row bg-slate-800 text-white text-2xl font-mono font-bold">
            <nav>
                <Link href="/">
                    News <br/> Recommender
                </Link>

                <Link href={"/routings/profile"}>
                    Profile
                </Link>
            </nav>
        </div>
    )
}