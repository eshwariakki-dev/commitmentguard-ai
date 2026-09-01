import { useState } from "react";
import "./App.css";
import RequirementsCard from "./components/RequirementsCard";
import VerificationCard from "./components/VerificationCard";
import AlternativeCard from "./components/AlternativeCard";
import AuditTrail from "./components/AuditTrail";

const API_BASE = "https://commitmentguard-ai.onrender.com";

const EXAMPLE_REQUEST =
  "I need wireless headphones under ₹3000 delivered tomorrow";

function App() {
  const [requestText, setRequestText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function handleVerify() {
    const text = requestText.trim() || EXAMPLE_REQUEST;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_BASE}/api/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request: text }),
      });
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(
        err.message.includes("fetch")
          ? "Cannot reach the backend. Make sure the Flask server is running on port 5000."
          : err.message,
      );
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleVerify();
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <div className="logo-mark">CG</div>
          <div>
            <h1>CommitmentGuard AI</h1>
            <p className="subtitle">
              Verified commitments for agentic commerce
            </p>
          </div>
        </div>
        <div className="status-pill">
          <span className="status-dot" />
          System active
        </div>
      </header>

      <main className="main">
        <section className="panel request-panel">
          <label className="panel-label" htmlFor="request-input">
            Buyer request
          </label>
          <textarea
            id="request-input"
            className="request-input"
            placeholder={EXAMPLE_REQUEST}
            value={requestText}
            onChange={(e) => setRequestText(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
          />
          <div className="request-footer">
            <span className="example-hint">Example: "{EXAMPLE_REQUEST}"</span>
            <button
              className="verify-btn"
              onClick={handleVerify}
              disabled={loading}
            >
              {loading ? "Verifying…" : "Verify Request"}
            </button>
          </div>
        </section>

        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="results">
            <RequirementsCard
              requirements={result.requirements}
              buyerRequest={result.buyer_request}
            />

            {result.final_status === "NO_MATCH" ? (
              <div className="no-match-card">
                <span className="status-badge blocked">NO MATCH</span>
                <p>{result.message}</p>
              </div>
            ) : (
              <>
                <VerificationCard
                  product={result.proposed_product}
                  verification={result.verification}
                />

                {result.final_status === "SELF_CORRECTED" && (
                  <AlternativeCard
                    originalName={result.proposed_product.name}
                    alternative={result.alternative}
                    message={result.message}
                  />
                )}

                {result.final_status === "NO_ALTERNATIVE" && (
                  <div className="no-alt-card">
                    <span className="status-badge blocked">
                      NO VERIFIED ALTERNATIVE AVAILABLE
                    </span>
                    <p>
                      No product in this category satisfies every requirement.
                      Rather than make a false promise, CommitmentGuard stops
                      here.
                    </p>
                  </div>
                )}
              </>
            )}

            <AuditTrail entries={result.audit_trail} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
