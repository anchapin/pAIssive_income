import React, { useState } from 'react';

const ResetPasswordPage = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  // In a real app, token would come from URL query params
  const token = "dummy-token";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitted(false);

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (newPassword !== confirm) {
      setError('Passwords do not match.');
      return;
    }

    try {
      // Replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      setSubmitted(true);
    } catch (err) {
      setError('Failed to reset password. Try again.');
    }
  };

  return (
    <main>
      <h1>Reset Password</h1>
      {submitted ? (
        <div role="status" aria-live="polite">
          <p>Your password has been reset successfully. <a href="/login">Return to login</a></p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} aria-label="Reset Password Form">
          <label htmlFor="reset-password">New Password</label>
          <input
            id="reset-password"
            type="password"
            value={newPassword}
            autoComplete="new-password"
            onChange={e => setNewPassword(e.target.value)}
            required
          />
          <label htmlFor="reset-confirm">Confirm New Password</label>
          <input
            id="reset-confirm"
            type="password"
            value={confirm}
            autoComplete="new-password"
            onChange={e => setConfirm(e.target.value)}
            required
          />
          <button type="submit">Reset Password</button>
          {error && <div role="alert">{error}</div>}
        </form>
      )}
      <a href="/login">Back to Login</a>
    </main>
  );
};

export default ResetPasswordPage;