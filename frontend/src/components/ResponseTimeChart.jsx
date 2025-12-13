import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function ResponseTimeChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 text-sm">
        No response time data available yet
      </div>
    );
  }

  // Transform data for recharts
  const chartData = data.map((check) => ({
    time: new Date(check.checked_at).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    }),
    responseTime: check.response_time || 0,
    isUp: check.is_up,
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-medium text-gray-900">{data.time}</p>
          <p className="text-sm text-gray-600">
            Response: <span className="font-semibold text-primary-600">{data.responseTime}ms</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Status: <span className={data.isUp ? 'text-green-600' : 'text-red-600'}>
              {data.isUp ? 'Up' : 'Down'}
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  // Determine line color based on average response time
  const avgResponseTime = chartData.reduce((sum, d) => sum + d.responseTime, 0) / chartData.length;
  const lineColor = avgResponseTime < 500 ? '#10b981' : avgResponseTime < 1000 ? '#f59e0b' : '#ef4444';

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs font-medium text-gray-600">Response Time (24h)</h4>
        <div className="flex items-center space-x-2 text-xs">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
            <span className="text-gray-600">&lt;500ms</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
            <span className="text-gray-600">500-1000ms</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
            <span className="text-gray-600">&gt;1000ms</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={150}>
        <LineChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10, fill: '#6b7280' }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fontSize: 10, fill: '#6b7280' }}
            label={{ value: 'ms', angle: -90, position: 'insideLeft', style: { fontSize: 10, fill: '#6b7280' } }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="responseTime"
            stroke={lineColor}
            strokeWidth={2}
            dot={{ fill: lineColor, r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
