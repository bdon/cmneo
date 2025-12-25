import { createSignal } from 'solid-js';
import { apiClient } from '../lib/api';

export default function RegisterForm() {
  const [email, setEmail] = createSignal('');
  const [password, setPassword] = createSignal('');
  const [firstName, setFirstName] = createSignal('');
  const [lastName, setLastName] = createSignal('');
  const [error, setError] = createSignal('');
  const [loading, setLoading] = createSignal(false);

  const handleRegister = async (e: Event) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await apiClient.register(email(), password(), firstName(), lastName());
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="register-container">
      <h2>Register</h2>

      {error() && <div class="error">{error()}</div>}

      <form onSubmit={handleRegister}>
        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            value={email()}
            onInput={(e) => setEmail(e.currentTarget.value)}
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            value={password()}
            onInput={(e) => setPassword(e.currentTarget.value)}
            required
            minLength={8}
          />
        </div>

        <div class="form-group">
          <label for="firstName">First Name</label>
          <input
            type="text"
            id="firstName"
            value={firstName()}
            onInput={(e) => setFirstName(e.currentTarget.value)}
          />
        </div>

        <div class="form-group">
          <label for="lastName">Last Name</label>
          <input
            type="text"
            id="lastName"
            value={lastName()}
            onInput={(e) => setLastName(e.currentTarget.value)}
          />
        </div>

        <button type="submit" disabled={loading()}>
          {loading() ? 'Creating account...' : 'Register'}
        </button>
      </form>
    </div>
  );
}
