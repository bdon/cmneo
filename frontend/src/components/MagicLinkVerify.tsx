import { createSignal, onMount, Show } from 'solid-js';
import { apiClient } from '../lib/api';

type VerifyStatus = 'verifying' | 'success' | 'error';

export default function MagicLinkVerify() {
  const [status, setStatus] = createSignal<VerifyStatus>('verifying');
  const [errorMessage, setErrorMessage] = createSignal<string>('');

  onMount(async () => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    if (!token) {
      setStatus('error');
      setErrorMessage('Invalid magic link');
      return;
    }

    try {
      await apiClient.verifyMagicLink(token);
      setStatus('success');
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1000);
    } catch (err) {
      setStatus('error');
      setErrorMessage(err instanceof Error ? err.message : 'Verification failed');
    }
  });

  return (
    <div class="card">
      <Show when={status() === 'verifying'}>
        <p>Verifying your magic link...</p>
      </Show>

      <Show when={status() === 'success'}>
        <div class="success">Login successful! Redirecting...</div>
      </Show>

      <Show when={status() === 'error'}>
        <div class="error">{errorMessage()}</div>
      </Show>
    </div>
  );
}
