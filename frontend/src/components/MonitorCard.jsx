import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { metricsAPI, monitorAPI } from '../lib/api';
import { Globe, Clock, TrendingUp, AlertCircle, Trash2, Power, PowerOff } from 'lucide-react';
import ResponseTimeChart from './ResponseTimeChart';

export default function MonitorCard({ monitor, onUpdate }) {
  const [isDeleting, setIsDeleting] = useState(false);

  // Fetch stats for this monitor
  const { data: stats } = useQuery({
    queryKey: ['monitor-stats', monitor.id],
    queryFn: async () => {
      const response = await metricsAPI.getStats(monitor.id, 24);
      return response.data;
    },
    refetchInterval: 60000, // Refetch every minute
  });

  // Fetch health check history for chart
  const { data: healthChecks } = useQuery({
    queryKey: ['health-checks', monitor.id],
    queryFn: async () => {
      const response = await metricsAPI.getHealthChecks(monitor.id, 50);
      return response.data.checks;
    },
    refetchInterval: 60000, // Refetch every minute
  });

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${monitor.name}"?`)) {
      return;
    }

    setIsDeleting(true);
    try {
      await monitorAPI.delete(monitor.id);
      onUpdate();
    } catch (error) {
      alert('Failed to delete monitor');
      setIsDeleting(false);
    }
  };

  const handleToggleActive = async () => {
    try {
      await monitorAPI.update(monitor.id, { is_active: !monitor.is_active });
      onUpdate();
    } catch (error) {
      alert('Failed to update monitor');
    }
  };

  const uptimeColor = stats
    ? stats.uptime_percentage >= 99
      ? 'text-green-600'
      : stats.uptime_percentage >= 95
      ? 'text-yellow-600'
      : 'text-red-600'
    : 'text-gray-600';

  return (
    <div className="card hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="text-lg font-semibold text-gray-900">{monitor.name}</h3>
            {monitor.is_active ? (
              <span className="badge badge-success">Active</span>
            ) : (
              <span className="badge badge-warning">Inactive</span>
            )}
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <Globe className="w-4 h-4 mr-1" />
            <span className="truncate">{monitor.url}</span>
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={handleToggleActive}
            className="p-2 text-gray-600 hover:text-primary-600 hover:bg-gray-100 rounded-lg transition-colors"
            title={monitor.is_active ? 'Deactivate' : 'Activate'}
          >
            {monitor.is_active ? (
              <Power className="w-5 h-5" />
            ) : (
              <PowerOff className="w-5 h-5" />
            )}
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete monitor"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats ? (
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-gray-600 mb-1">Uptime (24h)</p>
            <p className={`text-2xl font-bold ${uptimeColor}`}>
              {stats.uptime_percentage.toFixed(1)}%
            </p>
          </div>

          <div>
            <p className="text-xs text-gray-600 mb-1">Avg Response</p>
            <div className="flex items-baseline space-x-1">
              <p className="text-2xl font-bold text-gray-900">
                {stats.avg_response_time ? Math.round(stats.avg_response_time) : '-'}
              </p>
              {stats.avg_response_time && (
                <span className="text-sm text-gray-600">ms</span>
              )}
            </div>
          </div>

          <div>
            <p className="text-xs text-gray-600 mb-1">Incidents</p>
            <div className="flex items-center space-x-1">
              <p className="text-2xl font-bold text-gray-900">{stats.total_incidents}</p>
              {stats.ongoing_incidents > 0 && (
                <span className="badge badge-error text-xs">{stats.ongoing_incidents} active</span>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
          <p className="text-sm text-gray-600 mt-2">Loading stats...</p>
        </div>
      )}

      {/* Response Time Chart */}
      {healthChecks && healthChecks.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <ResponseTimeChart data={healthChecks} />
        </div>
      )}

      {/* Status Indicator */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        {stats && stats.last_check_status !== null && stats.last_check_status !== undefined ? (
          <div className="flex items-center text-sm">
            {stats.last_check_status ? (
              <>
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                <span className="text-green-700">Operational</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></div>
                <span className="text-red-700">Down</span>
              </>
            )}
            {stats.last_check_at && (
              <span className="text-gray-500 ml-auto">
                Last checked: {new Date(stats.last_check_at).toLocaleTimeString()}
              </span>
            )}
          </div>
        ) : (
          <div className="flex items-center text-sm text-gray-500">
            <AlertCircle className="w-4 h-4 mr-2" />
            <span>No checks yet</span>
          </div>
        )}
      </div>
    </div>
  );
}
