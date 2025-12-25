# Security Guide

## Overview

This application implements production-ready security features for protecting user data and preventing common web vulnerabilities.

## Authentication Security

### Password Security

- **Hashing**: Django's default PBKDF2 algorithm with SHA256
- **Validation**:
  - Minimum 8 characters
  - Cannot be entirely numeric
  - Cannot be too similar to user information
  - Cannot be a common password
- **No plaintext storage**: Passwords are never stored in plaintext

### JWT Token Security

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 24 hours (configurable via `JWT_EXPIRY_HOURS`)
- **Secret Key**: Separate from Django secret key
- **Payload**: Contains user ID and email only (no sensitive data)

### Magic Link Security

- **Token Generation**: Cryptographically secure random tokens (32 bytes, URL-safe)
- **Expiration**: 15 minutes (configurable via `MAGIC_LINK_EXPIRY_MINUTES`)
- **One-time use**: Tokens are marked as used after verification
- **Separate secret**: Uses dedicated `MAGIC_LINK_SECRET`

## OWASP Top 10 Protections

### 1. Injection (SQL Injection)

**Protection**: Django ORM with parameterized queries

```python
# Safe - parameterized
User.objects.filter(email=user_input)

# NEVER DO THIS - vulnerable to SQL injection
User.objects.raw(f"SELECT * FROM users WHERE email = '{user_input}'")
```

### 2. Broken Authentication

**Protections**:
- Secure password hashing
- Token expiration
- One-time magic links
- No password hints or recovery answers
- Secure session management

### 3. Sensitive Data Exposure

**Protections**:
- HTTPS enforcement in production (`SECURE_SSL_REDIRECT`)
- Secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- Passwords never logged or displayed
- JWT tokens in Authorization header (not URL)

### 4. XML External Entities (XXE)

**Protection**: Not accepting XML input by default. If you add XML parsing, use defusedxml.

### 5. Broken Access Control

**Protections**:
- Authentication required for protected endpoints
- User can only access their own data
- Django's permission system for admin access

```python
# Example: Only authenticated users
@router.get("/me", auth=AuthBearer())
def get_current_user(request):
    return request.auth  # Pre-verified user
```

### 6. Security Misconfiguration

**Protections**:
- `DEBUG = False` in production
- Minimal allowed hosts
- Security headers enabled
- Default admin URL (consider changing `/admin/` to something else)
- No error details in production responses

### 7. Cross-Site Scripting (XSS)

**Protections**:
- Django template auto-escaping
- Content Security Policy headers
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection` header (legacy browsers)

Frontend protections:
- SolidJS auto-escapes by default
- Avoid `innerHTML` with user content
- Sanitize any user-generated content

### 8. Insecure Deserialization

**Protection**: Using Pydantic/Ninja schemas for validation, not accepting pickled data.

### 9. Using Components with Known Vulnerabilities

**Protections**:
- Keep dependencies updated
- Run `pip audit` regularly
- Use Dependabot or similar tools

```bash
# Check for vulnerabilities
pip install pip-audit
pip-audit
```

### 10. Insufficient Logging & Monitoring

**Recommendations**:
- Log authentication failures
- Monitor for unusual patterns
- Set up error tracking (Sentry)
- Track magic link usage

## Production Security Settings

### Required Settings

```python
# config/settings.py (production)
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
```

### CORS Configuration

```python
# Only allow your frontend
CORS_ALLOWED_ORIGINS = [
    'https://your-frontend.com',
]

# Enable credentials for cookie-based auth (if needed)
CORS_ALLOW_CREDENTIALS = True
```

## Secrets Management

### Environment Variables

**Never commit secrets to Git!**

Required secrets:
- `DJANGO_SECRET_KEY`: Django's secret key
- `JWT_SECRET`: Separate key for JWT tokens
- `MAGIC_LINK_SECRET`: Separate key for magic links
- `DATABASE_URL`: Database connection string
- `AWS_ACCESS_KEY_ID`: AWS credentials
- `AWS_SECRET_ACCESS_KEY`: AWS credentials

### Generating Secure Keys

```python
# Generate Django secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Generate other secrets (Python)
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### Rotation Policy

