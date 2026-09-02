# CommitmentGuard AI

### Verify Before You Commit

## 📌 Overview

CommitmentGuard AI is a smart verification system for AI-powered shopping agents.

It checks whether a merchant can actually fulfill a customer's request before allowing the agent to make a commitment.

The system checks:

- Product availability
- Customer's budget
- Delivery requirement
- Suitable alternatives when the request cannot be fulfilled

This helps prevent an AI shopping agent from promising something the merchant cannot actually provide.

## 🎯 Problem Statement

AI shopping agents can make commitments to customers without first checking whether the merchant can actually fulfill the request.

For example, an agent may promise a product without checking:

- Whether the product is available
- Whether it is within the customer's budget
- Whether it can be delivered on time

This can lead to incorrect promises, failed orders, and a poor customer experience.

CommitmentGuard AI solves this by verifying the customer's requirements against the merchant's product information before allowing the commitment to proceed.

## 💡 Solution

CommitmentGuard AI follows a simple approach:

**Understand → Verify → Decide → Commit**

The system takes the customer's request in natural language and extracts the important requirements such as:

- Product
- Maximum budget
- Delivery requirement

It then searches the merchant catalog and verifies whether the requirements can be fulfilled.

If all conditions are satisfied, the commitment is marked as **VERIFIED**.

If the product is not available, the system gives **NO MATCH**.

If the requirements cannot be satisfied, the commitment is **BLOCKED** and the system looks for a suitable alternative.

An Audit Trail records the verification steps and the final decision.

## ✨ Key Features

- **Natural Language Request Parsing**  
  Understands customer requests and extracts product, budget, and delivery requirements.

- **Product Verification**  
  Checks the merchant catalog for matching products.

- **Budget Verification**  
  Ensures the product is within the customer's maximum budget.

- **Stock Verification**  
  Checks whether the required product is available.

- **Delivery Verification**  
  Checks whether the product can meet the customer's delivery requirement.

- **Alternative Suggestions**  
  Searches for a suitable alternative when the original request cannot be fulfilled.

- **Audit Trail**  
  Records the verification steps and explains how the final decision was reached.

- **Razorpay Test Payment**  
  Supports payment testing through Razorpay Test Mode.

## 🔄 How It Works

The system follows these steps:

1. **Customer Request**  
   The customer enters a request in natural language.

2. **Requirement Extraction**  
   The system extracts the product, budget, and delivery requirement.

3. **Product Search**  
   The system searches the merchant product catalog for a matching product.

4. **Verification**  
   The system checks:
   - Product availability
   - Stock
   - Budget
   - Delivery requirement

5. **Decision**
   - **VERIFIED** → All requirements are satisfied.
   - **NO MATCH** → The requested product is not available in the catalog.
   - **BLOCKED** → The requirements cannot be fulfilled.
   - **Alternative** → The system searches for a suitable alternative when possible.

6. **Audit Trail**  
   The verification steps and final decision are recorded.

7. **Payment**  
   If the commitment is verified, the customer can proceed to Razorpay payment.

## 🖥️ Project Screenshots

### Customer Request

The customer enters a request in natural language.

![Customer Request](screenshots/dashboard.png)

### Verified Commitment

The system verifies the product, stock, budget, and delivery requirements before allowing the customer to proceed.

![Verified Commitment](screenshots/verified.png)

### Audit Trail

The Audit Trail records the verification steps and shows how the final decision was reached.

![Audit Trail](screenshots/audit-trail.png)

### Razorpay Payment

After the commitment is verified, the customer can proceed to Razorpay Test Mode for payment testing.

![Razorpay Payment](screenshots/payment.png)

### No Match

If the requested product is not available in the merchant catalog, the system returns NO MATCH instead of showing an unrelated product.

![No Match](screenshots/no-match.png)

### Blocked Commitment

If the customer's requirements cannot be fulfilled, the system blocks the commitment and searches for a suitable alternative.

![Blocked Commitment](screenshots/blocked.png)

## 💳 Payment Testing

CommitmentGuard AI uses Razorpay Test Mode for payment testing.

No real money is involved during testing.

For card testing, the following test card number is used:

**Test Card:** `4100 2800 0000 1007`

This test card number is taken from Razorpay's official Test Card Details documentation.

A future expiry date and test CVV are used during the test payment.

A random mobile number is used only for testing purposes.

> Note: The payment integration is configured for Razorpay Test Mode and is not intended for real transactions.

## 🛠️ Technologies Used

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- Flask

### Payment

- Razorpay Test Mode

### Data

- JSON-based merchant product catalog

## 🌐 Live Demo

Try CommitmentGuard AI here:

👉 [Open Live Demo](https://commitmentguard-ai.vercel.app/)

## 👩‍💻 Author

**Eshwari V Akki**

GitHub: [eshwariakki-dev](https://github.com/eshwariakki-dev)
