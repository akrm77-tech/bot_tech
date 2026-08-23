# Security Policy

## Reporting a vulnerability

Do not publish tokens, passwords, personal data, or sensitive security details in public issues.

If you find a security problem, report it privately to the repository owner through GitHub.

## Secret handling

The Telegram bot token must be stored in the `BOT_TOKEN` environment variable.

Do not commit any of the following files or data:

* `.env` files
* Bot tokens
* Passwords
* Database files
* Log files containing sensitive information
* Exported user data
* API keys or other private credentials

Review administrator IDs and bot settings before deploying the project.

## Token rotation

If a bot token is exposed in source code, Git history, logs, or another public location:

1. Revoke the exposed token using Telegram BotFather.
2. Create a new token.
3. Update the deployment environment.
4. Check the Git history for other exposed secrets.

## Version

`1.0`

## Maintainer

[@akrm77-tech]
