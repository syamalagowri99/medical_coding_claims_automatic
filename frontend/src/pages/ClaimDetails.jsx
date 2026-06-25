import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { claimAPI } from '../services/api'
import Card from '../components/Card'
import { CheckCircle, Clock, AlertCircle, ChevronLeft } from 'lucide-react'

const statusConfig = {
  draft: { color: 'bg-gray-50 border-gray-200', textColor: 'text-gray-700', icon: 'gray', label: 'Draft' },
  submitted: { color: 'bg-blue-50 border-blue-200', textColor: 'text-blue-700', icon: 'blue', label: 'Submitted' },
  processing: { color: 'bg-yellow-50 border-yellow-200', textColor: 'text-yellow-700', icon: 'yellow', label: 'Processing' },
  approved: { color: 'bg-green-50 border-green-200', textColor: 'text-green-700', icon: 'green', label: 'Approved' },
  rejected: { color: 'bg-red-50 border-red-200', textColor: 'text-red-700', icon: 'red', label: 'Rejected' },
  denied: { color: 'bg-red-50 border-red-200', textColor: 'text-red-700', icon: 'red', label: 'Denied' },
}

function StatusBadge({ status }) {
  const normalizedStatus = String(status || '').toLowerCase()
  const config = statusConfig[normalizedStatus] || statusConfig.draft
  const iconMap = {
    gray: <Clock className="w-4 h-4" />,
    blue: <AlertCircle className="w-4 h-4" />,
    yellow: <Clock className="w-4 h-4" />,
    green: <CheckCircle className="w-4 h-4" />,
    red: <AlertCircle className="w-4 h-4" />,
  }

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${config.color} border ${config.textColor}`}>
      {iconMap[config.icon]}
      <span className="text-sm font-medium">{config.label}</span>
    </div>
  )
}

export default function ClaimDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [actionError, setActionError] = useState('')
  const [actionSuccess, setActionSuccess] = useState('')
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')

  const { data: claim, isLoading, error } = useQuery({
    queryKey: ['claim', id],
    queryFn: () => claimAPI.getById(id).then((r) => r.data),
    enabled: !!id,
  })

  const validateMutation = useMutation({
    mutationFn: (claimId) => claimAPI.validate(claimId),
    onSuccess: (res) => {
      setActionError('')
      setActionSuccess('Claim validated successfully')
      setTimeout(() => setActionSuccess(''), 5000)
      queryClient.invalidateQueries(['claims'])
      queryClient.invalidateQueries(['claim', id])
    },
    onError: (error) => {
      const message = error?.response?.data?.detail || error?.message || 'Validation failed'
      setActionError(message)
      setTimeout(() => setActionError(''), 5000)
    },
  })

  const submitMutation = useMutation({
    mutationFn: (claimId) => claimAPI.submit(claimId),
    onSuccess: () => {
      setActionError('')
      setActionSuccess('Claim submitted successfully')
      setTimeout(() => setActionSuccess(''), 5000)
      queryClient.invalidateQueries(['claims'])
      queryClient.invalidateQueries(['claim', id])
    },
    onError: (error) => {
      const message = error?.response?.data?.detail || error?.message || 'Submission failed'
      setActionError(message)
      setTimeout(() => setActionError(''), 5000)
    },
  })

  const approveMutation = useMutation({
    mutationFn: (claimId) => claimAPI.approveClaim(claimId),
    onSuccess: () => {
      setActionError('')
      setActionSuccess('Claim approved successfully')
      setTimeout(() => setActionSuccess(''), 5000)
      queryClient.invalidateQueries(['claims'])
      queryClient.invalidateQueries(['claim', id])
    },
    onError: (error) => {
      const message = error?.response?.data?.detail || error?.message || 'Approval failed'
      setActionError(message)
      setTimeout(() => setActionError(''), 5000)
    },
  })

  const rejectMutation = useMutation({
    mutationFn: (data) => claimAPI.rejectClaim(data.claimId, data.reason),
    onSuccess: () => {
      setActionError('')
      setActionSuccess('Claim rejected successfully')
      setTimeout(() => setActionSuccess(''), 5000)
      queryClient.invalidateQueries(['claims'])
      queryClient.invalidateQueries(['claim', id])
    },
    onError: (error) => {
      const message = error?.response?.data?.detail || error?.message || 'Rejection failed'
      setActionError(message)
      setTimeout(() => setActionError(''), 5000)
    },
  })

  if (isLoading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  if (error) return <div className="text-red-600">Failed to load claim</div>
  if (!claim) return <div className="text-gray-600">Claim not found.</div>

  const normalizedStatus = String(claim.status || '').toLowerCase()

  return (
    <div className="space-y-6">
      {actionError && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <p className="text-sm font-medium text-red-800">Error</p>
          <p className="text-sm text-red-700 mt-1">{actionError}</p>
        </div>
      )}
      
      {actionSuccess && (
        <div className="rounded-md bg-green-50 p-4 border border-green-200">
          <p className="text-sm font-medium text-green-800">Success</p>
          <p className="text-sm text-green-700 mt-1">{actionSuccess}</p>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button onClick={() => navigate(-1)} className="text-gray-600 hover:text-gray-900">
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Claim {claim.claim_number}</h2>
            <p className="text-gray-600 text-sm">{claim.insurance_provider} • Policy {claim.policy_number}</p>
          </div>
        </div>
        <StatusBadge status={claim.status} />
      </div>

      <Card>
        <h3 className="text-lg font-semibold mb-3">Claim Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Patient</p>
            <p className="font-medium">{claim.patient?.first_name} {claim.patient?.last_name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Amount</p>
            <p className="font-medium">${(claim.total_amount || 0).toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Created At</p>
            <p className="font-medium">{new Date(claim.created_at).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Status</p>
            <p className="font-medium capitalize">{String(claim.status || '').toLowerCase()}</p>
          </div>
          {claim.rendering_provider_npi && (
            <div>
              <p className="text-sm text-gray-600">Rendering Provider NPI</p>
              <p className="font-medium">{claim.rendering_provider_npi}</p>
            </div>
          )}
          {claim.place_of_service && (
            <div>
              <p className="text-sm text-gray-600">Place of Service</p>
              <p className="font-medium">{claim.place_of_service} {claim.place_of_service === "11" && "(Office)"}</p>
            </div>
          )}
          {claim.rejection_reason && (
            <div className="md:col-span-2">
              <p className="text-sm text-gray-600">Rejection Reason</p>
              <p className="font-medium text-red-700">{claim.rejection_reason}</p>
            </div>
          )}
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-4">Validations</h3>
        {claim.validations?.length > 0 ? (
          <div className="space-y-4">
            {(() => {
              const grouped = (claim.validations || []).reduce((acc, v) => {
                const category = v.validation_type || 'general'
                if (!acc[category]) acc[category] = []
                acc[category].push(v)
                return acc
              }, {})
              
              const categoryConfig = {
                documentation: { title: '📄 Documentation', color: 'bg-blue-50 border-blue-200 text-blue-800', badgeColor: 'bg-blue-200' },
                coding: { title: '💻 Coding Issues', color: 'bg-orange-50 border-orange-200 text-orange-800', badgeColor: 'bg-orange-200' },
                medical_necessity: { title: '🏥 Medical Necessity', color: 'bg-red-50 border-red-200 text-red-800', badgeColor: 'bg-red-200' },
                compliance: { title: '⚖️ Compliance', color: 'bg-purple-50 border-purple-200 text-purple-800', badgeColor: 'bg-purple-200' },
                general: { title: '⚠️ Other Issues', color: 'bg-yellow-50 border-yellow-200 text-yellow-800', badgeColor: 'bg-yellow-200' }
              }
              
              return Object.entries(grouped).map(([category, issues]) => {
                const config = categoryConfig[category] || categoryConfig.general
                return (
                  <div key={category} className={`border rounded-lg p-4 ${config.color}`}>
                    <h4 className="font-semibold mb-3">{config.title}</h4>
                    <ul className="space-y-2">
                      {issues.map((issue, idx) => (
                        <li key={idx} className="flex gap-2">
                          <span className={`flex-shrink-0 px-2 py-1 rounded text-xs font-medium ${config.badgeColor}`}>
                            {issue.severity || 'warning'}
                          </span>
                          <span className="flex-1">{issue.error_message || String(issue)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )
              })
            })()}
          </div>
        ) : (
          <div className="p-4 rounded-lg bg-green-50 border border-green-200 text-green-800">
            <p className="font-medium">✓ All validations passed</p>
            <p className="text-sm mt-1">This claim is ready for submission.</p>
          </div>
        )}
      </Card>

      <Card>
        <h3 className="text-lg font-semibold mb-3">Claim Items</h3>
        {claim.claim_items?.length > 0 ? (
          <div className="space-y-3">
            {claim.claim_items.map((item) => (
              <div key={item.id} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div>
                    <p className="text-sm text-gray-600">Description</p>
                    <p className="font-medium">{item.description || item.code || 'Line Item'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Amount</p>
                    <p className="font-medium text-lg">${(item.amount || 0).toFixed(2)}</p>
                  </div>
                  {item.procedure_code && (
                    <div>
                      <p className="text-sm text-gray-600">Procedure Code (CPT/HCPCS)</p>
                      <p className="font-medium">{item.procedure_code}</p>
                    </div>
                  )}
                  {item.diagnosis_code && (
                    <div>
                      <p className="text-sm text-gray-600">Diagnosis Code (ICD-10)</p>
                      <p className="font-medium">{item.diagnosis_code}</p>
                    </div>
                  )}
                  {item.service_date_start && (
                    <div>
                      <p className="text-sm text-gray-600">Service Date</p>
                      <p className="font-medium">{new Date(item.service_date_start).toLocaleDateString()} {item.service_date_end && item.service_date_end !== item.service_date_start ? `- ${new Date(item.service_date_end).toLocaleDateString()}` : ''}</p>
                    </div>
                  )}
                  {item.units && (
                    <div>
                      <p className="text-sm text-gray-600">Units</p>
                      <p className="font-medium">{item.quantity || 1} {item.units}</p>
                    </div>
                  )}
                  {!item.units && (
                    <div>
                      <p className="text-sm text-gray-600">Quantity</p>
                      <p className="font-medium">{item.quantity || 1}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No items added to this claim.</p>
        )}
      </Card>

      <div className="flex justify-end space-x-3">
        {normalizedStatus === 'draft' && (
          <>
            <button
              onClick={() => validateMutation.mutate(claim.id)}
              className="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-md hover:bg-gray-50"
            >
              {validateMutation.isLoading ? 'Validating...' : 'Validate'}
            </button>
            <button
              onClick={() => submitMutation.mutate(claim.id)}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
            >
              {submitMutation.isLoading ? 'Submitting...' : 'Submit Claim'}
            </button>
          </>
        )}
        {(normalizedStatus === 'submitted' || normalizedStatus === 'processing') && (
          <>
            <button
              onClick={() => setShowRejectModal(true)}
              className="bg-white text-red-700 border border-red-300 px-4 py-2 rounded-md hover:bg-red-50"
            >
              {rejectMutation.isLoading ? 'Rejecting...' : 'Reject'}
            </button>
            <button
              onClick={() => approveMutation.mutate(claim.id)}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              {approveMutation.isLoading ? 'Approving...' : 'Approve Claim'}
            </button>
          </>
        )}
      </div>

      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Reject Claim</h3>
            <p className="text-gray-600 mb-4">Please provide a reason for rejecting this claim.</p>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Enter rejection reason..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
              rows="4"
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowRejectModal(false)
                  setRejectionReason('')
                }}
                className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (rejectionReason.trim()) {
                    rejectMutation.mutate({ claimId: claim.id, reason: rejectionReason })
                    setShowRejectModal(false)
                    setRejectionReason('')
                  }
                }}
                disabled={!rejectionReason.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Reject Claim
              </button>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
