import './globals.css';
import { AppProviders } from '../components/providers/AppProviders.jsx';

export const metadata = {
  title: 'NIYOGEN – Field Surveillance & Audit',
  description: 'Field Operations Unit – Real-Time Field Reporting & Surveillance Ledger'
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-[#F8F9FA] text-slate-800 antialiased overflow-x-hidden min-h-screen">
        <AppProviders>
          {children}
        </AppProviders>
      </body>
    </html>
  );
}
