import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Layers, 
  Clock, 
  Cpu, 
  FileCheck
} from 'lucide-react';
import api from '../services/api';

export default function DocumentIngestion() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [docType, setDocType] = useState('syllabus'); // 'syllabus' | 'past_paper'
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [documentsList, setDocumentsList] = useState([]);
  const [reviewItems, setReviewItems] = useState([]);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [cRes, dRes] = await Promise.all([
        api.getCourses(),
        api.getDocuments()
      ]);
      setCourses(cRes.data);
      if (cRes.data.length > 0) setSelectedCourse(cRes.data[0].id);
      setDocumentsList(dRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setUploadResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('doc_type', docType);
    if (selectedCourse) formData.append('course_id', selectedCourse);

    try {
      const res = await api.uploadDocument(formData);
      setUploadResult(res.data);
      setReviewItems(res.data.details?.extracted_data || []);
      setSelectedFile(null);
      await loadData();
    } catch (err) {
      console.error(err);
      alert('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  const handleApprove = async () => {
    if (!uploadResult?.document_id) return;
    setApproving(true);
    try {
      const res = await api.approveDocument(uploadResult.document_id, {
        document_id: uploadResult.document_id,
        extracted_data: reviewItems,
      });
      setUploadResult({ ...uploadResult, status: res.data.status, approved: true });
      await loadData();
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setApproving(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      
      {/* Header */}
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
          <UploadCloud className="w-5 h-5 text-brand-600" />
          <span>Academic Document Ingestion & Structured Parsing</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Ingest PDF, DOCX, or scanned documents. Automatically extracts syllabus modules or past exam questions and indexes into ChromaDB.
        </p>
      </div>

      {/* Ingestion Dropzone & Form */}
      <form onSubmit={handleUpload} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Target Academic Course</label>
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2.5 font-medium focus:ring-2 focus:ring-brand-500"
            >
              {courses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} - {c.title}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Document Classification</label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setDocType('syllabus')}
                className={`py-2 px-3 rounded-lg text-xs font-bold border transition ${
                  docType === 'syllabus'
                    ? 'bg-brand-50 border-brand-500 text-brand-700'
                    : 'bg-slate-50 border-slate-200 text-slate-600'
                }`}
              >
                Syllabus & Curriculum
              </button>
              <button
                type="button"
                onClick={() => setDocType('past_paper')}
                className={`py-2 px-3 rounded-lg text-xs font-bold border transition ${
                  docType === 'past_paper'
                    ? 'bg-brand-50 border-brand-500 text-brand-700'
                    : 'bg-slate-50 border-slate-200 text-slate-600'
                }`}
              >
                Historical Exam Paper
              </button>
              <button
                type="button"
                onClick={() => setDocType('exam_template')}
                className={`py-2 px-3 rounded-lg text-xs font-bold border transition ${
                  docType === 'exam_template'
                    ? 'bg-brand-50 border-brand-500 text-brand-700'
                    : 'bg-slate-50 border-slate-200 text-slate-600'
                }`}
              >
                Exam Template
              </button>
            </div>
          </div>
        </div>

        {/* File Drag/Drop Area */}
        <div className="border-2 border-dashed border-slate-200 hover:border-brand-400 bg-slate-50/50 rounded-2xl p-8 text-center transition">
          <input
            type="file"
            id="fileInput"
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleFileChange}
            className="hidden"
          />
          <label htmlFor="fileInput" className="cursor-pointer flex flex-col items-center space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-brand-50 text-brand-600 flex items-center justify-center shadow-sm">
              <UploadCloud className="w-6 h-6" />
            </div>
            <span className="text-sm font-bold text-slate-800">
              {selectedFile ? selectedFile.name : 'Choose a file or drag & drop here'}
            </span>
            <span className="text-xs text-slate-400">
              Supports syllabus guides, question papers (.PDF, .DOCX, .TXT)
            </span>
            {selectedFile && (
              <span className="text-[11px] font-mono text-brand-600 bg-brand-50 px-2 py-0.5 rounded">
                Size: {Math.round(selectedFile.size / 1024)} KB
              </span>
            )}
          </label>
        </div>

        <button
          type="submit"
          disabled={!selectedFile || uploading}
          className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-bold py-2.5 rounded-xl text-xs transition flex items-center justify-center space-x-1.5"
        >
          <Cpu className="w-4 h-4" />
          <span>{uploading ? 'Extracting, Chunking & Indexing...' : 'Start Document Processing Pipeline'}</span>
        </button>

      </form>

      {/* Extraction Result Card */}
      {uploadResult && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 text-xs space-y-4 animate-in fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 font-bold text-sm text-slate-900">
              {uploadResult.approved ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : <FileCheck className="w-5 h-5 text-brand-600" />}
              <span>{uploadResult.approved ? 'Extraction Approved and Indexed' : 'Review Extracted Information'}</span>
            </div>
            <span className="text-slate-500">{uploadResult.filename}</span>
          </div>
          {!uploadResult.approved && (
            <div className="space-y-3">
              {reviewItems.map((item, index) => (
                <div key={index} className="border border-slate-200 rounded-xl p-3 space-y-2">
                  <div className="font-bold text-slate-700">Extracted item {index + 1}</div>
                  {item.text !== undefined ? (
                    <textarea
                      value={item.text}
                      onChange={(e) => setReviewItems(reviewItems.map((v, i) => i === index ? { ...v, text: e.target.value } : v))}
                      rows={4}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5"
                    />
                  ) : item.unit_number !== undefined ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <label>Unit Number
                        <input type="number" value={item.unit_number} onChange={(e) => setReviewItems(reviewItems.map((v,i) => i === index ? {...v, unit_number:parseInt(e.target.value)||1} : v))} className="mt-1 w-full border rounded-lg p-2" />
                      </label>
                      <label>Unit Title
                        <input value={item.title || ''} onChange={(e) => setReviewItems(reviewItems.map((v,i) => i === index ? {...v, title:e.target.value} : v))} className="mt-1 w-full border rounded-lg p-2" />
                      </label>
                      <label className="sm:col-span-2">Topics
                        {(item.topics || []).map((topic, topicIndex) => (
                          <div key={topicIndex} className="mt-1 flex gap-2">
                            <input value={topic.name || ''} onChange={(e) => setReviewItems(reviewItems.map((v,i) => i === index ? {...v, topics:(v.topics || []).map((t,j) => j === topicIndex ? {...t,name:e.target.value} : t)} : v))} className="flex-1 border rounded-lg p-2" />
                            <button type="button" onClick={() => setReviewItems(reviewItems.map((v,i) => i === index ? {...v, topics:(v.topics || []).filter((_,j) => j !== topicIndex)} : v))} className="text-rose-600 font-bold px-2">Remove</button>
                          </div>
                        ))}
                        <button type="button" onClick={() => setReviewItems(reviewItems.map((v,i) => i === index ? {...v, topics:[...(v.topics || []), {name:'',keywords:'',learning_outcome:''}]} : v))} className="mt-2 text-brand-600 font-bold">+ Add Topic</button>
                      </label>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {Object.entries(item).map(([field, value]) => (
                        <label key={field} className="font-semibold text-slate-700 capitalize">
                          {field.replaceAll('_',' ')}
                          {typeof value === 'object' ? (
                            <span className="mt-1 block text-slate-500 text-xs">Use the extracted template editor after import</span>
                          ) : (
                            <input value={String(value ?? '')} onChange={(e) => setReviewItems(reviewItems.map((v,i) => i === index ? {...v,[field]:e.target.value} : v))} className="mt-1 w-full border rounded-lg p-2 font-normal" />
                          )}
                        </label>
                      ))}
                    </div>
                  )}
                  {item.text !== undefined && (
                    <div className="grid grid-cols-2 gap-2">
                      <label>Marks
                        <input type="number" min="1" max="25" value={item.marks || 5}
                          onChange={(e) => setReviewItems(reviewItems.map((v, i) => i === index ? { ...v, marks: parseInt(e.target.value) } : v))}
                          className="ml-2 w-20 bg-slate-50 border border-slate-200 rounded p-1" />
                      </label>
                      <label>Sub-question
                        <input value={item.sub_label || ''}
                          onChange={(e) => setReviewItems(reviewItems.map((v, i) => i === index ? { ...v, sub_label: e.target.value } : v))}
                          className="ml-2 w-32 bg-slate-50 border border-slate-200 rounded p-1" />
                      </label>
                    </div>
                  )}
                </div>
              ))}
              {reviewItems.length === 0 && (
                <p className="text-amber-700">No structured items were extracted. The cleaned OCR text is available for review in document history.</p>
              )}
              <button
                type="button"
                onClick={handleApprove}
                disabled={approving || reviewItems.length === 0}
                className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold py-2.5 rounded-xl"
              >
                {approving ? 'Saving and Indexing...' : 'Approve and Save to Database'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Ingested Documents History */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 className="font-bold text-slate-900 text-sm mb-3">Indexed Academic Document Archive</h3>
        {documentsList.length === 0 ? (
          <p className="text-xs text-slate-400">No documents ingested yet.</p>
        ) : (
          <div className="divide-y divide-slate-100 text-xs">
            {documentsList.map((doc) => (
              <div key={doc.id} className="py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="w-4 h-4 text-slate-400" />
                  <div>
                    <span className="font-bold text-slate-800">{doc.filename}</span>
                    <span className="text-[11px] text-slate-400 ml-2 font-mono">({Math.round(doc.file_size / 1024)} KB)</span>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-600 uppercase">
                    {doc.doc_type}
                  </span>
                  <span className="font-mono text-emerald-600 font-bold">
                    {doc.extracted_items_count} chunks indexed
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
