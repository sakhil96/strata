interface StatusBarProps {
  freshness?: Record<string, string>;
  lastDbtRun?: string;
  evalScore?: number;
  serviceHealth?: string;
}

export function StatusBar({
  freshness,
  lastDbtRun,
  evalScore,
  serviceHealth,
}: StatusBarProps) {
  return (
    <footer className="border-t border-hairline mt-8 py-2 flex gap-6 text-micro uppercase text-ash tracking-widest">
      {freshness &&
        Object.entries(freshness).map(([source, ts]) => (
          <span key={source}>
            {source}: {ts}
          </span>
        ))}
      {lastDbtRun && <span>dbt: {lastDbtRun}</span>}
      {evalScore != null && (
        <span className={evalScore >= 0.9 ? "text-good" : "text-critical"}>
          eval: {(evalScore * 100).toFixed(0)}%
        </span>
      )}
      {serviceHealth && (
        <span
          className={serviceHealth === "ready" ? "text-good" : "text-critical"}
        >
          service: {serviceHealth}
        </span>
      )}
    </footer>
  );
}
