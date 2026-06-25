import Card from '../components/Card'
import { Activity, Shield, Clock } from 'lucide-react'

export default function Audit() {
  const auditLogs = [
    {
      id: 1,
      user: 'admin',
      action: 'Created patient record',
      entity: 'Patient #12345',
      timestamp: '2024-01-15 10:30:00',
      ip: '192.168.1.100',
    },
    {
      id: 2,
      user: 'coder1',
      action: 'Approved medical code',
      entity: 'Code E11.9',
      timestamp: '2024-01-15 10:25:00',
      ip: '192.168.1.101',
    },
    {
      id: 3,
      user: 'coder1',
      action: 'Uploaded document',
      entity: 'Document #456',
      timestamp: '2024-01-15 10:20:00',
      ip: '192.168.1.101',
    },
    {
      id: 4,
      user: 'admin',
      action: 'Created claim',
      entity: 'Claim #CLM-001',
      timestamp: '2024-01-15 10:15:00',
      ip: '192.168.1.100',
    },
    {
      id: 5,
      user: 'reviewer1',
      action: 'Validated claim',
      entity: 'Claim #CLM-001',
      timestamp: '2024-01-15 10:10:00',
      ip: '192.168.1.102',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">Audit Logs</h2>
        <p className="text-gray-600 mt-1">Track all system activities for compliance and security</p>
      </div>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">HIPAA Compliant</span>
          </div>
        </div>

        <div className="space-y-3">
          {auditLogs.map((log) => (
            <div key={log.id} className="p-4 border border-gray-200 rounded-md hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex items-start">
                  <Activity className="w-5 h-5 text-primary-500 mr-3 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{log.action}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      User: {log.user} • Entity: {log.entity}
                    </p>
                    <div className="flex items-center mt-2 text-xs text-gray-400">
                      <Clock className="w-3 h-3 mr-1" />
                      {log.timestamp} • IP: {log.ip}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 rounded-md">
            <p className="text-2xl font-bold text-green-600">100%</p>
            <p className="text-sm text-green-700">Audit Trail Coverage</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-md">
            <p className="text-2xl font-bold text-blue-600">5,234</p>
            <p className="text-sm text-blue-700">Total Log Entries</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-md">
            <p className="text-2xl font-bold text-purple-600">0</p>
            <p className="text-sm text-purple-700">Security Incidents</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
