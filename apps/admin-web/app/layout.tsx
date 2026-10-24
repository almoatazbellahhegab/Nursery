/** Public shell only. Protected routes must establish server identity later. */
import type { ReactNode } from "react";
import "./style.css";
import "./workspace.css";
export const metadata = { title: "Nursery | Workspace" };
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
