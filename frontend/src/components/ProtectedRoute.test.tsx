import { render, screen } from '@testing-library/react';
import { BrowserRouter, Routes, Route, MemoryRouter } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import { authUtils } from '../api';

// Mock the api module
jest.mock('../api', () => ({
  authUtils: {
    isAuthenticated: jest.fn(),
  },
}));

const TestProtectedComponent = () => <div>Protected Content</div>;
const TestLoginComponent = () => <div>Login Page</div>;

describe('ProtectedRoute Component', () => {
  beforeEach(() => {
    // Reset mock implementation but keep call tracking
    (authUtils.isAuthenticated as jest.Mock).mockReset();
  });

  const renderWithRouter = (isAuthenticated: boolean) => {
    (authUtils.isAuthenticated as jest.Mock).mockReturnValue(isAuthenticated);

    return render(
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<TestLoginComponent />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <TestProtectedComponent />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    );
  };

  test('renders children when authenticated', () => {
    renderWithRouter(true);
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
  });

  test('redirects to login when not authenticated', () => {
    renderWithRouter(false);
    
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });


});
