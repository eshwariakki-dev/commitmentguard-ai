const API_BASE = 'http://localhost:5000'

/**
 * Opens Razorpay's test-mode checkout for a given verified product.
 * Called only after CommitmentGuard has already verified the product -
 * this function does not decide fulfillability, it only handles payment.
 */
export async function payForProduct(product, onSuccess, onFailure) {
  try {
    const orderRes = await fetch(`${API_BASE}/api/create-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: product.price }),
    })

    if (!orderRes.ok) throw new Error('Failed to create order')
    const orderData = await orderRes.json()

    const options = {
      key: orderData.key_id,
      amount: orderData.amount * 100,
      currency: 'INR',
      name: 'CommitmentGuard AI',
      description: product.name,
      order_id: orderData.order_id,
      handler: function (response) {
        onSuccess(response)
      },
      modal: {
        ondismiss: function () {
          onFailure('Payment cancelled')
        },
      },
      theme: { color: '#5B8DEF' },
    }

    const rzp = new window.Razorpay(options)
    rzp.on('payment.failed', function (response) {
      onFailure(response.error.description || 'Payment failed')
    })
    rzp.open()
  } catch (err) {
    onFailure(err.message)
  }
}