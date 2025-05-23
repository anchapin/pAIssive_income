import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ResetPasswordForm from './ResetPasswordForm';
import { MemoryRouter } from 'react-router-dom';

describe('ResetPasswordForm', () => {
  it('renders form and resets password successfully', async () => {
    render(
      <MemoryRouter>
        <ResetPasswordForm />
      </MemoryRouter>
    );
    fireEvent.change(screen.getByLabelText(/new password/i), { target: { value: 'abc123456' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'abc123456' } });
    fireEvent.click(screen.getByRole('button', { name: /reset password/i }));
    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent(/password has been reset/i);
    });
  });

  it('shows error if passwords do not match', async () => {
    render(
      <MemoryRouter>
        <ResetPasswordForm />
      </MemoryRouter>
    );
    fireEvent.change(screen.getByLabelText(/new password/i), { target: { value: 'abc123456' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'different' } });
    fireEvent.click(screen.getByRole('button', { name: /reset password/i }));
    await screen.findByText(/do not match/i);
  });

  it('shows error if password is too short', async () => {
    render(
      <MemoryRouter>
        <ResetPasswordForm />
      </MemoryRouter>
    );
    fireEvent.change(screen.getByLabelText(/new password/i), { target: { value: 'short' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'short' } });
    fireEvent.click(screen.getByRole('button', { name: /reset password/i }));
    await screen.findByText(/at least 8/i);
  });

  it('shows "Back to login" link', () => {
    render(
      <MemoryRouter>
        <ResetPasswordForm />
      </MemoryRouter>
    );
    expect(screen.getByRole('link', { name: /back to login/i })).toBeInTheDocument();
  });
});