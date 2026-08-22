"use client";
import { useState, useRef, useEffect, useCallback } from "react";

export function useJob(taskName, initialPayload = {}, options = {}) {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const pollTimer = useRef(null);

  const stopPolling = () => {
    if (pollTimer.current) {
      clearInterval(pollTimer.current);
      pollTimer.current = null;
    }
  };

  const poll = useCallback((id) => {
    stopPolling();
    pollTimer.current = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/jobs/${id}`);
        if (!res.ok) return;
        const data = await res.json();
        setStatus(data.status);
        setProgress(data.progress || 0);
        setProgressMessage(data.progress_msg || data.progress_message || "");
        if (data.status === "done" || data.status === "completed") {
          setStatus("done");
          setResult(data.result);
          stopPolling();
        } else if (data.status === "failed" || data.status === "error") {
          setStatus("failed");
          setError(data.error || "Job failed");
          stopPolling();
        } else if (data.status === "cancelled") {
          setStatus("cancelled");
          stopPolling();
        }
      } catch (err) {
        console.warn("Job polling error:", err);
      }
    }, 1000);
  }, []);

  const start = async (payload) => {
    setStatus("running");
    setProgress(0);
    setProgressMessage("Starting task...");
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`http://localhost:8000/api/jobs/${taskName}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || initialPayload)
      });
      if (!res.ok) {
        throw new Error(`Failed to submit job: ${res.statusText}`);
      }
      const data = await res.json();
      setJobId(data.job_id);
      poll(data.job_id);
      return data.job_id;
    } catch (err) {
      setStatus("failed");
      setError(err.message);
    }
  };

  const cancel = async () => {
    if (!jobId) return;
    try {
      await fetch(`http://localhost:8000/api/jobs/${jobId}/cancel`, { method: "POST" });
      setStatus("cancelled");
      stopPolling();
    } catch (err) {
      console.warn("Cancel failed:", err);
    }
  };

  useEffect(() => {
    return () => stopPolling();
  }, []);

  return {
    jobId,
    status,
    progress,
    progressMessage,
    result,
    error,
    start,
    cancel
  };
}
