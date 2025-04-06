# Content Submission Telegram Bot

This bot allows users to submit creative content (stories, quotes, poems) along with their details and optionally a photo. Submissions are forwarded to a specified Telegram group.

## Features
- Welcome message and category selection.
- Collects user's full name, age, and submission text.
- Optional photo upload.
- Forwards submissions to a Telegram group.
- Provides options to submit another entry or contact admin.

## Deployment Instructions

1. **Set up environment variables**:
   - Add `BOT_TOKEN` and `GROUP_CHAT_ID` to your Heroku app's config vars.
     ```bash
     heroku config:set BOT_TOKEN=your_bot_token
     heroku config:set GROUP_CHAT_ID=your_group_chat_id
     ```

2. **Deploy to Heroku**:
   - Push the code to GitHub and connect your repository to Heroku.
   - Deploy the app using the Heroku dashboard or CLI.

3. **Run the bot**:
   - Ensure the `worker` dyno is enabled in Heroku.

## Notes
- Replace `your_admin_username` in the bot code with your actual admin username.
- Ensure the bot has permissions to send messages to the target group.