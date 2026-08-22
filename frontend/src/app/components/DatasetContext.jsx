"use client";
import { createContext, useContext, useEffect, useState } from "react";

const Ctx = createContext({ id: null, setId: () => {}, list: [], refresh: () => {} });

export function DatasetProvider({ children }) {
  const [id, setIdState] = useState(null);
  const [list, setList] = useState([]);

  const refresh = async () => {
    try {
      const r = await fetch("http://localhost:8000/api/datasets");
      const d = await r.json();
      const datasets = d.datasets || [];
      setList(datasets);
      const savedId = localStorage.getItem("dataset_id");
      const validIds = datasets.map((x) => x.id);
      if (savedId && validIds.includes(savedId)) {
        setIdState(savedId);
      } else if (datasets.length > 0) {
        setIdState(datasets[0].id);
        localStorage.setItem("dataset_id", datasets[0].id);
      } else {
        setIdState(null);
        localStorage.removeItem("dataset_id");
      }
    } catch (e) {
      console.warn("Failed to fetch datasets list:", e);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const setId = (v) => {
    if (v) {
      localStorage.setItem("dataset_id", v);
    } else {
      localStorage.removeItem("dataset_id");
    }
    setIdState(v);
  };

  return <Ctx.Provider value={{ id, setId, list, refresh }}>{children}</Ctx.Provider>;
}

export const useDataset = () => useContext(Ctx);
