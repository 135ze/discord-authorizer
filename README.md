# discord-authorizer
Verify incoming discord server users with Discord.py and Google Sheets API

Originally created for the CxC hackathon server to authorize incoming hackers to access private channels with roles.

This bot checks whether hackers are approved to participate in the hackathon, then whether they have registered as a member of the DSC club.

# Setup
1. Discord bot: add `DISCORD_TOKEN` and `DISCORD_GUILD` to `.env` file
2. Google Sheets: see https://developers.google.com/sheets/api/quickstart/go#authorize_credentials_for_a_desktop_application for `credentials.json` file
3. Discord server: add roles: `Verification Needed`, `Verified`, and `Admin`, as required.

# Usage
In the linked google sheet, create a first sheet containing a list of student ids and their Discord usernames. Then, in the second sheet, create a list of club members with their ids. Then, run the bot with a hosting service.

# Commands
1. `!verify`: Run by the user to be verified.
2. `!verifyall`: Run by admin users with the `Admin` role to accept all users in the linked Google Sheet.