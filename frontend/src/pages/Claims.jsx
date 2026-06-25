import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { claimAPI, patientAPI } from '../services/api'
import { Receipt, CheckCircle, Clock, AlertCircle, Plus, X, ChevronRight } from 'lucide-react'
import Card from '../components/Card'

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

function ClaimProgressTimeline() {
  return (
    <div className="my-4 p-4 bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg border border-primary-100">
      <h4 className="text-sm font-semibold text-gray-900 mb-3">Claim Progress</h4>
      <div className="flex items-center justify-between text-xs">
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 rounded-full bg-primary-500 text-white flex items-center justify-center mb-1">
            1
          </div>
          <span className="text-gray-600">Created</span>
        </div>
        <div className="flex-1 h-1 bg-primary-300 mx-2 mt-3"></div>
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 rounded-full bg-primary-500 text-white flex items-center justify-center mb-1">
            2
          </div>
          <span className="text-gray-600">Validated</span>
        </div>
        <div className="flex-1 h-1 bg-gray-300 mx-2 mt-3"></div>
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 rounded-full bg-gray-300 text-gray-600 flex items-center justify-center mb-1">
            3
          </div>
          <span className="text-gray-600">Submitted</span>
        </div>
        <div className="flex-1 h-1 bg-gray-300 mx-2 mt-3"></div>
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 rounded-full bg-gray-300 text-gray-600 flex items-center justify-center mb-1">
            4
          </div>
          <span className="text-gray-600">Approved</span>
        </div>
      </div>
    </div>
  )
}

