# Keep Your Render App Awake (Step-by-Step)

Since Render's Free Tier "sleeps" after 15 minutes of inactivity, you need an external service to "ping" (visit) your website automatically. This guide shows you how to use **UptimeRobot** (a free service) to do this.

## Prerequisite
Your app must be deployed and you must have your live URL (e.g., `https://os-buddy.onrender.com`).

## Method: Using UptimeRobot (Recommended)
This is a "set and forget" method. You do not need to keep your computer on.

1.  **Create an Account**
    *   Go to [UptimeRobot.com](https://uptimerobot.com/).
    *   Click **Register for FREE** and create an account.

2.  **Add a New Monitor**
    *   Once logged in, click **+ Add New Monitor** (button usually on the top left).

3.  **Configure the Monitor**
    *   **Monitor Type**: Select `HTTP(s)`.
    *   **Friendly Name**: Enter `OS Buddy Health Check` (or anything you like).
    *   **URL**: Enter your dedicated health URL:
        ```text
        https://os-buddy.onrender.com/healthz
        ```
        *(Note: Replace `https://os-buddy.onrender.com` with your actual Render URL if it's different. We added the `/healthz` part specially for this).*
    *   **Monitoring Interval**: Set to **5 minutes-** (Render sleeps after 15 mins, so 5 mins is safe).
    *   **Monitor Timeout**: Leave as default.

4.  **Save**
    *   Click **Create Monitor**.

## Result
UptimeRobot will visit your site every 5 minutes.
*   This resets Render's 15-minute countdown.
*   Your app will never go to sleep.
*   The "Cold Start" loading screen will disappear.
