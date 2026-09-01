function AuditTrail({ entries }) {
  if (!entries || entries.length === 0) return null

  return (
    <section className="panel">
      <span className="panel-label">Audit trail</span>
      <ol className="timeline">
        {entries.map((entry) => (
          <li key={entry.step} className="timeline-item">
            <div className="timeline-marker">
              <span className="timeline-step">{entry.step}</span>
            </div>
            <div className="timeline-content">
              <div className="timeline-top">
                <span className="timeline-action">{entry.action}</span>
                <span className="timeline-time">{entry.timestamp}</span>
              </div>
              <div className="timeline-detail">{entry.detail}</div>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}

export default AuditTrail
