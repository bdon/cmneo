import { createSignal, Show } from 'solid-js';
import { apiClient } from '../lib/api';

export default function ForgotPasswordForm() {
  const [email, setEmail] = createSignal<string>('');
  const [error, setError] = createSignal<string>('');
  const [success, setSuccess] = createSignal<boolean>(false);
  const [loading, setLoading] = createSignal<boolean>(false);

  const handleSubmit = async (e: SubmitEvent): Promise<void> => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await apiClient.requestPasswordReset(email());
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send password reset email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="forgot-password-container">
      <h2>Forgot Password</h2>

      <Show when={error()}>
        <div class="error">{error()}</div>
      </Show>

      <Show when={success()}>
        <div class="success">
          Password reset instructions have been sent to your email if an account exists with that address.
        </div>
      </Show>

      <Show when={!success()}>
        <form onSubmit={handleSubmit}>
          <div class="form-group">
            <label for="email">Email</label>
            <input
              type="email"
              id="email"
              value={email()}
              onInput={(e) => setEmail(e.currentTarget.value)}
              required
              placeholder="Enter your email address"
            />
          </div>

          <button type="submit" disabled={loading()}>
            {loading() ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>
      </Show>
    </div>
  );
}
