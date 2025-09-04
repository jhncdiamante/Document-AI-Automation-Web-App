import React, { useState, useRef, useEffect } from "react";
import { Listbox, Transition } from "@headlessui/react";
import { Check, ChevronDown } from "lucide-react";
import { Fragment } from "react";

import { io } from "socket.io-client";

const socket = io("http://localhost:5000");
import {
  FileText,
  Upload,
  Clock,
  CheckCircle,
  AlertCircle,
  User,
  Settings,
  LogOut,
  Search,
  Filter,
  MoreVertical,
  Eye,
  Download,
  FileCheck,
  Building2,
  Plus,
  X,
} from "lucide-react";

const getStatusColor = (status) => {
  switch (status) {
    case "completed":
      return "text-green-600 bg-green-100";
    case "processing":
      return "text-blue-600 bg-blue-100";
    case "queued":
      return "text-yellow-600 bg-yellow-100";
    case "error":
      return "text-red-600 bg-red-100";
    default:
      return "text-gray-600 bg-gray-100";
  }
};

const getStatusIcon = (status) => {
  switch (status) {
    case "completed":
      return <CheckCircle className="w-4 h-4" />;
    case "processing":
      return <Clock className="w-4 h-4" />;
    case "queued":
      return <Clock className="w-4 h-4" />;
    case "error":
      return <AlertCircle className="w-4 h-4" />;
    default:
      return <Clock className="w-4 h-4" />;
  }
};


