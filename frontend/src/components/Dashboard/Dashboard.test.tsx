import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './Dashboard';
import { api } from '../../api';

// Mock the api module
jest.mock('../../api', () => ({
  api: {
    getDashboard: jest.fn(),
  },
}));

const mockDashboardData = {
  totalJobs: 5,
  completedJobs: 3,
  failedJobs: 1,
  totalProducts: 150,
  totalCarts: 45,
  recentItems: [
    {
      id: 1,
      source: 'products',
      remoteId: 123,
      payload: { title: 'Product 1', price: 29.99 },
      status: 'Success',
      createdAt: '2024-01-15T10:00:00Z',
    },
    {
      id: 2,
      source: 'carts',
      remoteId: 456,
      payload: { products: ['item1', 'item2'] },
      status: 'Success',
      createdAt: '2024-01-15T09:30:00Z',
    },
  ],
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderDashboard = () => {
    return render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );
  };

  test('shows loading state initially', () => {
    (api.getDashboard as jest.Mock).mockImplementation(() => new Promise(() => {}));
    
    renderDashboard();
    
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  test('displays dashboard stats after loading', async () => {
    (api.getDashboard as jest.Mock).mockResolvedValue(mockDashboardData);
    
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Total Jobs')).toBeInTheDocument();
    });

    // Verify each stat shows the correct value
    const totalJobsStat = screen.getByTestId('stat-total-jobs');
    expect(totalJobsStat).toHaveTextContent('5');
    expect(totalJobsStat).toHaveTextContent('Total Jobs');

    const completedStat = screen.getByTestId('stat-completed');
    expect(completedStat).toHaveTextContent('3');
    expect(completedStat).toHaveTextContent('Completed');

    const failedStat = screen.getByTestId('stat-failed');
    expect(failedStat).toHaveTextContent('1');
    expect(failedStat).toHaveTextContent('Failed');

    const productsStat = screen.getByTestId('stat-products');
    expect(productsStat).toHaveTextContent('150');
    expect(productsStat).toHaveTextContent('Products');

    const cartsStat = screen.getByTestId('stat-carts');
    expect(cartsStat).toHaveTextContent('45');
    expect(cartsStat).toHaveTextContent('Carts');
  });

  test('displays recent items', async () => {
    (api.getDashboard as jest.Mock).mockResolvedValue(mockDashboardData);
    
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Recent Imports')).toBeInTheDocument();
    });

    expect(screen.getByText('carts')).toBeInTheDocument();
    expect(screen.getByText(/Product 1/)).toBeInTheDocument();
    expect(screen.getByText('2 items')).toBeInTheDocument();
  });

  test('displays error message on failure', async () => {
    (api.getDashboard as jest.Mock).mockRejectedValue(new Error('Failed to load dashboard'));
    
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Failed to load dashboard')).toBeInTheDocument();
    });
  });

  test('shows empty state when no recent items', async () => {
    const emptyData = {
      ...mockDashboardData,
      recentItems: [],
    };
    (api.getDashboard as jest.Mock).mockResolvedValue(emptyData);
    
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Recent Imports')).toBeInTheDocument();
    });

    expect(screen.getByText('No imported items yet')).toBeInTheDocument();
  });

  test('formats dates correctly', async () => {
    (api.getDashboard as jest.Mock).mockResolvedValue(mockDashboardData);
    
    renderDashboard();

    await waitFor(() => {
      const dateElements = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
      expect(dateElements.length).toBeGreaterThan(0);
    });
  });
});
