import { PropsWithChildren } from 'react';
import { Navigation } from './Navigation';

interface PageLayoutProps {
  children: React.ReactNode;
}

export const PageLayout = ({ children }: PageLayoutProps) => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation />
      <main className="py-10">
        <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export const PageLoader = () => (
  <div className="p-4">Loading...</div>
);

export const NotFound = () => (
  <div className="p-4">Not Found</div>
);
