import { useState } from 'react';
import { X } from 'lucide-react';
import { monitorAPI } from '../lib/api';

export default function AddMonitorModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    method: 'GET',
    expected_status: 200,
    check_interval: 60,
    timeout: 10,
    is_active: true,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await monitorAPI.create(formData);
      // Reset form
      setFormData({
        name: '',
        url: '',
        method: 'GET',
        expected_status: 200,
        check_interval: 60,
        timeout: 10,
        is_active: true,
      });
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create monitor');
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Add New Monitor</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Name */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Monitor Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input"
                placeholder="Production API"
                required
              />
            </div>

            {/* URL */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL *
              </label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="input"
                placeholder="https://api.example.com/health"
                required
              />
            </div>

            {/* Method */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                HTTP Method *
              </label>
              <select
                value={formData.method}
                onChange={(e) => setFormData({ ...formData, method: e.target.value })}
                className="input"
                required
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="PATCH">PATCH</option>
                <option value="DELETE">DELETE</option>
                <option value="HEAD">HEAD</option>
                <option value="OPTIONS">OPTIONS</option>
              </select>
            </div>

            {/* Expected Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expected Status Code *
              </label>
              <input
                type="number"
                value={formData.expected_status}
                onChange={(e) => setFormData({ ...formData, expected_status: parseInt(e.target.value) })}
                className="input"
                min="100"
                max="599"
                required
              />
            </div>

            {/* Check Interval */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Check Interval (seconds) *
              </label>
              <input
                type="number"
                value={formData.check_interval}
                onChange={(e) => setFormData({ ...formData, check_interval: parseInt(e.target.value) })}
                className="input"
                min="10"
                max="3600"
                required
              />
              <p className="mt-1 text-xs text-gray-500">How often to check (10-3600 seconds)</p>
            </div>

            {/* Timeout */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Timeout (seconds) *
              </label>
              <input
                type="number"
                value={formData.timeout}
                onChange={(e) => setFormData({ ...formData, timeout: parseInt(e.target.value) })}
                className="input"
                min="1"
                max="60"
                required
              />
              <p className="mt-1 text-xs text-gray-500">Request timeout (1-60 seconds)</p>
            </div>

            {/* Active */}
            <div className="md:col-span-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  Start monitoring immediately
                </span>
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
            >
              {isSubmitting ? 'Creating...' : 'Create Monitor'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