- Rotate secrets every 90 days
- Rotate immediately if compromised
- Use different keys for different purposes
- Keep old keys for grace period when rotating

## Database Security

### Connection Security

```python
# Use SSL for database connections
DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
```

### RDS Security

- Enable encryption at rest
- Enable encryption in transit
- Use IAM authentication (optional)
- Restrict security group access
- Enable automated backups
- Set retention period

## Email Security

### SES Configuration

- Use IAM user with minimal permissions (SendEmail only)
- Enable DKIM signing
- Configure SPF and DMARC records
- Monitor bounce and complaint rates

### Email Content Security

```python
# Avoid putting sensitive data in emails
# Include unsubscribe links
# Use HTTPS links only
# Set expiration times for magic links
```

## Rate Limiting

**Recommended**: Add rate limiting to prevent abuse

```python
# Example with django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login(request):
    # ...
```

Consider rate limiting:
- Login attempts: 5 per minute per IP
- Registration: 3 per hour per IP
- Magic link requests: 3 per hour per email
- API calls: 100 per minute per user

## Input Validation

### API Layer

All inputs are validated through Pydantic schemas:

```python
class LoginSchema(Schema):
    email: str  # Automatically validated
    password: str
```

### Additional Validation

```python
# Email validation
from django.core.validators import validate_email

# Custom validators
def validate_password_strength(password):
    if len(password) < 8:
        raise ValueError("Password too short")
    # Add more checks
```

## Headers Security

```python
# Recommended headers (already configured)
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

## Frontend Security

### API Token Storage

```typescript
// Use localStorage for tokens (acceptable for non-sensitive apps)
// For higher security, consider:
// - httpOnly cookies
// - Short-lived tokens with refresh tokens
// - Token encryption

// Current implementation
localStorage.setItem('access_token', token);
```

### XSS Prevention

```tsx
// SolidJS escapes by default
<div>{userInput}</div>  // Safe

// If you need HTML, sanitize first
import DOMPurify from 'dompurify';
<div innerHTML={DOMPurify.sanitize(userHTML)} />
```

### CSRF Protection

```typescript
// For cookie-based auth, include CSRF token
// Current JWT implementation doesn't need CSRF tokens
// But if you add cookie auth:
headers: {
  'X-CSRFToken': getCookie('csrftoken'),
}
```

## Monitoring & Incident Response

### Logging

```python
# Log authentication events
import logging
logger = logging.getLogger(__name__)

# Failed login
logger.warning(f"Failed login attempt for {email} from {ip}")

# Successful login
logger.info(f"User {email} logged in from {ip}")

# Magic link sent
logger.info(f"Magic link sent to {email}")
```

### Monitoring Checklist

- [ ] Set up error tracking (Sentry)
- [ ] Monitor failed login attempts
- [ ] Track unusual magic link patterns
- [ ] Set up uptime monitoring
- [ ] Configure database alerts
- [ ] Monitor API response times
- [ ] Track email delivery rates

### Incident Response Plan

1. **Detection**: Automated alerts for suspicious activity
2. **Containment**: Disable compromised accounts, rotate secrets
3. **Investigation**: Review logs, identify scope
4. **Recovery**: Restore from backups if needed
5. **Post-incident**: Update security measures

## Security Checklist for Production

- [ ] `DEBUG = False`
- [ ] Strong `SECRET_KEY` (not default, not in Git)
- [ ] Separate secrets for JWT and magic links
- [ ] HTTPS enforced
- [ ] Secure cookies enabled
- [ ] HSTS headers configured
- [ ] `ALLOWED_HOSTS` configured
- [ ] CORS origins restricted
- [ ] Database SSL enabled
- [ ] Database encryption at rest
- [ ] AWS SES production access
- [ ] Rate limiting implemented
- [ ] Error tracking configured
- [ ] Logging configured
- [ ] Backup strategy in place
- [ ] Dependencies up to date
- [ ] Security headers configured

## Regular Security Tasks

### Weekly
- Review authentication logs for anomalies
- Check error rates

### Monthly
- Update dependencies
- Review access logs
- Test backup restoration

### Quarterly
- Rotate secrets
- Security audit
- Penetration testing
- Review and update security policies

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email security contact (set this up)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE Top 25](https://cwe.mitre.org/top25/)
