'use client';

import Link from "next/link";
import React from "react";

export default function Navbar({ links }) {
  return (
    <div className="w-full flex flex-row justify-between items-center bg-slate-800 text-white text-2xl font-mono font-bold px-6 py-4">
        {links.map((link, index) => (
            <Link
            key={index}
            href={link.path}
            onClick={link.onClick || null}  // Add click handler if provided
            className={`hover:text-gray-300 ${link.highlight ? 'bg-slate-700 px-4 py-2 rounded-md' : ''}`}
            >
            {link.name}
            </Link>
        ))}
    </div>
  );
}