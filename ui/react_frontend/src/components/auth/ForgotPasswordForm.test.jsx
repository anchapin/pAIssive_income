import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ForgotPasswordForm from './ForgotPasswordForm';
import { MemoryRouter } from 'react-router-dom';

describe('ForgotPasswordForm', () => {
  it('renders form and submits email', async () => {
    render(
      <MemoryRouter>
        <ForgotPasswordForm />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /forgot password/i })).toBeInTheDocument();
    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'foo@example.com' } });
    fireEvent.click(screen.getByRole('button', { name: /send reset link/i }));
    // Wait for success confirmation
    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent(/reset link has been sent/i);
    });
  });

  it('shows error if email is empty and disables button', () => {
    render(
      <MemoryRouter>
        <ForgotPasswordForm />
      </MemoryRouter>
    );
    const button = screen.getByRole('button', { name: /send reset link/i });
    expect(button).toBeDisabled();
  });

  it('shows "Back to login" link', () => {
    render(
      <MemoryRouter>
        <ForgotPasswordForm />
      </MemoryRouter>
    );
    expect(screen.getByRole('link', { name: /back to login/i })).toBeInTheDocument();
  });
});