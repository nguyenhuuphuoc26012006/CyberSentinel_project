
import { useEffect, useState } from "react";
import type { Alert, SecurityEvent } from "./types";

const API =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:5000/api";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API}${path}`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString("vi-VN");
}

function Metric({
  label,
  value,
  note,
  icon,
}: {
  label: string;
  value: string;
  note: string;
  icon: string;
}) {
  return (
    <article className="metric">
      <div className="metric-top">
        <span>{label}</span>
        <b>{icon}</b>
      </div>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function Severity({ value }: { value: string }) {
  return (
    <span className={`severity ${value.toLowerCase()}`}>
      {value.toUpperCase()}
    </span>
  );
}

export default function App() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [apiStatus, setApiStatus] = useState("Đang kết nối");
  const [error, setError] = useState("");

  async function refresh() {
    try {
      const [eventData, alertData, health] = await Promise.all([
        fetchJson<{ items: SecurityEvent[] }>("/events?limit=50"),
        fetchJson<{ items: Alert[] }>("/alerts?limit=50"),
        fetchJson<{ status: string }>("/health"),
      ]);

      setEvents(eventData.items);
      setAlerts(alertData.items);

      setApiStatus(
        health.status === "ok"
          ? "Hoạt động"
          : "Có lỗi dịch vụ"
      );

      setError("");
    } catch {
      setApiStatus("Mất kết nối");
      setError(
        "Không thể kết nối Backend. Hãy kiểm tra Docker và API."
      );
    }
  }

  useEffect(() => {
    void refresh();

    const timer = window.setInterval(() => {
      void refresh();
    }, 5000);

    return () => window.clearInterval(timer);
  }, []);

  const criticalCount = alerts.filter(
    (alert) => alert.severity === "critical"
  ).length;

  const highCount = alerts.filter(
    (alert) => alert.severity === "high"
  ).length;

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">C</span>
          <div>
            <b>CyberSentinel</b>
            <small>SECURITY OPERATIONS</small>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <a className="nav active">▦ Overview</a>
        <a className="nav">◷ Event Logs</a>
        <a className="nav">⚑ Alerts</a>
        <a className="nav">⌘ Detection Rules</a>
        <a className="nav">◎ Incidents</a>
        <a className="nav">⇧ Log Sources</a>

        <div className="sidebar-bottom">
          <span className="pulse" />
          SIEM ENGINE
          <b>DEV</b>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <span className="eyebrow">
              SECURITY / OVERVIEW
            </span>

            <h1>Security Overview</h1>

            <p>
              Giám sát và phân tích sự kiện an ninh tập trung.
            </p>
          </div>

          <div className="status">
            <i className="pulse" />
            API: {apiStatus}

            <button onClick={() => void refresh()}>
              ↻ Refresh
            </button>
          </div>
        </header>

        {error && <div className="error">{error}</div>}

        <section className="metrics">
          <Metric
            label="TOTAL EVENTS"
            value={events.length.toString()}
            note="50 sự kiện gần nhất"
            icon="▤"
          />

          <Metric
            label="OPEN ALERTS"
            value={alerts.length.toString()}
            note="Cảnh báo chưa xử lý"
            icon="⚑"
          />

          <Metric
            label="HIGH SEVERITY"
            value={highCount.toString()}
            note="Mức độ High"
            icon="⚠"
          />

          <Metric
            label="CRITICAL ALERTS"
            value={criticalCount.toString()}
            note="Mức độ Critical"
            icon="✹"
          />
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Recent Security Events</h2>
              <p>
                Sự kiện mới nhất từ Log Collector
              </p>
            </div>

            <span className="live">
              <i className="pulse" />
              LIVE · 5S
            </span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>TIME</th>
                  <th>EVENT</th>
                  <th>SOURCE IP</th>
                  <th>USER</th>
                  <th>SEVERITY</th>
                  <th>SOURCE</th>
                </tr>
              </thead>

              <tbody>
                {events.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="empty">
                      Chưa có sự kiện. Hãy gửi log thử nghiệm vào API.
                    </td>
                  </tr>
                ) : (
                  events.map((event) => (
                    <tr key={event.id}>
                      <td>{formatDate(event.created_at)}</td>
                      <td className="event-name">
                        {event.event_type}
                      </td>
                      <td>{event.source_ip ?? "—"}</td>
                      <td>{event.username ?? "—"}</td>
                      <td>
                        <Severity value={event.severity} />
                      </td>
                      <td>{event.source}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Detection Alerts</h2>
              <p>
                Cảnh báo được tạo bởi Detection Engine
              </p>
            </div>

            <span className="count">
              {alerts.length} ALERTS
            </span>
          </div>

          {alerts.length === 0 ? (
            <div className="empty block-empty">
              Chưa phát hiện cảnh báo nào.
            </div>
          ) : (
            <div className="alert-list">
              {alerts.map((alert) => (
                <article
                  className="alert-row"
                  key={alert.id}
                >
                  <div className="alert-icon">⚠</div>

                  <div className="alert-info">
                    <b>{alert.title}</b>

                    <p>{alert.description}</p>

                    <small>
                      {alert.rule_id} ·{" "}
                      {formatDate(alert.created_at)}
                    </small>
                  </div>

                  <Severity value={alert.severity} />
                </article>
              ))}
            </div>
          )}
        </section>

        <footer>
          CyberSentinel · Independent SIEM Lab · Educational prototype
        </footer>
      </section>
    </main>
  );
}
