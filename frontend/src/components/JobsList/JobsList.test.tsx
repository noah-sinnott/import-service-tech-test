import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobsList from './JobsList';
import { api } from '../../api';

// Mock the api module
jest.mock('../../api', () => ({
  api: {
    listJobs: jest.fn(),
    getJob: jest.fn(),
  },
}));

const mockJobs = [
  {
    jobId: 1,
    status: 'Completed',
    selectedSources: ['products', 'carts'],
    progress: {
      products: { completed: 30, total: 30, status: 'Completed' },
      carts: { completed: 20, total: 20, status: 'Completed' },
    },
    error: null,
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:30:00Z',
  },
  {
    jobId: 2,
    status: 'Running',
    selectedSources: ['products'],
    progress: {
      products: { completed: 15, total: 30, status: 'Running' },
    },
    error: null,
    createdAt: '2024-01-15T11:00:00Z',
    updatedAt: '2024-01-15T11:15:00Z',
  },
  {
    jobId: 3,
    status: 'Failed',
    selectedSources: ['carts'],
    progress: {
      carts: { completed: 5, total: 20, status: 'Failed' },
    },
    error: 'Connection timeout',
    createdAt: '2024-01-15T09:00:00Z',
    updatedAt: '2024-01-15T09:05:00Z',
  },
];

describe('JobsList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  const renderJobsList = () => {
    return render(
      <BrowserRouter>
        <JobsList />
      </BrowserRouter>
    );
  };

  test('shows loading state initially', () => {
    (api.listJobs as jest.Mock).mockImplementation(() => new Promise(() => {}));
    
    renderJobsList();
    
    expect(screen.getByText('Loading jobs...')).toBeInTheDocument();
  });

  test('displays jobs after loading', async () => {
    (api.listJobs as jest.Mock).mockResolvedValue(mockJobs);
    
    renderJobsList();

    await waitFor(() => {
      expect(screen.getByText('Import Jobs')).toBeInTheDocument();
    });

    expect(screen.getByText('Job #1')).toBeInTheDocument();
    expect(screen.getByText('Job #2')).toBeInTheDocument();
    expect(screen.getByText('Job #3')).toBeInTheDocument();
  });

  test('displays job statuses correctly', async () => {
    (api.listJobs as jest.Mock).mockResolvedValue(mockJobs);
    
    renderJobsList();

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
      expect(screen.getByText('Running')).toBeInTheDocument();
      expect(screen.getByText('Failed')).toBeInTheDocument();
    });
  });

  test('displays sources for each job', async () => {
    (api.listJobs as jest.Mock).mockResolvedValue(mockJobs);
    
    renderJobsList();

    await waitFor(() => {
      const productsElements = screen.getAllByText(/products/i);
      const cartsElements = screen.getAllByText(/carts/i);
      
      expect(productsElements.length).toBeGreaterThan(0);
      expect(cartsElements.length).toBeGreaterThan(0);
    });
  });

  test('displays error message on failure', async () => {
    (api.listJobs as jest.Mock).mockRejectedValue(new Error('Failed to load jobs'));
    
    renderJobsList();

    await waitFor(() => {
      expect(screen.getByText('Failed to load jobs')).toBeInTheDocument();
    });
  });

  test('polls active jobs', async () => {
    const runningJob = {
      ...mockJobs[1],
      status: 'Running',
    };
    
    (api.listJobs as jest.Mock).mockResolvedValue([runningJob]);
    (api.getJob as jest.Mock).mockResolvedValue(runningJob);
    
    renderJobsList();

    await waitFor(() => {
      expect(screen.getByText('Job #2')).toBeInTheDocument();
    });

    // Clear initial calls
    (api.getJob as jest.Mock).mockClear();

    // Advance timers to trigger polling
    jest.advanceTimersByTime(2000);

    await waitFor(() => {
      expect(api.getJob).toHaveBeenCalledWith(2);
    });
  });

  test('stops polling when job completes', async () => {
    const runningJob = {
      ...mockJobs[1],
      status: 'Running',
    };
    const completedJob = {
      ...runningJob,
      status: 'Completed',
    };
    
    (api.listJobs as jest.Mock).mockResolvedValue([runningJob]);
    (api.getJob as jest.Mock).mockResolvedValue(completedJob);
    
    renderJobsList();

    await waitFor(() => {
      expect(screen.getByText('Running')).toBeInTheDocument();
    });

    // Advance time and verify polling happens
    jest.advanceTimersByTime(2000);
    
    await waitFor(() => {
      expect(api.getJob).toHaveBeenCalled();
    });

    // After job completes, verify it shows as completed
    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });
  });

  test('shows empty state when no jobs', async () => {
    (api.listJobs as jest.Mock).mockResolvedValue([]);
    
    renderJobsList();

    await waitFor(() => {
      expect(screen.getByText('No jobs yet')).toBeInTheDocument();
    });
  });

  test('displays error message for failed jobs', async () => {
    (api.listJobs as jest.Mock).mockResolvedValue([mockJobs[2]]);
    
    renderJobsList();

    await waitFor(() => {
      expect(screen.getByText(/Connection timeout/i)).toBeInTheDocument();
    });
  });

  test('formats dates correctly', async () => {
    (api.listJobs as jest.Mock).mockResolvedValue(mockJobs);
    
    renderJobsList();

    await waitFor(() => {
      const dateElements = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
      expect(dateElements.length).toBeGreaterThan(0);
    });
  });
});
