import { useState } from "react";
import { payForProduct } from "../payment";

function VerificationCard({ product, verification }) {
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [paymentError, setPaymentError] = useState(null);

  if (!product || !verification) return null;

  const statusClass =
    verification.status === "VERIFIED" ? "verified" : "blocked";

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
    <section className="panel">
      <div className="panel-header">
        <span className="panel-label">Commitment verification</span>

        <span className={`status-badge ${statusClass}`}>
          {verification.status}
        </span>
      </div>

      <div className="product-row">
        <div>
          <div className="product-name">{product.name}</div>

          <div className="product-meta">
            ₹{product.price} · {product.delivery_days} day delivery ·{" "}
            {product.stock} in stock
          </div>

          {product.category && (
            <div className="product-category">Category: {product.category}</div>
          )}
        </div>
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

      {verification.status === "VERIFIED" && (
        <div className="payment-block">
          {paymentStatus === "success" ? (
            <div className="payment-success">
              ✓ Payment successful. Order confirmed.
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
      )}
    </section>
  );
}

export default VerificationCard;
