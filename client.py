# web client stuff
# define URL resources
BASE_URL = "https://freesound.org/apiv2"
SOUNDS = "/sounds"
SEARCH = "/search/text"
DOWNLOAD = "/download"
AUTHORIZE = "/oauth2/authorize"

# where to download samples too
TARGET_DIR = 'tmp/'

class ApiClient:
    def __init__(self, client_key, secret_key):
        self.client_key = client_key
        self.secret_key = secret_key
        self.oauth2_code

    def oauth2_authorize():
        oauth = OAuth2Session(
            CLIENT_ID, redirect_uri='https://freesound.org/home/app_permissions/permission_granted/'
        )

        authorization_url, state = oauth.authorization_url(
            'https://freesound.org/apiv2/oauth2/authorize/'
        )
        # open new browser
        webbrowser.open_new(authorization_url)

        # request code from browser
        authorization_response=input("type in authorization code: ")
        r = requests.post(
            'https://freesound.org/apiv2/oauth2/access_token/',
            params={
                'client_id': CLIENT_ID,
                'client_secret': SECRET_KEY,
                'grant_type': 'authorization_code',
                'code': authorization_response
            }
        )

        if r.status_code != 200:
            print("error during OAuth2 authorization")
            return False

        oauth2_code = r.json()['access_token']
        return True

    
