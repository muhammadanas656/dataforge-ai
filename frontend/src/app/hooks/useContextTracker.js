"use client";
import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { useDataset } from "../components/DatasetContext";

export function useContextTracker(sessionId = "default") {
  const pathname = usePathname();
  const { id: datasetId } = useDataset();

  useEffect(() => {
    const extractModule = (path) => {
      if (!path || path === "/") return "overview";
      const clean = path.replace(/^\//, "");
      const parts = clean.split("/");
      return parts[0] || "overview";
    };

    const activeModule = extractModule(pathname);

    // Post context update to backend
    fetch("http://localhost:8000/api/context/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        active_page: pathname,
        active_module: activeModule,
        active_dataset_id: datasetId || null,
        action: `navigate_${activeModule}`
      })
    }).catch(() => {});
  }, [pathname, datasetId, sessionId]);
}
