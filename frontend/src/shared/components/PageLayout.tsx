import { PropsWithChildren } from 'react';

export const PageLayout = ({ children }: PropsWithChildren) => {
  return <div className="p-4 max-w-screen-md mx-auto">{children}</div>;
};

export const PageLoader = () => (
  <div className="p-4">Loading...</div>
);

export const NotFound = () => (
  <div className="p-4">Not Found</div>
);
