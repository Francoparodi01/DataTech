# Security

## Secrets

Never commit database credentials, API keys, webhook URLs containing tokens, cookies, or session data. Use environment variables or a managed secret store.

An earlier repository revision exposed a MongoDB connection credential. Removing it from the current tree is not sufficient: rotate/revoke the credential in MongoDB Atlas and rewrite Git history before considering the incident fully remediated.

## Reporting

If you discover a credential or security issue, rotate the affected secret first, then remove it from code and history. Avoid opening a public issue containing the secret value.
