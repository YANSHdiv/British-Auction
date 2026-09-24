import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { AuctionListPage } from './pages/AuctionListPage';
import { AuctionDetailPage } from './pages/AuctionDetailPage';
import { CreateRfqPage } from './pages/CreateRfqPage';
import { NotFoundPage } from './pages/NotFoundPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: true,
      staleTime: 2000,
    },
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode; buyerOnly?: boolean }> = ({
  children,
  buyerOnly = false,
}) => {
  const { user, isLoading, isBuyer } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-500 font-semibold text-sm">
        Initializing workspace...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (buyerOnly && !isBuyer) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const AppContent: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AuctionListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/auctions/:id"
            element={
              <ProtectedRoute>
                <AuctionDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/create-rfq"
            element={
              <ProtectedRoute buyerOnly>
                <CreateRfqPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>British Auction RFQ Engine &copy; {new Date().getFullYear()} &bull; Professional B2B Sourcing Platform</span>
          <span className="font-mono text-slate-400">PostgreSQL &bull; FastAPI &bull; React &bull; Tailwind</span>
        </div>
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
