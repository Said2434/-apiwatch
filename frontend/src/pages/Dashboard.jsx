import { useState, useEffect, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { monitorAPI, metricsAPI } from '../lib/api';
import { useAuthStore } from '../store/authStore';
import { Activity, Plus, LogOut, TrendingUp, AlertCircle, CheckCircle2, XCircle, Wifi, WifiOff } from 'lucide-react';
import MonitorCard from '../components/MonitorCard';
import AddMonitorModal from '../components/AddMonitorModal';

export default function Dashboard() {
  const { user, logout } = useAuthStore();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const queryClient = useQueryClient();

  // Fetch monitors
  const { data: monitorsData, isLoading: monitorsLoading, refetch: refetchMonitors } = useQuery({
    queryKey: ['monitors'],
    queryFn: async () => {
      const response = await monitorAPI.list();
      return response.data;
    },
  });

  // Fetch dashboard stats
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await metricsAPI.getDashboard(24);
      return response.data;
    },
    refetchInterval: 60000, // Refetch every minute
  });

  const handleMonitorAdded = () => {
    refetchMonitors();
    setIsAddModalOpen(false);
  };

  // WebSocket connection for real-time updates
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_API_URL.replace('http', 'ws') + '/api/v1/ws';

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          console.log('WebSocket message:', message);

          if (message.type === 'stats_updated') {
            // Invalidate all queries to trigger refetch
            queryClient.invalidateQueries(['dashboard']);
            queryClient.invalidateQueries(['monitor-stats']);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);

          // Reconnect after 5 seconds
          setTimeout(() => {
            console.log('Attempting to reconnect...');
            connectWebSocket();
          }, 5000);
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [queryClient]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">APIWatch</h1>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* WebSocket Connection Status */}
              <div className="flex items-center space-x-2">
                {isConnected ? (
                  <>
                    <Wifi className="w-4 h-4 text-green-600" />
                    <span className="text-xs text-green-600 font-medium">Live</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-4 h-4 text-gray-400" />
                    <span className="text-xs text-gray-400 font-medium">Connecting...</span>
                  </>
                )}
              </div>

              <button
                onClick={logout}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
              >
                <LogOut className="w-5 h-5" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        {dashboardData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Monitors</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {dashboardData.total_monitors}
                  </p>
                </div>
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Activity className="w-6 h-6 text-primary-600" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Monitors</p>
                  <p className="text-3xl font-bold text-green-600 mt-1">
                    {dashboardData.active_monitors}
                  </p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Overall Uptime</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {dashboardData.overall_uptime.toFixed(1)}%
                  </p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Ongoing Incidents</p>
                  <p className="text-3xl font-bold text-red-600 mt-1">
                    {dashboardData.ongoing_incidents}
                  </p>
                </div>
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <XCircle className="w-6 h-6 text-red-600" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Monitors Section */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Your Monitors</h2>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Add Monitor</span>
          </button>
        </div>

        {/* Monitor List */}
        {monitorsLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading monitors...</p>
          </div>
        ) : monitorsData?.monitors.length === 0 ? (
          <div className="card text-center py-12">
            <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No monitors yet</h3>
            <p className="text-gray-600 mb-6">
              Get started by adding your first API monitor
            </p>
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="btn btn-primary inline-flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Add Your First Monitor</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {monitorsData?.monitors.map((monitor) => (
              <MonitorCard
                key={monitor.id}
                monitor={monitor}
                onUpdate={refetchMonitors}
              />
            ))}
          </div>
        )}
      </main>

      {/* Add Monitor Modal */}
      <AddMonitorModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={handleMonitorAdded}
      />
    </div>
  );
}
