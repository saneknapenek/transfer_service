from environs import Env



env = Env()
env.read_env()


CLIENT_ID = env('CLIENT_ID')
CLIENT_SECRET = env('CLIENT_SECRET')
AUTH_URI = env('AUTH_URI')
REDIRECT_URI_CALLBACK = env('REDIRECT_URI_CALLBACK')
REDIRECT_URI_TOKEN = env('REDIRECT_URI_TOKEN')
TOKEN_URI = env('TOKEN_URI')
TOKEN = ...

# TOKEN_URI = "https://oauth2.googleapis.com/token"
# AUTH_PROVIDER_X509_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
# CLIENT_SECRET = "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"