const FuneralAuditDashboard = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState("");
  const [showAddJob, setShowAddJob] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobs, setJobs] = useState([
    
  ]);

  useEffect(() => {
    // Listen for backend job updates
    socket.on("new_job", (jobData) => {
      console.log("New job received:", jobData);
      setJobs((prevJobs) => [...prevJobs, jobData]); // append new job
    });

    socket.on("job_update", (updatedJob) => {
      console.log("Job updated:", updatedJob);
      setJobs((prevJobs) =>
        prevJobs.map((job) =>
          job.id === updatedJob.id ? { ...job, ...updatedJob } : job
        )
      );
    });

    socket.on("job_progress", (update) => {
      console.log("Job progress update:", update);
      setJobs((prevJobs) =>
        prevJobs.map((job) =>
          job.id === update.id ? { ...job, status: update.status } : job
        )
      );
    });

    return () => {
      socket.off("new_job");
      socket.off("job_update");
      socket.off("job_progress");
    };
  }, []);
  const fileInputRef = useRef(null);

  const branches = [
    "Downtown Branch",
    "North Branch",
    "South Branch",
    "East Branch",
  ];

  const handleLogin = (e) => {
    if (e) e.preventDefault();
    setIsLoggedIn(true);
  };

  const handleAddJob = (jobData) => {
    const newJob = {
      id: jobs.length + 1,
      ...jobData,
      status: "queued",
    };
    setJobs([...jobs, newJob]);
    setShowAddJob(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 w-full max-w-md shadow-2xl">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FileCheck className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">
              Document Audit
            </h1>
            <p className="text-white/70">Funeral Service Document Management</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-white/80 text-sm font-medium mb-2">
                Email
              </label>
              <input
                type="email"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="admin@funeralservice.com"
                required
              />
            </div>

            <div>
              <label className="block text-white/80 text-sm font-medium mb-2">
                Password
              </label>
              <input
                type="password"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              onClick={handleLogin}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02]"
            >
              Sign In
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <FileCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Best Funeral Services
              </h1>
              <p className="text-sm text-gray-500">Document Auditing System</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search documents..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="flex items-center space-x-3">
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <Settings className="w-5 h-5" />
              </button>
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <button
                onClick={() => setIsLoggedIn(false)}
                className="p-2 text-gray-400 hover:text-red-600 transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 min-h-screen p-6">
          <nav className="space-y-2">
            

            <button
              onClick={() => setShowAddJob(true)}
              className="mt-5 w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02] flex items-center justify-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Add New Job</span>
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Document Auditing Jobs
            </h2>
            <div className="flex items-center space-x-2">
              <button className="flex items-center space-x-1.5 px-2.5 py-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
                <Filter className="w-3.5 h-3.5" />
                <span>Filter</span>
              </button>
            </div>

          </div>

         {/* Jobs Grid */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {jobs.filter((job) => !selectedBranch || job.branch === selectedBranch).length === 0 ? (
    <div className="col-span-full flex flex-col items-center justify-center py-20 text-gray-500">
      <FileText className="w-12 h-12 mb-4 text-gray-400" />
      <p className="text-lg font-medium">No job entries</p>
      <p className="text-sm text-gray-400">Start by adding a new audit job.</p>
    </div>
  ) : (
    jobs
      .filter((job) => !selectedBranch || job.branch === selectedBranch)
      .map((job) => (
        <div
          key={job.id}
          className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-all duration-200 cursor-pointer transform hover:scale-[1.02]"
          onClick={() => setSelectedJob(job)}
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 text-sm">{job.case_number}</h3>
                <p className="text-xs text-gray-500">{job.branch}</p>
              </div>
            </div>
            <button className="p-1 text-gray-400 hover:text-gray-600">
              <MoreVertical className="w-4 h-4" />
            </button>
          </div>

          {/* 🔹 enforce equal height */}
          <div className="space-y-3 min-h-[180px] flex flex-col justify-between">
            <div>
              <div
                className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}
              >
                {getStatusIcon(job.status)}
                <span className="capitalize">{job.status}</span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm mt-3">
                <div>
                  <p className="text-gray-500">Files</p>
                  <p className="font-semibold text-gray-900">
                    {Array.isArray(job.files) ? job.files.length : 0}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Type</p>
                  <p className="font-semibold text-gray-900 capitalize">
                    {job.feature}
                  </p>
                </div>
              </div>

              {job.status === "completed" && (
                <div className="grid grid-cols-2 gap-4 text-sm mt-3">
                  <div>
                    <p className="text-gray-500">Accuracy</p>
                    <p className="font-semibold text-green-600">{job.accuracy}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Issues</p>
                    <p
                      className={`font-semibold ${
                        Array.isArray(job.issues) && job.issues.length === 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {Array.isArray(job.issues) ? job.issues.length : 0}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* 🔹 Stick to bottom */}
            {job.status === "processing" && (
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden mt-3">
                <div
                  className="h-2 w-full rounded-full
                    bg-gradient-to-r from-blue-600 via-blue-400 to-blue-500
                    bg-[length:200%_100%] animate-shimmer"
                ></div>
              </div>
            )}
            <div className="pt-2 border-t border-gray-100 mt-auto">
              <p className="text-xs text-gray-500">Created: {job.created_at}</p>
              {job.completed_at && (
                <p className="text-xs text-gray-500">Completed: {job.completed_at}</p>
              )}
            </div>
          </div>
        </div>
      ))
  )}
</div>

        </main>
      </div>

      {/* Add Job Modal */}
      {showAddJob && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">
                Add New Audit Job
              </h3>
              <button
                onClick={() => setShowAddJob(false)}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <AddJobForm
              onSubmit={handleAddJob}
              branches={branches}
              setShowAddJob={setShowAddJob}
            />
          </div>
        </div>
      )}

      {/* Job Details Panel */}
      {selectedJob && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  {selectedJob.case_number}
                </h3>
                <p className="text-gray-500">{selectedJob.branch}</p>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <JobDetails job={selectedJob} />
          </div>
        </div>
      )}
    </div>
  );
};

const AddJobForm = ({ onSubmit, branches, setShowAddJob }) => {
  const [formData, setFormData] = useState({
    case_number: "",
    feature: "general",
    branch: "",
    description: "",
    created_at: "",
    files: [],
  });
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    setFormData((prev) => ({ ...prev, files: [...prev.files, ...files] }));
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setFormData((prev) => ({ ...prev, files: [...prev.files, ...files] }));
  };

  const removeFile = (index) => {
    setFormData((prev) => ({
      ...prev,
      files: prev.files.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...formData, files: formData.files.length });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Audit Type */}
      <div>
        <h3 className="text-sm font-semibold text-gray-800 mb-4 uppercase tracking-wide">
          Audit Type
        </h3>
        <div className="grid grid-cols-2 gap-4">
          {/* General Audit */}
          <label
            className={`cursor-pointer flex flex-col items-center justify-center rounded-2xl border p-6 transition-all duration-200 shadow-sm
          ${
            formData.feature === "general"
              ? "border-blue-600 bg-blue-50 ring-2 ring-blue-500"
              : "border-gray-200 hover:border-blue-400 hover:bg-gray-50"
          }`}
          >
            <input
              type="radio"
              value="general"
              checked={formData.feature === "general"}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, feature: e.target.value }))
              }
              className="hidden"
            />
            <span className="text-lg font-semibold text-gray-900">
              General Audit
            </span>
            <span className="text-sm text-gray-500">
              Standard checks for one document
            </span>
          </label>

          {/* Comparison Audit */}
          <label
            className={`cursor-pointer flex flex-col items-center justify-center rounded-2xl border p-6 transition-all duration-200 shadow-sm
          ${
            formData.feature === "comparison"
              ? "border-purple-600 bg-purple-50 ring-2 ring-purple-500"
              : "border-gray-200 hover:border-purple-400 hover:bg-gray-50"
          }`}
          >
            <input
              type="radio"
              value="comparison"
              checked={formData.feature === "comparison"}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, feature: e.target.value }))
              }
              className="hidden"
            />
            <span className="text-lg font-semibold text-gray-900">
              Document Comparison
            </span>
            <span className="text-sm text-gray-500">
              Cross-check 2 files side by side
            </span>
          </label>
        </div>
      </div>

      {/* Case Number and Branch*/}

      {/* Case & Branch */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Case Number */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">
            Case Number
          </label>
          <input
            type="text"
            value={formData.case_number}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, case_number: e.target.value }))
            }
            className="w-full px-4 py-3 border border-gray-300 rounded-xl 
                 focus:outline-none focus:ring-2 focus:ring-blue-500 
                 focus:border-transparent shadow-sm"
            required
          />
        </div>

        {/* Branch (Listbox) */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">
            Branch
          </label>
          <Listbox
            value={formData.branch}
            onChange={(val) =>
              setFormData((prev) => ({ ...prev, branch: val }))
            }
          >
            <div className="relative">
              {/* Button */}
              <Listbox.Button
                className="relative w-full cursor-pointer rounded-xl border border-gray-300 bg-white 
                     py-3 pl-4 pr-10 text-left shadow-sm focus:outline-none 
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
              >
                <span className="block truncate text-gray-900">
                  {formData.branch || "Select Branch"}
                </span>
                <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                </span>
              </Listbox.Button>

              {/* Options */}
              <Transition
                as={Fragment}
                leave="transition ease-in duration-100"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
              >
                <Listbox.Options
                  className="absolute mt-2 w-full max-h-60 overflow-auto rounded-xl 
                       bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
                >
                  {branches.map((branch) => (
                    <Listbox.Option
                      key={branch}
                      value={branch}
                      className={({ active }) =>
                        `relative cursor-pointer select-none py-3 pl-10 pr-4 rounded-lg mx-1
                  ${active ? "bg-blue-50 text-blue-600" : "text-gray-900"}`
                      }
                    >
                      {({ selected }) => (
                        <>
                          <span
                            className={`block truncate ${
                              selected ? "font-semibold" : "font-normal"
                            }`}
                          >
                            {branch}
                          </span>
                          {selected ? (
                            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600">
                              <Check className="h-5 w-5" />
                            </span>
                          ) : null}
                        </>
                      )}
                    </Listbox.Option>
                  ))}
                </Listbox.Options>
              </Transition>
            </div>
          </Listbox>
        </div>
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-2">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, description: e.target.value }))
          }
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
          rows="3"
          placeholder="Additional details about the audit job..."
        />
      </div>

      {/* File Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-2">
          Documents
        </label>
        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
            dragActive
              ? "border-blue-500 bg-blue-50 animate-pulse"
              : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">
            Drag and drop files here, or click to browse
          </p>
          <p className="text-sm text-gray-500">Supports *.PDF only</p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {formData.files.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-sm font-medium text-gray-700">Selected Files:</p>
            {formData.files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg shadow-sm"
              >
                <span className="text-sm text-gray-700">{file.name}</span>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex space-x-4 pt-4">
        <button
          type="button" // change from "submit" to "button" to prevent default form submission
          onClick={async () => {
            //if (formData.feature == "comparison" && formData.files.length != 2) return alert("Two files only are accepted in Comparison Feature.");
            //if (formData.files.length === 0) return alert("Please upload at least one file.");
            if (formData.case_number.trim() == "")
              return alert("Case number is required.");
            if (
              !(
                formData.feature == "comparison" ||
                formData.feature == "general"
              )
            )
              return alert("Feature is required.");

            const data = new FormData();
            data.append("case_number", formData.case_number);
            data.append("feature", formData.feature);
            data.append("branch", formData.branch);
            data.append("description", formData.description);
            data.append(
              "created_at",
              new Date()
                .toLocaleString("en-CA", {
                  year: "numeric",
                  month: "2-digit",
                  day: "2-digit",
                  hour: "2-digit",
                  minute: "2-digit",
                  hour12: true,
                })
                .replace(",", "")
                .replace(/\./g, "")   // remove dots in a.m. / p.m.
                .toUpperCase()
            );
            formData.files.forEach((file) => data.append("files", file));

            try {
              const response = await fetch(
                "http://localhost:5000/start_audit",
                {
                  method: "POST",
                  body: data,
                }
              );

              const result = await response.json();
              setShowAddJob(false);
            } catch (err) {
              console.error("Failed to start audit job:", err);
            }
          }}
          className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
        >
          Start Audit Job
        </button>

        <button
          type="button"
          onClick={() => setShowAddJob(false)}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
          
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

const JobDetails = ({ job }) => {
  const results = job.results || {
    summary: {
      totalDocuments: job.files?.length || 0,
      processedDocuments: job.files?.length || 0,
      accuracy: job.accuracy || 0,
      issues: [],
    },
    documents: [],
  };

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${getStatusColor(job.status)}`}>
              {getStatusIcon(job.status)}
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Job Status</h4>
              <p className="text-sm text-gray-600 capitalize">{job.status}</p>
            </div>
          </div>

          <div className="flex space-x-2">
            <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Eye className="w-4 h-4" />
              <span>View Raw</span>
            </button>
          </div>
        </div>
      </div>

      {job.status === "completed" && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-gray-900">
                {results.summary.totalDocuments}
              </div>
              <div className="text-sm text-gray-500">Total Documents</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {results.summary.accuracy}
              </div>
              <div className="text-sm text-gray-500">Accuracy</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-red-600">
                {results.summary.issues.length}
              </div>
              <div className="text-sm text-gray-500">Issues Found</div>
            </div>
          </div>

          {/* Issues List */}
          {results.issues?.length > 0 && (
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-gray-900">
                Issues Detected
              </h4>
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <ul className="text-sm text-yellow-700 space-y-2">
                  {results.issues.map((issue, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <span className="text-yellow-600">•</span>
                      <span>{issue}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </>
      )}

      {job.status === "processing" && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center animate-pulse">
              <Clock className="w-4 h-4 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">
                Processing Documents
              </h4>
              <p className="text-sm text-blue-700">
                OCR and AI analysis in progress...
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-blue-700">Progress</span>
              <span className="text-blue-900 font-medium">{job.progress}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${job.progress}%` }}
              ></div>
            </div>

            <div className="text-sm text-blue-700">
              <p>• OCR text extraction: Complete</p>
              <p>
                • AI document validation:{" "}
                {job.progress > 50 ? "In progress" : "Queued"}
              </p>
              <p>
                • Data verification:{" "}
                {job.progress > 80 ? "In progress" : "Queued"}
              </p>
              <p>
                • Report generation:{" "}
                {job.progress > 95 ? "In progress" : "Queued"}
              </p>
            </div>
          </div>
        </div>
      )}

      {job.status === "queued" && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
              <Clock className="w-4 h-4 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-yellow-900">Job Queued</h4>
              <p className="text-sm text-yellow-700">
                Waiting for processing resources...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Job Metadata */}
      <div className="bg-gray-50 rounded-xl p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Job Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Created:</span>
            <span className="ml-2 font-medium text-gray-900">
              {job.created_at}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Feature:</span>
            <span className="ml-2 font-medium text-gray-900 capitalize">
              {job.feature}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Branch:</span>
            <span className="ml-2 font-medium text-gray-900">{job.branch}</span>
          </div>
          <div>
            <span className="text-gray-500">Files:</span>
            <span className="ml-2 font-medium text-gray-900">
              {Array.isArray(job.files) ? job.files.length : 0}
            </span>
          </div>

          <div>
            <span className="text-gray-500">Description:</span>
            <span className="ml-2 font-medium text-gray-900">
              {job.description}
            </span>
          </div>
          {job.completed_at && (
            <div>
              <span className="text-gray-500">Completed:</span>
              <span className="ml-2 font-medium text-gray-900">
                {job.completed_at}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FuneralAuditDashboard;
