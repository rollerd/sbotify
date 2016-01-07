# Sbotify

Sbotify is small Python script that grabs the currently playing track from Spotify (or any service that supports scrobbling) and
creates a JSON payload for output to Slack webhook integration. Works for multiple users supplied in a text file.

# Sbotify Update

This was just a small test for fun to see how Slack integrations work (we had a #music channel, so why not?).
I don't plan on doing any more work with it.


# Requirements

The script user must have a last.fm API account.

Each user that wishes to display their currently playing track must have a last.fm account and enable scrobbling from Spotify (or other service) to last.fm

**pylast** - For connecting to last.fm API

**requests** - For POSTing to Slack webhook URL

**spotipy** - For connecting to Spotify unauthenticated API and grabbing track info 