export default function Claims() {
  const [selectedPatient, setSelectedPatient] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [claimNumber, setClaimNumber] = useState('')
  const [insuranceProvider, setInsuranceProvider] = useState('')
  const [policyNumber, setPolicyNumber] = useState('')
  const [createError, setCreateError] = useState('')
  const [createSuccess, setCreateSuccess] = useState('')
  const [actionMessage, setActionMessage] = useState({ type: '', text: '' })
  const queryClient = useQueryClient()

  // Generate claim number format: CLM-YYYYMM-XXXXX
  const generateClaimNumber = useMemo(() => {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const random = String(Math.floor(Math.random() * 100000)).padStart(5, '0')
    return `CLM-${year}${month}-${random}`
  }, [])

  const { data: patients } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientAPI.list().then(res => res.data),
  })

  const { data: claims } = useQuery({
    queryKey: ['claims', selectedPatient],
    queryFn: () => selectedPatient
      ? claimAPI.getByPatient(selectedPatient).then(res => res.data)
      : claimAPI.list().then(res => res.data),
    enabled: !!selectedPatient || selectedPatient === '',
  })

  const submitMutation = useMutation({
    mutationFn: (claimId) => claimAPI.submit(claimId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['claims'] })
      queryClient.invalidateQueries({ queryKey: ['claims', selectedPatient] })
      setActionMessage({ type: 'success', text: 'Claim submitted successfully.' })
      setTimeout(() => setActionMessage({ type: '', text: '' }), 5000)
    },
    onError: (error) => {
      setActionMessage({
        type: 'error',
        text: error?.response?.data?.detail || error?.message || 'Submit failed'
      })
      setTimeout(() => setActionMessage({ type: '', text: '' }), 5000)
    },
  })

  const validateMutation = useMutation({
    mutationFn: (claimId) => claimAPI.validate(claimId),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['claims'] })
      queryClient.invalidateQueries({ queryKey: ['claims', selectedPatient] })
      const issues = response?.data?.validations?.length ?? 0
      setActionMessage({
        type: issues > 0 ? 'warning' : 'success',
        text: issues > 0
          ? `Validation completed: ${issues} issue(s) found.`
          : 'Validation passed with no issues.'
      })
      setTimeout(() => setActionMessage({ type: '', text: '' }), 5000)
    },
    onError: (error) => {
      setActionMessage({
        type: 'error',
        text: error?.response?.data?.detail || error?.message || 'Validation failed'
      })
      setTimeout(() => setActionMessage({ type: '', text: '' }), 5000)
    },
  })

  const createClaimMutation = useMutation({
    mutationFn: (claimData) => claimAPI.create(claimData),
    onSuccess: (response) => {
      queryClient.invalidateQueries(['claims'])
      queryClient.invalidateQueries({ queryKey: ['claims', selectedPatient], exact: true })
      setCreateSuccess(`Claim ${response.data.claim_number} created successfully!`)
      handleResetForm()
      setTimeout(() => setCreateSuccess(''), 4000)
    },
    onError: (error) => {
      const message = error?.response?.data?.detail || error?.message || 'Failed to create claim'
      setCreateError(message)
    },
  })

  const handleResetForm = () => {
    setClaimNumber('')
    setInsuranceProvider('')
    setPolicyNumber('')
    setCreateError('')
    setShowCreateForm(false)
  }

  const handleCreateClaim = () => {
    if (!selectedPatient) {
      setCreateError('Please select a patient')
      return
    }
    if (!claimNumber.trim()) {
      setCreateError('Claim number is required')
      return
    }
    if (!insuranceProvider.trim()) {
      setCreateError('Insurance provider is required')
      return
    }
    if (!policyNumber.trim()) {
      setCreateError('Policy number is required')
      return
    }

    createClaimMutation.mutate({
      patient_id: selectedPatient,
      claim_number: claimNumber,
      insurance_provider: insuranceProvider,
      policy_number: policyNumber,
    })
  }

  const handleOpenCreateForm = () => {
    setShowCreateForm(true)
    setClaimNumber(generateClaimNumber)
    setInsuranceProvider('')
    setPolicyNumber('')
    setCreateError('')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Claims Management</h2>
          <p className="text-gray-600 mt-1">Create, validate, and submit medical claims</p>
        </div>
        <button
          type="button"
          onClick={handleOpenCreateForm}
          className="bg-primary-500 text-white px-4 py-2 rounded-md hover:bg-primary-600 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Claim
        </button>
      </div>

      {/* Create Claim Form */}
      {showCreateForm && (
        <Card>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Create New Claim</h3>
            <button
              onClick={handleResetForm}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {createError && (
            <div className="mb-4 rounded-md bg-red-50 p-3 text-red-700 border border-red-100">
              <p className="text-sm font-medium">Error</p>
              <p className="text-sm">{createError}</p>
            </div>
          )}

          {createSuccess && (
            <div className="mb-4 rounded-md bg-green-50 p-3 text-green-700 border border-green-100">
              <p className="text-sm font-medium">✓ Success</p>
              <p className="text-sm">{createSuccess}</p>
            </div>
          )}


          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Patient *</label>
              <select
                value={selectedPatient}
                onChange={(e) => {
                  setSelectedPatient(e.target.value)
                  setCreateError('')
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select Patient</option>
                {patients?.map((patient) => (
                  <option key={patient.id} value={patient.id}>
                    {patient.first_name} {patient.last_name} ({patient.patient_id})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Claim Number *</label>
              <input
                type="text"
                value={claimNumber}
                onChange={(e) => {
                  setClaimNumber(e.target.value)
                  setCreateError('')
                }}
                placeholder="CLM-XXXXX"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <p className="text-xs text-gray-500 mt-1">Auto-generated, can be modified</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Insurance Provider *</label>
              <input
                type="text"
                value={insuranceProvider}
                onChange={(e) => {
                  setInsuranceProvider(e.target.value)
                  setCreateError('')
                }}
                placeholder="e.g., Blue Cross, Aetna, UnitedHealth"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Policy Number *</label>
              <input
                type="text"
                value={policyNumber}
                onChange={(e) => {
                  setPolicyNumber(e.target.value)
                  setCreateError('')
                }}
                placeholder="POL-XXXXX"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="mt-4 flex justify-end space-x-3">
            <button
              type="button"
              onClick={handleResetForm}
              className="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleCreateClaim}
              disabled={createClaimMutation.isPending}
              className="bg-primary-500 text-white px-4 py-2 rounded-md hover:bg-primary-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
            >
              {createClaimMutation.isPending ? 'Creating...' : 'Create Claim'}
            </button>
          </div>
        </Card>
      )}

      {/* Claims List */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Claims</h3>
          <select
            value={selectedPatient}
            onChange={(e) => setSelectedPatient(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Patients</option>
            {patients?.map((patient) => (
              <option key={patient.id} value={patient.id}>
                {patient.first_name} {patient.last_name}
              </option>
            ))}
          </select>
        </div>

        {actionMessage.text && (
          <div className={`mb-4 rounded-md p-3 border ${actionMessage.type === 'success' ? 'bg-green-50 border-green-100 text-green-700' : actionMessage.type === 'warning' ? 'bg-yellow-50 border-yellow-100 text-yellow-700' : 'bg-red-50 border-red-100 text-red-700'}`}>
            <p className="text-sm font-medium">
              {actionMessage.type === 'success' ? 'Success' : actionMessage.type === 'warning' ? 'Validation Result' : 'Error'}
            </p>
            <p className="text-sm">{actionMessage.text}</p>
          </div>
        )}
        <div className="space-y-3">
          {claims?.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No claims found</p>
          ) : (
            claims?.map((claim) => (
              <div key={claim.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow bg-white">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start flex-1">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center mr-3 flex-shrink-0">
                      <Receipt className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-900">{claim.claim_number}</p>
                      <p className="text-xs text-gray-600 mt-0.5">
                        {claim.insurance_provider} • <span className="font-medium">${claim.total_amount?.toFixed(2) || '0.00'}</span>
                      </p>
                    </div>
                  </div>
                  <StatusBadge status={claim.status || 'draft'} />
                </div>

                {claim.status === 'draft' && <ClaimProgressTimeline />}

                <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
                  <div className="flex items-center space-x-4 text-xs">
                    {claim.validations?.length > 0 && (
                      <div className="flex items-center text-yellow-600 bg-yellow-50 px-2 py-1 rounded">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        <span>{claim.validations.length} issues</span>
                      </div>
                    )}
                    <div className="flex items-center text-gray-600">
                      <Receipt className="w-3 h-3 mr-1" />
                      <span>{claim.claim_items?.length || 0} items</span>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    {claim.status === 'draft' && (
                      <>
                        <button
                          type="button"
                          onClick={() => validateMutation.mutate(claim.id)}
                          disabled={validateMutation.isPending}
                          className="text-primary-600 hover:text-primary-700 text-xs font-semibold disabled:text-gray-300 transition-colors"
                        >
                          {validateMutation.isPending ? 'Validating...' : 'Validate'}
                        </button>
                        <button
                          type="button"
                          onClick={() => submitMutation.mutate(claim.id)}
                          disabled={submitMutation.isPending}
                          className="bg-primary-600 text-white px-3 py-1 rounded text-xs font-semibold hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                        >
                          {submitMutation.isPending ? 'Submitting...' : 'Submit'}
                        </button>
                      </>
                    )}
                    <Link to={`/claims/${claim.id}`} className="text-gray-600 hover:text-gray-900 text-xs font-semibold transition-colors flex items-center">
                      View <ChevronRight className="w-3 h-3 ml-0.5" />
                    </Link>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  )
}
