import React, { useEffect, useState } from 'react';
import { api, DashboardStats } from '../../api';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    try {
      const data = await api.getDashboard();
      setStats(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-message">{error}</div>
        <button className="btn-primary" onClick={loadDashboard} style={{ marginTop: '1rem' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div>
      <div className="dashboard-stats" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '1rem',
        marginBottom: '1.5rem'
      }}>
        <div className="stat-card" data-testid="stat-total-jobs">
          <div className="stat-value">{stats.totalJobs}</div>
          <div className="stat-label">Total Jobs</div>
        </div>
        <div className="stat-card" data-testid="stat-completed">
          <div className="stat-value">{stats.completedJobs}</div>
          <div className="stat-label">Completed</div>
        </div>
        <div className="stat-card" data-testid="stat-failed">
          <div className="stat-value">{stats.failedJobs}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-card" data-testid="stat-products">
          <div className="stat-value">{stats.totalProducts}</div>
          <div className="stat-label">Products</div>
        </div>
        <div className="stat-card" data-testid="stat-carts">
          <div className="stat-value">{stats.totalCarts}</div>
          <div className="stat-label">Carts</div>
        </div>
      </div>

      <div className="card">
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
          flexWrap: 'wrap',
          gap: '0.5rem'
        }}>
          <h2 style={{ margin: 0 }}>Recent Imports</h2>
          <button className="btn-secondary" onClick={loadDashboard}>
            Refresh
          </button>
        </div>

        {stats.recentItems.length === 0 ? (
          <div className="empty-state">
            <h3>No imported items yet</h3>
            <p>Start an import job to see data here</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="items-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Source</th>
                  <th>Remote ID</th>
                  <th>Status</th>
                  <th>Title</th>
                  <th>Imported At</th>
                </tr>
              </thead>
              <tbody>
                {stats.recentItems.map(item => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>
                      <span className="source-tag">{item.source}</span>
                    </td>
                    <td>{item.remoteId}</td>
                    <td>
                      <span className={`status-badge status-${item.status.toLowerCase()}`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="item-detail">
                      {item.payload.title 
                        ? truncateText(item.payload.title, 50)
                        : item.source === 'carts' 
                          ? `${item.payload.products?.length || 0} items`
                          : 'N/A'
                      }
                    </td>
                    <td className="timestamp">{formatDate(item.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
