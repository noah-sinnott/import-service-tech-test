import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Onboarding from './Onboarding';
import { api } from '../../api';

// Mock the api module
jest.mock('../../api', () => ({
  api: {
    createJob: jest.fn(),
  },
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('Onboarding Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderOnboarding = () => {
    return render(
      <BrowserRouter>
        <Onboarding />
      </BrowserRouter>
    );
  };

  test('renders source selection step', () => {
    renderOnboarding();
    
    expect(screen.getByText('Select Data Sources')).toBeInTheDocument();
    expect(screen.getByText(/products/i)).toBeInTheDocument();
    expect(screen.getByText(/carts/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
  });

  test('allows selecting and deselecting sources', () => {
    renderOnboarding();
    
    const productsCheckbox = screen.getByLabelText(/products/i) as HTMLInputElement;
    const cartsCheckbox = screen.getByLabelText(/carts/i) as HTMLInputElement;

    expect(productsCheckbox.checked).toBe(false);
    expect(cartsCheckbox.checked).toBe(false);

    fireEvent.click(productsCheckbox);
    expect(productsCheckbox.checked).toBe(true);

    fireEvent.click(cartsCheckbox);
    expect(cartsCheckbox.checked).toBe(true);

    fireEvent.click(productsCheckbox);
    expect(productsCheckbox.checked).toBe(false);
  });

  test('shows error when proceeding without selecting sources', () => {
    renderOnboarding();
    
    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);

    expect(screen.getByText('Please select at least one data source')).toBeInTheDocument();
  });

  test('proceeds to credentials step after selecting sources', () => {
    renderOnboarding();
    
    const productsCheckbox = screen.getByLabelText(/products/i);
    fireEvent.click(productsCheckbox);

    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);

    expect(screen.getByText('Configure Credentials')).toBeInTheDocument();
    expect(screen.getByText(/products/i)).toBeInTheDocument();
  });

  test('allows entering API key credentials', () => {
    renderOnboarding();
    
    // Select source
    fireEvent.click(screen.getByLabelText(/products/i));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Enter API key
    const apiKeyInput = screen.getByPlaceholderText(/enter products api key/i) as HTMLInputElement;
    fireEvent.change(apiKeyInput, { target: { value: 'test-api-key-123' } });

    expect(apiKeyInput.value).toBe('test-api-key-123');
  });

  test('allows switching between API key and OAuth', () => {
    renderOnboarding();
    
    // Select source
    fireEvent.click(screen.getByLabelText(/products/i));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Check API Key is selected by default
    const apiKeyRadio = screen.getByLabelText(/api key/i) as HTMLInputElement;
    expect(apiKeyRadio.checked).toBe(true);

    // Switch to OAuth
    const oauthRadio = screen.getByLabelText(/oauth/i);
    fireEvent.click(oauthRadio);

    expect(screen.getByText(/connect via oauth/i)).toBeInTheDocument();
  });

  test('shows error when starting import without credentials', () => {
    renderOnboarding();
    
    // Select source
    fireEvent.click(screen.getByLabelText(/products/i));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Try to start import without entering credentials
    const startButton = screen.getByRole('button', { name: /start import/i });
    fireEvent.click(startButton);

    expect(screen.getByText(/missing credentials/i)).toBeInTheDocument();
  });

  test('successfully creates job and navigates', async () => {
    (api.createJob as jest.Mock).mockResolvedValue({ jobId: 1 });
    
    renderOnboarding();
    
    // Select source
    fireEvent.click(screen.getByLabelText(/products/i));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Enter credentials
    const apiKeyInput = screen.getByPlaceholderText(/enter products api key/i);
    fireEvent.change(apiKeyInput, { target: { value: 'test-api-key' } });

    // Start import
    const startButton = screen.getByRole('button', { name: /start import/i });
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(api.createJob).toHaveBeenCalledWith({
        selectedSources: ['products'],
        credentials: {
          products: { apiKey: 'test-api-key' },
        },
      });
      expect(mockNavigate).toHaveBeenCalledWith('/jobs');
    });
  });

  test('displays error on job creation failure', async () => {
    (api.createJob as jest.Mock).mockRejectedValue(new Error('Invalid API key'));
    
    renderOnboarding();
    
    // Select source
    fireEvent.click(screen.getByLabelText(/products/i));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Enter credentials
    const apiKeyInput = screen.getByPlaceholderText(/enter products api key/i);
    fireEvent.change(apiKeyInput, { target: { value: 'bad-key' } });

    // Start import
    const startButton = screen.getByRole('button', { name: /start import/i });
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid API key')).toBeInTheDocument();
    });
  });

  test('handles multiple sources with different credentials', async () => {
    (api.createJob as jest.Mock).mockResolvedValue({ jobId: 1 });
    
    renderOnboarding();
    
    // Select both sources
    fireEvent.click(screen.getByLabelText(/products/i));
    fireEvent.click(screen.getByLabelText(/carts/i));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Enter credentials for both
    const productsKeyInput = screen.getByPlaceholderText(/enter products api key/i);
    const cartsKeyInput = screen.getByPlaceholderText(/enter carts api key/i);
    fireEvent.change(productsKeyInput, { target: { value: 'products-key' } });
    fireEvent.change(cartsKeyInput, { target: { value: 'carts-key' } });

    // Start import
    const startButton = screen.getByRole('button', { name: /start import/i });
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(api.createJob).toHaveBeenCalledWith({
        selectedSources: ['products', 'carts'],
        credentials: {
          products: { apiKey: 'products-key' },
          carts: { apiKey: 'carts-key' },
        },
      });
    });
  });

  test('allows going back from credentials to source selection', () => {
    renderOnboarding();
    
    // Go to credentials step
    fireEvent.click(screen.getByLabelText(/products/i));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    expect(screen.getByText('Configure Credentials')).toBeInTheDocument();

    // Go back
    const backButton = screen.getByRole('button', { name: /back/i });
    fireEvent.click(backButton);

    expect(screen.getByText('Select Data Sources')).toBeInTheDocument();
  });

  test('disables start button while loading', async () => {
    (api.createJob as jest.Mock).mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    renderOnboarding();
    
    // Select source and enter credentials
    fireEvent.click(screen.getByLabelText(/products/i));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    
    const apiKeyInput = screen.getByPlaceholderText(/enter products api key/i);
    fireEvent.change(apiKeyInput, { target: { value: 'test-key' } });

    // Start import
    const startButton = screen.getByRole('button', { name: /start import/i });
    fireEvent.click(startButton);

    expect(startButton).toBeDisabled();
  });
});
