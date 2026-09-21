import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Adept Eduverse - JEE Advanced Maths',
  description: 'Organized JEE Advanced Maths video lectures, problem solving, and PYQs',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 antialiased text-slate-900">
        {children}
      </body>
    </html>
  );
}
