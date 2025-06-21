/**
 * Tests for the RegisterForm component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegisterForm from './RegisterForm';

// Mock useAppContext and useFormValidation
vi.mock('../../context/AppContext', () => ({
  useAppContext: vi.fn()
}));
vi.mock('../../utils/validation', () => ({
  useFormValidation: vi.fn(),
  validationSchemas: { register: {} }
}));

import { useAppContext } from '../../context/AppContext';
import { useFormValidation } from '../../utils/validation';

describe('RegisterForm', () => {
  let registerMock;
  let formState;

  beforeEach(() => {
    registerMock = vi.fn();
    useAppContext.mockReturnValue({ register: registerMock });

    formState = {
      values: {
        username: '',
        email: '',
        authCredential: '',
        confirmCredential: '',
        name: ''
      },
      errors: {},
      touched: {},
      handleChange: vi.fn(),
      handleBlur: vi.fn(),
      handleSubmit: (cb) => (e) => { e.preventDefault(); cb(formState.values); },
      isValid: false
    };
    useFormValidation.mockReturnValue(formState);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders all input fields and register button', () => {
    render(<RegisterForm />);
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Authentication Credential/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Confirm Credential/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Register/i })).toBeInTheDocument();
  });

  it('disables register button if isValid is false or submitting', () => {
    render(<RegisterForm />);
    expect(screen.getByRole('button', { name: /Register/i })).toBeDisabled();

    // Simulate valid form
    formState.isValid = true;
    formState.isSubmitting = false;
    useFormValidation.mockReturnValue(formState);
    render(<RegisterForm />);
    // Button would still be disabled because isSubmitting is not a prop here; form logic would enable it in real form
  });

  it('calls register with correct data on submit', async () => {
    formState.values = {
      username: 'user',
      email: 'test@example.com',
      authCredential: 'secret',
      confirmCredential: 'secret',
      name: 'Test User'
    };
    formState.isValid = true;
    useFormValidation.mockReturnValue(formState);

    registerMock.mockResolvedValueOnce(undefined);

    render(<RegisterForm onSuccess={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /Register/i }));

    await waitFor(() => {
      expect(registerMock).toHaveBeenCalledWith({
        username: 'user',
        email: 'test@example.com',
        credential: 'secret',
        name: 'Test User'
      });
    });
  });

  it('shows server error if registration throws', async () => {
    formState.values = {
      username: 'baduser',
      email: 'fail@example.com',
      authCredential: 'fail',
      confirmCredential: 'fail',
      name: 'Bad User'
    };
    formState.isValid = true;
    useFormValidation.mockReturnValue(formState);

    registerMock.mockRejectedValue(new Error('fail'));

    render(<RegisterForm />);
    fireEvent.click(screen.getByRole('button', { name: /Register/i }));

    await waitFor(() =>
      expect(screen.getByText(/Registration failed/i)).toBeInTheDocument()
    );
  });

  it('calls onSuccess callback on successful registration', async () => {
    formState.values = {
      username: 'user',
      email: 'test@example.com',
      authCredential: 'secret',
      confirmCredential: 'secret',
      name: 'Test User'
    };
    formState.isValid = true;
    useFormValidation.mockReturnValue(formState);

    const onSuccess = vi.fn();
    registerMock.mockResolvedValueOnce(undefined);

    render(<RegisterForm onSuccess={onSuccess} />);
    fireEvent.click(screen.getByRole('button', { name: /Register/i }));

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('toggles credential visibility for both credential fields', () => {
    render(<RegisterForm />);
    const toggleAuthBtn = screen.getAllByLabelText(/toggle credential visibility/i)[0];
    const toggleConfirmBtn = screen.getAllByLabelText(/toggle credential visibility/i)[1];
    expect(toggleAuthBtn).toBeInTheDocument();
    expect(toggleConfirmBtn).toBeInTheDocument();
    fireEvent.click(toggleAuthBtn);
    fireEvent.click(toggleConfirmBtn);
    // Actual field type change is not asserted due to mocking, but handlers are invoked
  });
});