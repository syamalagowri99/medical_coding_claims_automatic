import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentAPI, patientAPI } from '../services/api'
import { Upload, FileText, CheckCircle, Clock, AlertCircle, X, RefreshCw, File } from 'lucide-react'
import Card from '../components/Card'

export default function Documents() {
  const [selectedPatient, setSelectedPatient] = useState('')
  const [file, setFile] = useState(null)
  const [documentType, setDocumentType] = useState('clinical_note')
  const [uploadError, setUploadError] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState('')
  const [viewingDocument, setViewingDocument] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)
  const queryClient = useQueryClient()

  const { data: patients } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientAPI.list().then(res => res.data),
  })

  const { data: documents, isLoading: isDocsLoading, isError: isDocsError, error: docsError, refetch } = useQuery({
    queryKey: ['documents', selectedPatient],
    queryFn: () => selectedPatient 
      ? documentAPI.getByPatient(selectedPatient).then(res => res.data)
      : documentAPI.list().then(res => res.data),
    refetchInterval: 3000, // Auto-refresh every 3 seconds
  })

  // Auto-refresh documents list when upload succeeds
  useEffect(() => {
    if (uploadSuccess) {
      const timer = setTimeout(() => {
        refetch()
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [uploadSuccess, refetch])

  const uploadMutation = useMutation({
    mutationFn: (data) => documentAPI.upload(data.patientId, data.file, data.documentType),
    onSuccess: (response) => {
      queryClient.invalidateQueries(['documents'])
      queryClient.invalidateQueries({ queryKey: ['documents', selectedPatient], exact: true })
      setFile(null)
      setUploadError('')
      setUploadSuccess(`Document "${response.data.filename}" uploaded successfully and processing...`)
      setTimeout(() => setUploadSuccess(''), 5000)
    },
    onError: (error) => {
      const message = error?.response?.data?.detail || error?.message || 'Upload failed.'
      setUploadError(message)
    },
  })

  const reprocessMutation = useMutation({
    mutationFn: (documentId) => documentAPI.process(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries(['documents'])
      queryClient.invalidateQueries({ queryKey: ['documents', selectedPatient], exact: true })
    },
  })

  const handleUpload = () => {
    if (!selectedPatient) {
      setUploadError('Please select a patient before uploading.')
      return
    }
    if (!file) {
      setUploadError('Please select or drop a file to upload.')
      return
    }

    setUploadError('')
    uploadMutation.mutate({ patientId: Number(selectedPatient), file, documentType })
  }

  const handleViewDocument = (doc) => {
    setViewingDocument(doc)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (['.pdf', '.txt', '.docx'].some(ext => droppedFile.name.toLowerCase().endsWith(ext))) {
        setFile(droppedFile)
        setUploadError('')
        if (selectedPatient) {
          uploadMutation.mutate({ patientId: Number(selectedPatient), file: droppedFile, documentType })
        } else {
          setUploadError('Select a patient before dropping a document.')
        }
      } else {
        setUploadError('Please drop a PDF, TXT, or DOCX file')
      }
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (['.pdf', '.txt', '.docx'].some(ext => selectedFile.name.toLowerCase().endsWith(ext))) {
        setFile(selectedFile)
        setUploadError('')
        if (selectedPatient) {
          uploadMutation.mutate({ patientId: Number(selectedPatient), file: selectedFile, documentType })
        }
      } else {
        setUploadError('Please select a PDF, TXT, or DOCX file')
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Document</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Patient *</label>
            <select
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="clinical_note">Clinical Note</option>
              <option value="discharge_summary">Discharge Summary</option>
              <option value="operative_report">Operative Report</option>
              <option value="lab_result">Lab Result</option>
              <option value="radiology_report">Radiology Report</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">File or use drag-and-drop below</label>
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.txt,.docx"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={handleClick}
          className={`relative border-2 border-dashed rounded-lg p-8 transition-all cursor-pointer ${
            dragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400 bg-gray-50 hover:bg-primary-50'
          }`}
        >
          <div className="text-center">
            {file ? (
              <>
                <File className="w-12 h-12 text-primary-500 mx-auto mb-3" />
                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </>
            ) : (
              <>
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-sm font-medium text-gray-900">
                  Drag and drop your file here, or click to select
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Supported formats: PDF, TXT, DOCX (Max 10MB)
                </p>
              </>
            )}
          </div>
        </div>

        <div className="mt-4 space-y-3">
          {uploadError && (
            <div className="rounded-md bg-red-50 p-3 text-red-700 border border-red-100">
              <p className="text-sm font-medium">Upload failed</p>
              <p className="text-sm">{uploadError}</p>
            </div>
          )}
          {uploadSuccess && (
            <div className="rounded-md bg-green-50 p-3 text-green-700 border border-green-100">
              <p className="text-sm font-medium">✓ Success</p>
              <p className="text-sm">{uploadSuccess}</p>
            </div>
          )}
          <div className="flex justify-end">
            <button
              type="button"
              onClick={handleUpload}
              disabled={!file || !selectedPatient || uploadMutation.isPending}
              className="bg-primary-500 text-white px-4 py-2 rounded-md hover:bg-primary-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
            >
              <Upload className="w-4 h-4 mr-2" />
              {uploadMutation.isPending ? 'Uploading...' : 'Upload Document'}
            </button>
          </div>
        </div>
      </Card>

      {/* Documents List */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Documents</h3>
        <div className="space-y-3">
          {isDocsLoading ? (
            <p className="text-gray-500 text-center py-8">Loading documents...</p>
          ) : isDocsError ? (
            <div className="rounded-md bg-red-50 p-3 text-red-700 border border-red-100">
              <p className="text-sm font-medium">Failed to load documents</p>
              <p className="text-sm">{docsError?.message || 'An error occurred while fetching documents.'}</p>
            </div>
          ) : documents?.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No documents found</p>
          ) : (
            documents?.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-md hover:bg-gray-50">
                <div className="flex items-center flex-1">
                  <FileText className="w-5 h-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                    <p className="text-xs text-gray-500">
                      {doc.document_type} • {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    {doc.status === 'processed' && (
                      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    )}
                    {doc.status === 'processing' && (
                      <Clock className="w-5 h-5 text-yellow-500 mr-2" />
                    )}
                    {doc.status === 'failed' && (
                      <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                    )}
                    <span className="text-sm text-gray-600 capitalize">{doc.status}</span>
                  </div>
                  <div className="flex gap-2">
                    {doc.status === 'failed' && (
                      <button
                        onClick={() => reprocessMutation.mutate(doc.id)}
                        disabled={reprocessMutation.isPending}
                        className="text-amber-600 hover:text-amber-700 text-sm font-medium flex items-center gap-1"
                      >
                        <RefreshCw className="w-4 h-4" />
                        Retry
                      </button>
                    )}
                    <button 
                      onClick={() => handleViewDocument(doc)}
                      className="text-primary-500 hover:text-primary-600 text-sm font-medium"
                    >
                      View
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Document Viewer Modal */}
      {viewingDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{viewingDocument.filename}</h3>
                <p className="text-xs text-gray-500 mt-1">
                  Status: <span className="capitalize font-medium text-gray-700">{viewingDocument.status}</span>
                </p>
              </div>
              <button
                onClick={() => setViewingDocument(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-auto bg-gray-50 p-4 rounded border border-gray-200">
              {viewingDocument.status === 'processing' ? (
                <div className="flex items-center justify-center h-32">
                  <div className="text-center">
                    <Clock className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
                    <p className="text-gray-600">Document is being processed...</p>
                  </div>
                </div>
              ) : viewingDocument.status === 'failed' ? (
                <div className="flex items-center justify-center h-32">
                  <div className="text-center">
                    <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
                    <p className="text-gray-600">Failed to process document</p>
                  </div>
                </div>
              ) : viewingDocument.content_text ? (
                <div className="text-content">
                  <pre className="whitespace-pre-wrap break-words text-sm font-mono text-gray-800 bg-white p-3 rounded border border-gray-200">
                    {viewingDocument.content_text}
                  </pre>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No content available</p>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between">
              {viewingDocument.status === 'failed' && (
                <button
                  onClick={() => {
                    reprocessMutation.mutate(viewingDocument.id)
                    setViewingDocument(null)
                  }}
                  disabled={reprocessMutation.isPending}
                  className="bg-amber-600 text-white px-4 py-2 rounded-md hover:bg-amber-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {reprocessMutation.isPending ? 'Retrying...' : 'Retry Processing'}
                </button>
              )}
              <button
                onClick={() => setViewingDocument(null)}
                className="ml-auto bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
              >
                Close
              </button>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
