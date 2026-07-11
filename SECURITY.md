# SECURITY.md

# Security Policy

Thank you for helping improve the security of **TransferX**. We take security seriously and appreciate responsible disclosure of vulnerabilities.

---

# Supported Versions

| Version | Supported |
|----------|-----------|
| 1.x.x | ✅ Yes |
| < 1.0 | ❌ No |

Only the latest stable release receives security updates and bug fixes.

---

# Reporting a Security Vulnerability

If you discover a security vulnerability, **please do not report it publicly**.

Instead, report it privately using one of the following methods:

- Email: **your-email@example.com**
- GitHub Issues: **Do not create a public issue for security vulnerabilities.**
- Marketplace Messaging: If you purchased the project from a marketplace, contact the seller directly.

Please include the following information:

- Description of the vulnerability
- Steps to reproduce
- Affected version
- Expected behavior
- Actual behavior
- Screenshots or logs (if applicable)
- Suggested fix (optional)

---

# Responsible Disclosure

We kindly request that you:

- Allow reasonable time for investigation.
- Avoid publicly disclosing vulnerabilities before a fix is available.
- Do not access or modify data that does not belong to you.
- Do not perform denial-of-service attacks.
- Do not attempt to compromise production systems.

---

# Security Best Practices

For production deployments, we recommend the following:

## Environment Variables

- Store secrets in a `.env` file.
- Never commit the `.env` file to version control.
- Rotate credentials periodically.

---

## Secret Key

Use a long, randomly generated secret key.

Example:

```env
SECRET_KEY=generate-a-long-random-secret-key
```

Never reuse the default key.

---

## SMTP Credentials

- Use App Passwords whenever supported.
- Never hardcode SMTP credentials.
- Use environment variables.
- Rotate credentials if compromised.

---

## Password Security

TransferX is designed to:

- Store hashed passwords only.
- Never store plaintext passwords.
- Verify passwords securely.

Developers should always use secure password hashing mechanisms and avoid implementing custom encryption.

---

## HTTPS

Always deploy behind HTTPS.

Recommended:

- Let's Encrypt
- Nginx
- Apache
- Cloudflare SSL

Never transmit login credentials over HTTP.

---

## Session Security

Recommended settings:

- Secure Cookies
- HTTPOnly Cookies
- SameSite Cookies
- Session Expiration

---

## File Upload Security

If file uploads are enabled:

- Restrict allowed file types.
- Limit maximum upload size.
- Sanitize filenames.
- Validate uploaded files.
- Store uploads outside the web root whenever possible.
- Scan uploads for malware before processing.

---

## Database Security

- Backup regularly.
- Restrict database permissions.
- Never expose the database publicly.
- Encrypt backups.

---

## Dependency Management

Keep dependencies updated.

Regularly run:

```bash
pip install --upgrade -r requirements.txt
```

Monitor dependencies for known vulnerabilities.

---

## Access Control

Always:

- Protect administrative routes.
- Restrict sensitive endpoints.
- Validate user permissions.
- Verify authentication before granting access.

---

## Logging

Avoid logging:

- Passwords
- API Keys
- SMTP Credentials
- Session Tokens
- Authentication Cookies

Logs should never contain sensitive information.

---

# Security Checklist

Before deploying to production, verify that:

- [ ] `.env` is configured correctly.
- [ ] Debug mode is disabled.
- [ ] HTTPS is enabled.
- [ ] Secret keys are unique.
- [ ] SMTP credentials are secure.
- [ ] File upload restrictions are enabled.
- [ ] Database backups are configured.
- [ ] Sensitive files are excluded from version control.

---

# Third-Party Components

TransferX may use third-party libraries.

Keep all dependencies updated to their latest stable versions to reduce security risks.

---

# Disclaimer

While every effort has been made to build a secure application, no software is completely free of vulnerabilities.

Developers are responsible for securely deploying, configuring, and maintaining their own installations.

---

# Contact

For security-related concerns, please contact:

**Email:** your-email@example.com

Thank you for helping keep TransferX secure.