import React, { useState } from 'react';

/**
 * Minimal "Forgot Password" page for requesting a password reset link.
 * Integrates with a backend endpoint: POST /api/auth/forgot-password { email }
 */
export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitted(false);
    try {
      const resp = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        throw new Error(data.message || 'Request failed');
      }
      setSubmitted(true);
    } catch (err) {
      setError(err.message || 'Request failed');
    }
  };

  return (
    <main role="main" aria-label="Forgot Password">
      <h1>Forgot Password</h1>
      {submitted ? (
        <div role="status" style={{ color: 'green' }}>
          If the email is registered, a password reset link has been sent.
        </div>
      ) : (
        <form onSubmit={handleSubmit} aria-label="Forgot Password Form">
          <label htmlFor="forgot-email">Email Address</label>
          <input
            id="forgot-email"
            name="email"
            type="email"
            value={email}
            autoComplete="email"
            required
            onChange={e => setEmail(e.target.value)}
            aria-label="Email Address"
          />
          <button type="submit" disabled={!email}>
            Send Reset Link
          </button>
          {error && (
            <div role="alert" style={{ color: 'red' }}>
              {error}
            </div>
          )}
        </form>
      )}
    </main>
  );
}
