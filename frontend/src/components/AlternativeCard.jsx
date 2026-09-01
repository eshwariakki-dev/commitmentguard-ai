import { useState } from "react";
import { payForProduct } from "../payment";

function AlternativeCard({ originalName, alternative, message }) {
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [paymentError, setPaymentError] = useState(null);

  if (!alternative) return null;
  const { product, verification } = alternative;

  function handlePay() {
    setPaymentStatus(null);
    setPaymentError(null);
    payForProduct(
      product,
      () => setPaymentStatus("success"),
      (errMsg) => {
        setPaymentStatus("failed");
        setPaymentError(errMsg);
      },
    );
  }

  return (
    <section className="panel corrected-panel">
      <div className="panel-header">
        <span className="panel-label">Self-correction</span>
        <span className="status-badge corrected">SELF-CORRECTED</span>
      </div>

      <p className="correction-message">{message}</p>

      <div className="alt-product-card">
        <div className="product-row">
          <div>
            <div className="product-name">{product.name}</div>
            <div className="product-meta">
              ₹{product.price} · {product.delivery_days} day delivery ·{" "}
              {product.stock} in stock
            </div>
          </div>
          <span className="status-badge verified small">VERIFIED</span>
        </div>

        <ul className="check-list">
          {verification.checks.map((check, i) => (
            <li
              key={i}
              className={`check-item ${check.passed ? "pass" : "fail"}`}
            >
              <span className="check-icon">{check.passed ? "✓" : "✗"}</span>
              <div>
                <div className="check-req">{check.requirement}</div>
                <div className="check-detail">{check.detail}</div>
              </div>
            </li>
          ))}
        </ul>

        <div className="payment-block">
          {paymentStatus === "success" ? (
            <div className="payment-success">
              ✓ Payment successful — order confirmed.
            </div>
          ) : (
            <>
              <button className="pay-btn" onClick={handlePay}>
                Proceed to Payment
              </button>
              {paymentStatus === "failed" && (
                <div className="payment-error">
                  Payment failed: {paymentError}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </section>
  );
}

export default AlternativeCard;
