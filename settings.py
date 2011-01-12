
# These are the settings that tend to differ between installations of Streamer. Tweak these for your installation.

APP_NAME = "commently"

# API KEY - You can get this from https://code.google.com/apis/console/
API_KEY = ""

# This is the token that will act as a shared secret to verify that this application is the one that registered the given subscription. The hub will send us a challenge containing this token.
SECRET_TOKEN = "SOME_SECRET_TOKEN"

# Should we ignore the hubs defined in the feeds we're consuming
ALWAYS_USE_DEFAULT_HUB = False

# What PSHB hub should we use for feeds that don't support PSHB. pollinghub.appspot.com is a hub I've set up that does polling.
DEFAULT_HUB = "http://pubsubhubbub.appspot.com/"

# Each Buzz Activity is a pretty static URL.
ACTIVITY_URL = "https://www.googleapis.com/buzz/v1/activities/%s/@self/%s/@comments"

CALLBACK_URL = "https://%s.appspot.com/pubsub/callback" % APP_NAME

# Should anyone be able to add/delete subscriptions or should access be restricted to admins
OPEN_ACCESS = False

# How often should a task, such as registering a subscription, be retried before we give up
MAX_TASK_RETRIES = 10

# Maximum number of items to be fetched for any part of the system that wants everything of a given data model type
MAX_FETCH = 500

# Should Streamer check that posts it receives from a putative hub are for feeds it's actually subscribed to
SHOULD_VERIFY_INCOMING_POSTS = False

# Buzz API endpoint
BUZZ_ACTIVITIES = "https://www.googleapis.com/buzz/v1/activities/%s/@public"


PROFILE_URL_ROOT = "http://www.google.com/profiles/"

FILTER_MAP = {
  "actor.profileUrl" : "username",
  "id" : "id"
}

# Installation specific config ends.

