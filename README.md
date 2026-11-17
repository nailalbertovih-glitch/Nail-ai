# NAIL AI — starter project

This is a **source-code starter**, not a compiled APK and not yet connected to any Telegram account.

## What is included
- `android/`: minimal Android app (Kotlin + Jetpack Compose) showing the control-panel shell.
- `backend/`: FastAPI service skeleton for Telegram Business webhook intake, AI draft generation, and manual approval before sending.
- `.env.example`: names of required secrets. Never put real keys in source control or send them in chat.

## Important limitations
- Android app and backend must be built/deployed and tested before use.
- Telegram Business connection requires a bot created with BotFather and explicitly connected by the account owner with appropriate permissions.
- This first design creates drafts only. It does not automatically send messages.
- The backend uses SQLite for a prototype. A production deployment needs HTTPS, persistent storage, access controls, backups, rate limits, and monitoring.

## Backend setup (on a computer or server)
1. Copy `backend/.env.example` to `backend/.env` and fill in secrets locally.
2. From `backend/`, create a virtual environment and install `requirements.txt`.
3. Run `uvicorn app:app --host 0.0.0.0 --port 8000` behind HTTPS.
4. Configure Telegram's webhook to `https://YOUR_DOMAIN/telegram/webhook` and set the same webhook secret in `.env`.
5. Connect the bot to Telegram Business in Telegram settings. Do not share bot tokens or API keys.

## Android build
Open the `android/` folder in Android Studio and build the `app` module. The project intentionally does not include a prebuilt APK or signing keys.


## Cloud build with GitHub Actions
1. Upload the contents of this folder to a GitHub repository (keep the `android/`, `backend/`, and `.github/` folders at the repository root).
2. Open the repository's **Actions** tab.
3. Select **NAIL AI build** and choose **Run workflow** (or push a commit touching `android/` or `backend/`).
4. When the run finishes, open the run and download the `NAIL-AI-debug-apk` artifact. Extract it to obtain `app-debug.apk`.

The workflow checks Python syntax and builds an unsigned debug APK. It does not deploy the backend, connect Telegram, or configure production secrets. Do not install this APK as a production app until it has been reviewed and tested.
