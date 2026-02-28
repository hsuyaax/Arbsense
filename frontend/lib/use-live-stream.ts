"use client";

import { useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type LiveStats = {
  markets_scanned: number;
  opportunities: number;
  avg_spread: number;
  timestamp: number;
};

export function useLiveStream() {
  const [live, setLive] = useState<LiveStats | null>(null);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const es = new EventSource(`${API_URL}/stream`);
    esRef.current = es;

    es.onopen = () => setConnected(true);

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (!data.error) {
          setLive(data as LiveStats);
        }
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      setConnected(false);
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, []);

  const triggerRefresh = async () => {
    try {
      await fetch(`${API_URL}/refresh`, { method: "POST" });
    } catch {
      // ignore
    }
  };

  return { live, connected, triggerRefresh };
}
