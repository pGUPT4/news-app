'use client'

import Link from "next/link"
import React from "react"


export default function Navbar() {
    return(
        <div className="w-full flex flex-row justify-between items-center bg-slate-800 text-white text-2xl font-mono font-bold px-6 py-4">
            
            <Link href="/" className= "hover:text-gray-300">
                News <br/> Recommender
            </Link>
            
            <Link href={"/routings/profile"} className="hover:text-gray-300 bg-slate-700 px-4 py-2 rounded-md">
                Profile
            </Link>
            
        </div>
    )
}