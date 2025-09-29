
import React, { useState, useRef, useEffect } from "react";
import { Listbox } from "@headlessui/react";
import { Check, ChevronDown } from "lucide-react";
import { Menu, Transition } from "@headlessui/react";
import { Fragment } from "react";
import { motion, AnimatePresence } from "framer-motion";

import { io } from "socket.io-client";

const BASE_URL = "http://localhost:5000";
const socket = io(BASE_URL, {
  withCredentials: true,
  transports: ["websocket"],
});

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
    case "failed":
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
    case "failed":
      return <AlertCircle className="w-4 h-4" />;
    default:
      return <Clock className="w-4 h-4" />;
  }
};

const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

const FuneralAuditDashboard = () => {

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState("");
  const [showAddJob, setShowAddJob] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [confirmAction, setConfirmAction] = useState(null);

  useEffect(() => {
    if (!isLoggedIn) return;

    async function fetchJobs() {
      try {
        setJobsLoading(true);
        const res = await fetch(`${BASE_URL}/user/jobs`, {
          method: "GET",
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          setJobs(data);
        } else {
          console.error("Jobs fetch failed:", res.status);
        }
      } catch (err) {
        console.error("Failed to fetch jobs:", err);
      } finally {
        setJobsLoading(false);
      }
    }

    fetchJobs();
  }, [isLoggedIn]);

  const handleAction = (type, job) => {
    setConfirmAction({ type, job });
  };

  const confirmJobAction = async () => {
    if (!confirmAction) return;

    try {
      if (confirmAction.type === "delete") {
        await fetch(`${BASE_URL}/user/jobs/${confirmAction.job.id}/delete`, {
          method: "DELETE",
          credentials: "include",
        });
        setJobs((prev) => prev.filter((j) => j.id !== confirmAction.job.id));
      } else if (confirmAction.type === "stop") {
        await fetch(`${BASE_URL}/user/jobs/${confirmAction.job.id}/stop`, {
          method: "POST",
          credentials: "include",
        });
        setJobs((prev) =>
          prev.map((j) =>
            j.id === confirmAction.job.id ? { ...j, status: "stopped" } : j
          )
        );
      } else if (confirmAction.type === "logout") {
        await handleLogout();
      }
    } catch (err) {
      console.error("Action failed:", err);
    } finally {
      setConfirmAction(null);
    }
  };

  useEffect(() => {
    if (!isLoggedIn) return; // only connect if logged in
  
    if (!socket.connected) socket.connect();
  
    const handleNewJob = (jobData) => setJobs((prev) => [...prev, jobData]);
    const handleJobUpdate = (updatedJob) =>
      setJobs((prev) =>
        prev.map((job) => (job.id === updatedJob.id ? { ...job, ...updatedJob } : job))
      );
    const handleJobProgress = (update) =>
      setJobs((prev) =>
        prev.map((job) => (job.id === update.id ? { ...job, status: update.status } : job))
      );
    const handleJobFailed = (failedJob) =>
      setJobs((prev) =>
        prev.map((job) =>
          job.id === failedJob.id
            ? { ...job, status: "failed", error: failedJob.error || "Unknown error" }
            : job
        )
      );
  
    socket.on("new_job", handleNewJob);
    socket.on("job_update", handleJobUpdate);
    socket.on("job_progress", handleJobProgress);
    socket.on("job_failed", handleJobFailed);
  
    return () => {
      socket.off("new_job", handleNewJob);
      socket.off("job_update", handleJobUpdate);
      socket.off("job_progress", handleJobProgress);
      socket.off("job_failed", handleJobFailed);
    };
  }, [isLoggedIn]);
  

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${BASE_URL}/me`, {
          method: "GET",
          credentials: "include",
        });

        if (res.ok) {
          const data = await res.json();
          setIsLoggedIn(true);
          console.log("Session restored for:", data.username);
        } else {
          setIsLoggedIn(false);
        }
      } catch (err) {
        console.error("Session check failed:", err);
      } finally {
        setLoading(false);
      }
    };
    checkSession();
  }, []);

  const fileInputRef = useRef(null);

  const branches = ["Phoenix", "Peoria"];

  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const username = formData.get("username");
    const password = formData.get("password");

    const data = new URLSearchParams();
    data.append("username", username);
    data.append("password", password);

    try {
      const response = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        body: data,
        credentials: "include",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      if (response.ok) {
        setIsLoggedIn(true);
      } else {
        const msg = await response.text();
        alert(`Login failed: ${msg}`);
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("Something went wrong, try again.");
    }
  };

  const handleLogout = async () => {
    try {
      const res = await fetch(`${BASE_URL}/logout`, {
        method: "POST",
        credentials: "include",
      });

      if (res.ok) {
        setIsLoggedIn(false);
        console.log("Logged out successfully");
      } else {
        console.error("Logout failed");
      }
    } catch (err) {
      console.error("Error logging out:", err);
    }
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

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center"
      >
        <motion.div
  animate={{ rotate: 360 }}
  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
  className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full"
/>

      </motion.div>
    );
  }

  if (!isLoggedIn) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 w-full max-w-md shadow-2xl"
        >
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4, type: "spring", stiffness: 200 }}
              className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4"
            >
              <FileCheck className="w-8 h-8 text-white" />
            </motion.div>
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="text-2xl font-bold text-white mb-2"
            >
              Document Audit
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="text-white/70"
            >
              Funeral Service Document Management
            </motion.p>
          </div>

          <motion.form
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            onSubmit={handleLogin}
            className="space-y-6"
          >
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.9 }}
            >
              <label className="block text-white/80 text-sm font-medium mb-2">
                Email
              </label>
              <input
                type="text"
                name="username"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                placeholder="admin@funeralservice.com"
                required
              />
            </motion.div>

            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 1.0 }}
            >
              <label className="block text-white/80 text-sm font-medium mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                placeholder="••••••••"
                required
              />
            </motion.div>

            <motion.button
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 1.1 }}
              type="submit"
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02]"
            >
              Sign In
            </motion.button>
          </motion.form>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen bg-gray-50"
    >
      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.5 }}
        className="bg-white border-b border-gray-200 px-6 py-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center"
            >
              <FileCheck className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Best Funeral Services</h1>
              <p className="text-sm text-gray-500">Document Auditing System</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search documents..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
            </div>

            <div className="flex items-center space-x-3">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
              >
                <Settings className="w-5 h-5" />
              </motion.button>
              <motion.div
                whileHover={{ scale: 1.1 }}
                className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center"
              >
                <User className="w-4 h-4 text-white" />
              </motion.div>
              <motion.button
                whileHover={{ scale: 1.1, color: "#ef4444" }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleAction("logout")}
                className="p-2 text-gray-400 hover:text-red-600 transition-colors duration-200"
              >
                <LogOut className="w-5 h-5" />
              </motion.button>
            </div>
          </div>
        </div>
      </motion.header>

      <div className="flex">
        {/* Sidebar */}
        <motion.aside
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="w-64 bg-white border-r border-gray-200 min-h-screen p-6"
        >
          <nav className="space-y-2">
            <motion.button
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowAddJob(true)}
              className="mt-5 w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 flex items-center justify-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Add New Job</span>
            </motion.button>
          </nav>
        </motion.aside>

        {/* Main Content */}
        <motion.main
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="flex-1 p-6"
        >
          <div className="mb-6">
            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center space-x-1.5 px-2.5 py-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50 transition-all duration-200"
              >
                <Filter className="w-3.5 h-3.5" />
                <span>Filter</span>
              </motion.button>
            </div>
          </div>

          {/* Jobs Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jobsLoading ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="col-span-full flex flex-col items-center justify-center py-20 text-gray-500"
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                  <Clock className="w-12 h-12 mb-4 text-gray-400" />
                </motion.div>
                <p className="text-lg font-medium">Loading jobs...</p>
              </motion.div>
            ) : jobs.filter((job) => !selectedBranch || job.branch === selectedBranch).length === 0 ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="col-span-full flex flex-col items-center justify-center py-20 text-gray-500"
              >
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <FileText className="w-12 h-12 mb-4 text-gray-400" />
                </motion.div>
                <p className="text-lg font-medium">No job entries</p>
                <p className="text-sm text-gray-400">Start by adding a new audit job.</p>
              </motion.div>
            ) : (
              <AnimatePresence>
                {jobs
                  .filter((job) => !selectedBranch || job.branch === selectedBranch)
                  .map((job, index) => (
                    <motion.div
                      key={job.id}
                      initial={{ opacity: 0, y: 20, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -20, scale: 0.95 }}
                      transition={{ delay: index * 0.1, duration: 0.3 }}
                      whileHover={{ scale: 1.02, y: -5 }}
                      className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-all duration-300 cursor-pointer"
                      onClick={() => setSelectedJob(job)}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <motion.div
                            transition={{ duration: 0.5 }}
                            className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center"
                          >
                            <FileText className="w-5 h-5 text-white" />
                          </motion.div>
                          <div>
                            <h3 className="font-semibold text-gray-900 text-sm">{job.case_number}</h3>
                            <p className="text-xs text-gray-500">{job.branch}</p>
                          </div>
                        </div>

                        {/* Actions Menu */}
                        <Menu as="div" className="relative inline-block text-left">
                          <div>
                            <Menu.Button
                              onClick={(e) => e.stopPropagation()}
                              className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-all duration-200"
                            >
                              <MoreVertical className="w-4 h-4" />
                            </Menu.Button>
                          </div>

                          <Transition
                            as={Fragment}
                            enter="transition ease-out duration-200"
                            enterFrom="transform opacity-0 scale-95"
                            enterTo="transform opacity-100 scale-100"
                            leave="transition ease-in duration-150"
                            leaveFrom="transform opacity-100 scale-100"
                            leaveTo="transform opacity-0 scale-95"
                          >
                            <Menu.Items className="absolute right-0 mt-2 w-32 origin-top-right rounded-xl bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-20">
                              {job.status === "completed" || job.status === "stopped" || job.status === "failed" || job.status === "canceled" ? (
                                <Menu.Item>
                                  {({ active }) => (
                                    <motion.button
                                      whileHover={{ scale: 1.02 }}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleAction("delete", job);
                                      }}
                                      className={`${
                                        active ? "bg-red-50 text-red-600" : "text-red-500"
                                      } w-full text-left px-4 py-2 text-sm rounded-lg transition-all duration-150`}
                                    >
                                      Delete
                                    </motion.button>
                                  )}
                                </Menu.Item>
                              ) : (
                                <Menu.Item>
                                  {({ active }) => (
                                    <motion.button
                                      whileHover={{ scale: 1.02 }}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleAction("stop", job);
                                      }}
                                      className={`${
                                        active ? "bg-yellow-50 text-yellow-600" : "text-yellow-500"
                                      } w-full text-left px-4 py-2 text-sm rounded-lg transition-all duration-150`}
                                    >
                                      Stop
                                    </motion.button>
                                  )}
                                </Menu.Item>
                              )}
                            </Menu.Items>
                          </Transition>
                        </Menu>
                      </div>

                      <div className="space-y-3 min-h-[180px] flex flex-col justify-between">
                        <div>
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.2 }}
                            className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                              job.status
                            )}`}
                          >
                            {getStatusIcon(job.status)}
                            <span className="capitalize">{job.status}</span>
                          </motion.div>

                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.3 }}
                            className="grid grid-cols-2 gap-4 text-sm mt-3"
                          >
                            <div>
                              <p className="text-gray-500">Files</p>
                              <p className="font-semibold text-gray-900">
                                {Array.isArray(job.files) ? job.files.length : 0}
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-500">Type</p>
                              <p className="font-semibold text-gray-900 capitalize">{job.feature}</p>
                            </div>
                          </motion.div>

                          {job.status === "completed" && (
                            <motion.div
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: 0.4 }}
                              className="grid grid-cols-2 gap-4 text-sm mt-3"
                            >
                              <div>
                                <p className="text-gray-500">Accuracy</p>
                                <p
                                  className={`font-semibold ${
                                    parseInt(job.accuracy) >= 80
                                      ? "text-green-600"
                                      : parseInt(job.accuracy) >= 50
                                      ? "text-yellow-500"
                                      : "text-red-600"
                                  }`}
                                >
                                  {job.accuracy}
                                </p>
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
                            </motion.div>
                          )}

                          {job.status === "failed" && (
                            <motion.div
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.4 }}
                              className="mt-3 text-sm text-red-600"
                            >
                              <p className="font-semibold">Audit Failed</p>
                              <p>{job.error || "An unexpected error occurred during audit."}</p>
                            </motion.div>
                          )}
                        </div>

                        {job.status === "processing" && (
                          <motion.div
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: 1 }}
                            transition={{ delay: 0.5, duration: 0.8 }}
                            className="w-full bg-gray-200 rounded-full h-2 overflow-hidden mt-3"
                          >
                            <motion.div
                              animate={{
                                x: ["-100%", "400%"],
                              }}
                              transition={{
                                duration: 1,
                                repeat: Infinity,
                                ease: "easeInOut",
                              }}
                              className="h-2 w-1/3 rounded-full bg-gradient-to-r from-blue-600 via-blue-400 to-blue-500"
                            />
                          </motion.div>
                        )}

                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.6 }}
                          className="pt-2 border-t border-gray-100 mt-auto"
                        >
                          <p className="text-xs text-gray-500">
                            Created:{" "}
                            {new Date(job.created_at).toLocaleString(undefined, {
                              month: "2-digit",
                              day: "2-digit",
                              year: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                              hour12: true,
                              timeZone: userTimeZone,
                            })}
                          </p>
                          {job.completed_at && (
                            <p className="text-xs text-gray-500">
                              Completed:{" "}
                              {new Date(job.completed_at).toLocaleString(undefined, {
                                month: "2-digit",
                                day: "2-digit",
                                year: "numeric",
                                hour: "2-digit",
                                minute: "2-digit",
                                hour12: true,
                                timeZone: userTimeZone,
                              })}
                            </p>
                          )}
                        </motion.div>
                      </div>
                    </motion.div>
                  ))}
              </AnimatePresence>
            )}
          </div>
        </motion.main>
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
    {confirmAction && (
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
    <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-lg">
      <h3 className="text-lg font-bold text-gray-900 mb-3">
        {confirmAction.type === "delete"
          ? "Confirm Deletion"
          : confirmAction.type === "stop"
          ? "Confirm Stop"
          : "Confirm Logout"}
      </h3>
      <p className="text-sm text-gray-600 mb-6">
        {confirmAction.type === "delete"
          ? "Are you sure you want to delete this completed job?"
          : confirmAction.type === "stop"
          ? "Are you sure you want to stop this running job?"
          : "Are you sure you want to sign out of your account?"}
      </p>
      <div className="flex justify-end space-x-3">
        <button
          onClick={() => setConfirmAction(null)}
          className="px-4 py-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={confirmJobAction}
          className={`px-4 py-2 rounded-lg text-white ${
            confirmAction.type === "delete"
              ? "bg-red-600 hover:bg-red-700"
              : confirmAction.type === "stop"
              ? "bg-yellow-500 hover:bg-yellow-600"
              : "bg-red-600 hover:bg-red-700"
          }`}
        >
          Confirm
        </button>
      </div>
    </div>
  </div>
)}

    </motion.div>
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
              General
            </span>
            <span className="text-sm text-gray-500">
              Standard checks for one document
            </span>
          </label>

          {/* Comparison Audit */}
          <label
            className={`cursor-pointer flex flex-col items-center justify-center rounded-2xl border p-6 transition-all duration-200 shadow-sm
          ${
            formData.feature === "cross-check"
              ? "border-purple-600 bg-purple-50 ring-2 ring-purple-500"
              : "border-gray-200 hover:border-purple-400 hover:bg-gray-50"
          }`}
          >
            <input
              type="radio"
              value="cross-check"
              checked={formData.feature === "cross-check"}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, feature: e.target.value }))
              }
              className="hidden"
            />
            <span className="text-lg font-semibold text-gray-900">
                Cross-check
            </span>
            <span className="text-sm text-gray-500">
              Compare 2 files side by side
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
          placeholder="Additional notes (Optional)"
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
            if (formData.feature == "cross-check" && formData.files.length != 2) return alert("Two files only are accepted in Cross-check Feature.");
            if (formData.files.length === 0) return alert("Please upload at least one file.");
            if (formData.case_number.trim() == "")
              return alert("Case number is required.");
            if (formData.feature.trim() == "")
              return alert("Case number is required.");

            const data = new FormData();
            data.append("case_number", formData.case_number);
            data.append("feature", formData.feature);
            data.append("branch", formData.branch);
            data.append("description", formData.description);
            
            formData.files.forEach((file) => data.append("files", file));
            setShowAddJob(false);
            
            try {
              const response = await fetch(
                `${BASE_URL}/user/add_job`,
                {
                  method: "POST",
                  credentials: 'include',
                  body: data,
                }
              );
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
            
          </div>
        </div>
      </div>

      {job.status === "completed" && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <div className="bg-white border border-gray-200 rounded-xl p-7 text-center">
              <div className="text-2xl font-bold text-gray-900">
              {Array.isArray(job.files) ? job.files.length : 0}
                
              </div>
              <div className="text-sm text-gray-500">Total Documents</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-7 text-center">
              <div className={`text-2xl font-semibold ${
                        parseInt(job.accuracy) >= 80
                          ? "text-green-600"
                          : parseInt(job.accuracy) >= 50
                          ? "text-yellow-500"
                          : "text-red-600"
                      }`}>
                {job.accuracy}
              </div>
              <div className="text-sm text-gray-500">Accuracy</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-7 text-center">
              <div className="text-2xl font-bold text-red-600">
                {job.issues.length}
              </div>
              <div className="text-sm text-gray-500">Issues Found</div>
            </div>
          </div>

          {/* Issues List */}
          {job.issues?.length > 0 && (
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-gray-900">
                Issues Detected
              </h4>
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <ul className="text-sm text-yellow-700 space-y-2">
                  {job.issues.map((issue, i) => (
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

        {job.status === "failed" && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <h4 className="text-lg font-semibold text-red-700">Audit Failed</h4>
            <p className="text-sm text-red-600 mt-2">
              {job.error || "No error message provided."}
            </p>
          </div>
        )}

      

      {/* Job Metadata */}
      <div className="bg-gray-50 rounded-xl p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Job Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Created:</span>
            <span className="ml-2 font-medium text-gray-900">
              
            {new Date(job.created_at).toLocaleString(undefined, {
              month: "2-digit",
              day: "2-digit",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
              hour12: true,
              timeZone: userTimeZone,
            })}
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
              {new Date(job.completed_at).toLocaleString(undefined, {
              month: "2-digit",
              day: "2-digit",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
              hour12: true,
              timeZone: userTimeZone,
            })}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FuneralAuditDashboard;
