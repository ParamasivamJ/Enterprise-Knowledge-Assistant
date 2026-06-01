import "./globals.css";

export const metadata = {
  title: "Enterprise Knowledge Assistant",
  description: "AI-powered document search with citations and evaluation dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
