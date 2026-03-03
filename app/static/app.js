// GEO Score — Checkout Handler
document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('checkout-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    var url = document.getElementById('url').value.trim();
    var email = document.getElementById('email').value.trim();
    var btn = form.querySelector('button[type="submit"]');
    if (btn) btn.disabled = true;

    try {
      var res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, email: email }),
      });
      var checkoutData = await res.json();
      var jobId = checkoutData.jobId;
      if (!res.ok) {
        alert(checkoutData.detail || 'Something went wrong');
        if (btn) btn.disabled = false;
        return;
      }
      if (jobId) {
        localStorage.setItem('geo_job_id', jobId);
      }
      window.location.href = checkoutData.checkout_url;
    } catch (err) {
      alert('Network error. Please try again.');
      if (btn) btn.disabled = false;
    }
  });
});
