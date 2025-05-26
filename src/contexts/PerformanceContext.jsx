import React, { createContext, useState, useContext, useEffect } from 'react';

const PerformanceContext = createContext({
  metrics: {
    responseTime: 0,
    memoryUsage: 0,
    cpuUsage: 0,
  },
  addPerformanceEntry: () => {},
});

export function PerformanceProvider({ children }) {
  const [metrics, setMetrics] = useState({
    responseTime: 0,
    memoryUsage: 0,
    cpuUsage: 0,
  });

  const addPerformanceEntry = (entry) => {
    setMetrics(prevMetrics => ({
      ...prevMetrics,
      ...entry,
    }));
  };

  // Simulate performance monitoring
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate memory usage between 30-70%
      const memoryUsage = 30 + Math.random() * 40;
      
      // Simulate CPU usage between 10-50%
      const cpuUsage = 10 + Math.random() * 40;
      
      addPerformanceEntry({
        memoryUsage,
        cpuUsage,
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <PerformanceContext.Provider value={{ metrics, addPerformanceEntry }}>
      {children}
    </PerformanceContext.Provider>
  );
}

export function usePerformance() {
  return useContext(PerformanceContext);
}