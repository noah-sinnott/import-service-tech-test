import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api';
import './Onboarding.css';

const AVAILABLE_SOURCES = ['products', 'carts'];

const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<'select' | 'credentials'>('select');

  const [selectedSources, setSelectedSources] = useState<string[]>([]);

  const [authType, setAuthType] = useState<Record<string, 'apikey' | 'oauth'>>({});
  const [tokens, setTokens] = useState<Record<string, { apiKey?: string; oauthToken?: string }>>({});

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSourceToggle = (source: string) => {
    setSelectedSources(prev =>
      prev.includes(source)
        ? prev.filter(s => s !== source)
        : [...prev, source]
    );
  };

  const handleNext = () => {
    if (selectedSources.length === 0) {
      setError('Please select at least one data source');
      return;
    }
    setError(null);
    // Initialize auth type for each source
    const initialAuthType: Record<string, 'apikey' | 'oauth'> = {};
    selectedSources.forEach(source => {
      initialAuthType[source] = 'apikey';
    });
    setAuthType(initialAuthType);
    setStep('credentials');
  };

  const handleOAuthConnect = (source: string) => {
    // Mock OAuth flow
    const token = `oauth_token_${source}_${Date.now()}`;
    setTokens(prev => ({ ...prev, [source]: { ...prev[source], oauthToken: token } }));
  };

  const handleTokenChange = (source: string, token: string) => {
    setTokens(prev => ({ ...prev, [source]: { ...prev[source], apiKey: token } }));
  };

  const handleAuthTypeChange = (source: string, type: 'apikey' | 'oauth') => {
    setAuthType(prev => ({ ...prev, [source]: type }));
  };

  const handleStartImport = async () => {
    // Validate credentials
    const missingCreds = selectedSources.filter(source => {
      const type = authType[source];
      const sourceTokens = tokens[source];
      if (type === 'apikey') {
        return !sourceTokens?.apiKey;
      }
      return !sourceTokens?.oauthToken;
    });

    if (missingCreds.length > 0) {
      setError(`Missing credentials for: ${missingCreds.join(', ')}`);
      return;
    }

    setError(null);
    setLoading(true);

    try {
      // Create job with appropriate credentials based on auth type
      const credentials: Record<string, { apiKey?: string; oauthToken?: string }> = {};
      selectedSources.forEach(source => {
        const sourceTokens = tokens[source];
        if (authType[source] === 'apikey') {
          credentials[source] = { apiKey: sourceTokens?.apiKey };
        } else {
          credentials[source] = { oauthToken: sourceTokens?.oauthToken };
        }
      });

      const jobRequest = {
        selectedSources,
        credentials,
      };

      await api.createJob(jobRequest);
      
      // Navigate to jobs list to see the import progress
      navigate('/jobs');
    } catch (err: any) {
      setError(err.message || 'Failed to start import');
      setLoading(false);
    }
  };

  const handleBack = () => {
    setStep('select');
    setError(null);
  };



  return (
    <div className="card">
      <h2>Import Data</h2>

      {step === 'select' && (
        <>
          <div className="form-group">
            <label>Select Data Sources</label>
            <div className="checkbox-group">
              {AVAILABLE_SOURCES.map(source => (
                <label key={source} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(source)}
                    onChange={() => handleSourceToggle(source)}
                  />
                  <span>{source}</span>
                </label>
              ))}
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button className="btn-primary" onClick={handleNext}>
            Next: Configure Credentials
          </button>
        </>
      )}

      {step === 'credentials' && (
        <>
          <div className="form-group">
            <label>Configure Credentials</label>
            <p style={{ color: '#7f8c8d', marginBottom: '1rem' }}>
              Enter API keys or use OAuth to connect each data source.
            </p>

            {selectedSources.map(source => (
              <div key={source} className="credentials-section">
                <h3>{source}</h3>

                <div className="auth-type-group">
                  <label>
                    <input
                      type="radio"
                      name={`auth-${source}`}
                      checked={authType[source] === 'apikey'}
                      onChange={() => handleAuthTypeChange(source, 'apikey')}
                    />
                    API Key
                  </label>
                  <label>
                    <input
                      type="radio"
                      name={`auth-${source}`}
                      checked={authType[source] === 'oauth'}
                      onChange={() => handleAuthTypeChange(source, 'oauth')}
                    />
                    OAuth
                  </label>
                </div>

                {authType[source] === 'apikey' ? (
                  <input
                    type="text"
                    placeholder={`Enter ${source} API key`}
                    value={tokens[source]?.apiKey || ''}
                    onChange={(e) => handleTokenChange(source, e.target.value)}
                  />
                ) : tokens[source]?.oauthToken ? (
                  <div className="connected-badge">
                    ✓ Connected via OAuth
                  </div>
                ) : (
                  <button
                    className="btn-secondary oauth-button"
                    onClick={() => handleOAuthConnect(source)}
                  >
                    🔗 Connect via OAuth
                  </button>
                )}
              </div>
            ))}
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="button-group">
            <button className="btn-secondary" onClick={handleBack}>
              Back
            </button>
            <button
              className="btn-success"
              onClick={handleStartImport}
              disabled={loading}
            >
              {loading ? 'Starting...' : 'Start Import'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Onboarding;
