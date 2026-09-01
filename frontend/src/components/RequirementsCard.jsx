function RequirementsCard({ requirements, buyerRequest }) {
  if (!requirements) return null;

  function formatDate(dateString) {
    if (!dateString) return null;

    const date = new Date(`${dateString}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
      return dateString;
    }

    return date.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  }

  function getDeliveryText() {
    const deadline = formatDate(requirements.delivery_deadline);
    const condition = requirements.delivery_condition;

    if (deadline) {
      if (condition === "before") {
        return `Before ${deadline}`;
      }

      if (condition === "within") {
        return `Within ${requirements.max_delivery_days} day(s), by ${deadline}`;
      }

      return `By ${deadline}`;
    }

    if (requirements.max_delivery_days != null) {
      return `Within ${requirements.max_delivery_days} day(s)`;
    }

    return "Not specified";
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <span className="panel-label">AI understanding</span>

        <span className="source-tag">{requirements.source}</span>
      </div>

      <p className="quoted-request">"{buyerRequest}"</p>

      <div className="requirement-grid">
        {/* PRODUCT */}
        <div className="requirement-item">
          <span className="req-key">Product</span>

          <span className="req-value">
            {requirements.product || "Not specified"}
          </span>
        </div>

        {/* CATEGORY */}
        <div className="requirement-item">
          <span className="req-key">Category</span>

          <span className="req-value">
            {requirements.category || "Not specified"}
          </span>
        </div>

        {/* BUDGET */}
        <div className="requirement-item">
          <span className="req-key">Maximum budget</span>

          <span className="req-value">
            {requirements.max_budget != null
              ? `₹${requirements.max_budget.toLocaleString("en-IN")}`
              : "Not specified"}
          </span>
        </div>

        {/* DELIVERY */}
        <div className="requirement-item">
          <span className="req-key">Delivery required</span>

          <span className="req-value">{getDeliveryText()}</span>
        </div>
      </div>
    </section>
  );
}

export default RequirementsCard;
