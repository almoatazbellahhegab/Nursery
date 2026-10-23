/** Public shell only. Protected routes must establish server identity later. */
import type { ReactNode } from 'react';
import './style.css';
export const metadata = { title: 'Nursery administration foundation' };
export default function Layout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
