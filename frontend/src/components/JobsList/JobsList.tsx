import React, { useEffect, useState } from 'react';
import { api, ImportJob } from '../../api';
import './JobsList.css';

const JobsList: React.FC = () => {
  const [jobs, setJobs] = useState<ImportJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeJobIds, setActiveJobIds] = useState<number[]>([]);

  const loadJobs = async () => {
    try {
      const jobsList = await api.listJobs();
      setJobs(jobsList);
      setError(null);

      // Identify jobs that need polling (Running or Pending)
      const active = jobsList
        .filter(job => job.status === 'Running' || job.status === 'Pending')
        .map(job => job.jobId);
      
      setActiveJobIds(active);
    } catch (err: any) {
      setError(err.message || 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  const pollActiveJobs = async () => {
    if (activeJobIds.length === 0) return;
    
    try {
      // Only fetch active jobs
      const updates = await Promise.all(
        activeJobIds.map(id => api.getJob(id))
      );
      
      // Update jobs list with fresh data for active jobs
      setJobs(prevJobs => 
        prevJobs.map(job => {
          const update = updates.find(u => u.jobId === job.jobId);
          return update || job;
        })
      );
      
      // Recalculate which jobs are still active
      const stillActive = updates
        .filter(job => job.status === 'Running' || job.status === 'Pending')
        .map(job => job.jobId);
      
      setActiveJobIds(stillActive);
    } catch (err) {
      console.error('Polling error:', err);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  useEffect(() => {
    if (activeJobIds.length === 0) return;

    const interval = setInterval(pollActiveJobs, 2000);

    return () => clearInterval(interval);
  }, [activeJobIds]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusClass = (status: string) => {
    return `status-${status.toLowerCase()}`;
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Loading jobs...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-message">{error}</div>
        <button className="btn-primary" onClick={loadJobs} style={{ marginTop: '1rem' }}>
          Retry
        </button>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="card">
        <div className="empty-state">
          <h3>No jobs yet</h3>
          <p>Create your first import job to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Import Jobs</h2>
        <button className="btn-secondary" onClick={loadJobs}>
          Refresh
        </button>
      </div>

      <div className="job-list">
        {jobs.map(job => (
          <div key={job.jobId} className="job-item">
            <div className="job-header">
              <span className="job-id">Job #{job.jobId}</span>
              <span className={`status-badge ${getStatusClass(job.status)}`}>
                {job.status}
              </span>
            </div>

            <div className="job-sources">
              {job.selectedSources.map(source => (
                <span key={source} className="source-tag">
                  {source}
                </span>
              ))}
            </div>

            <div className="timestamp">
              Created: {formatDate(job.createdAt)}
            </div>

            <div className="progress-section">
              {Object.entries(job.progress).map(([source, progress]) => (
                <div key={source} className="progress-item">
                  <div className="progress-label">
                    <span style={{ textTransform: 'capitalize' }}>{source}</span>
                    <span>
                      {progress.completed} / {progress.total}
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className={`progress-fill ${progress.status === 'Completed' ? 'completed' : ''}`}
                      style={{
                        width: `${(progress.completed / progress.total) * 100}%`
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {job.error && (
              <div className="error-message">
                {job.error}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default JobsList;
