'use client';

import { useRouter } from 'next/navigation';
import Link from "next/link";
import Navbar from '@/app/component/navbar';

export default function Profile() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      const response = await fetch('https://news-recommender-backend-20d530136c15.herokuapp.com/logout', {
        credentials: 'include',
      });
      if (response.ok) {
        router.push('/login');
      } else {
        alert('Logout failed');
      }
    } catch (err) {
      alert('Something went wrong');
    }
  };

  const navLinks = [
    { name: "Home", path: "../" },
    { name: "Logout", path: "#", onClick: handleLogout, highlight: true },
  ];

  return (
    <div className="min-h-screen bg-black">
      <Navbar links={navLinks} />
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-4">Profile</h1>
        <p>Welcome to your profile!</p>
      </div>
    </div>
  );
}