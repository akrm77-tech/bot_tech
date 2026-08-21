# Security Policy

## Reporting a vulnerability

Do not publish tokens, credentials, personal data, or exploit details in a public issue. Report security concerns privately to the repository owner through GitHub.

## Secret handling

The Telegram bot token must be supplied through the `BOT_TOKEN` environment variable. Administrator IDs and channel settings should be reviewed before deployment. Never commit `.env` files, databases, logs, or exported user data.

## Rotation

If a token has ever appeared in source control or logs, revoke it in Telegram BotFather, create a replacement, update the deployment secret, and review the Git history for additional exposure.
