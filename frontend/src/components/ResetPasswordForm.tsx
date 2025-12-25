import { createSignal, onMount, Show } from 'solid-js';
import { apiClient } from '../lib/api';

export default function ResetPasswordForm() {
  const [token, setToken] = createSignal<string>('');
  const [newPassword, setNewPassword] = createSignal<string>('');
  const [confirmPassword, setConfirmPassword] = createSignal<string>('');
  const [error, setError] = createSignal<string>('');
  const [success, setSuccess] = createSignal<boolean>(false);
  const [loading, setLoading] = createSignal<boolean>(false);

  onMount(() => {
    // Get token from URL query params
    const params = new URLSearchParams(window.location.search);
    const tokenParam = params.get('token');
    if (tokenParam) {
      setToken(tokenParam);
    } else {
      setError('Invalid or missing reset token');
    }
  });

  const handleSubmit = async (e: SubmitEvent): Promise<void> => {
    e.preventDefault();
    setError('');

    if (newPassword() !== confirmPassword()) {
      setError('Passwords do not match');
      return;
    }

    if (newPassword().length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      await apiClient.confirmPasswordReset(token(), newPassword());
      setSuccess(true);
      // Redirect to login after 2 seconds
      setTimeout(() => {
        window.location.href = '/auth/login';
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="reset-password-container">
      <h2>Reset Password</h2>

      <Show when={error()}>
        <div class="error">{error()}</div>
      </Show>

      <Show when={success()}>
        <div class="success">
          Password has been reset successfully! Redirecting to login...
        </div>
      </Show>

      <Show when={!success() && token()}>
        <form onSubmit={handleSubmit}>
          <div class="form-group">
            <label for="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              value={newPassword()}
              onInput={(e) => setNewPassword(e.currentTarget.value)}
              required
              minLength={8}
              placeholder="Enter new password"
            />
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword()}
              onInput={(e) => setConfirmPassword(e.currentTarget.value)}
              required
              minLength={8}
              placeholder="Confirm new password"
            />
          </div>

          <button type="submit" disabled={loading()}>
            {loading() ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
      </Show>
    </div>
  );
}
