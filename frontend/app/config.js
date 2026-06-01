// Configuration for dynamic API URL resolution in production.
// NEXT_PUBLIC_API_URL can be set in Vercel to point to your AWS EC2 instance.
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
