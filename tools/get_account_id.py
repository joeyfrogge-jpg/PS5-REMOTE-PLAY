#!/usr/bin/env python3
"""
PSN Account ID (base64) helper for PS5-REMOTE-PLAY

This script helps you obtain the 8-byte little-endian base64 Account ID
required for console registration.

It does NOT store credentials. You authenticate directly with Sony.
"""

import base64
import sys
import webbrowser
from urllib.parse import urlparse, parse_qs

# Official Remote Play OAuth client parameters (publicly known)
CLIENT_ID = "ba495a24-818c-472b-b12d-ff231c1b5745"
REDIRECT_URI = "https://remoteplay.dl.playstation.net/remoteplay/redirect"

LOGIN_URL = (
    "https://auth.api.sonyentertainmentnetwork.com/2.0/oauth/authorize"
    "?service_entity=urn:service-entity:psn"
    "&response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    "&scope=psn:clientapp"
    "&request_locale=en_US"
    "&ui=pr"
    "&service_logo=ps"
    "&layout_type=popup"
    "&smcid=remoteplay"
    "&prompt=always"
    "&PlatformPrivacyWs1=minimal"
)


def main():
    print("=" * 60)
    print("PS5-REMOTE-PLAY – PSN Account ID (base64) Helper")
    print("=" * 60)
    print()
    print("1. A browser window will open to Sony’s official login page.")
    print("2. Sign in with your PSN account.")
    print("3. After login you will land on a mostly blank / ‘redirect’ page.")
    print("4. Copy the ENTIRE address bar URL and paste it below.")
    print()

    input("Press Enter to open the login page...")
    webbrowser.open(LOGIN_URL)

    print()
    redirect_url = input("Paste the full redirect URL here:\n> ").strip()

    if not redirect_url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    # Extract the authorization code
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)
    code = params.get("code", [None])[0]

    if not code:
        print("Could not find ‘code’ parameter in the URL.")
        print("Make sure you copied the full address bar after signing in.")
        sys.exit(1)

    print()
    print("Authorization code received. Exchange it for tokens...")

    # Note: A complete implementation would exchange the code for an access token
    # and then query the account info. For privacy and simplicity this helper
    # currently stops here and points the user to verified methods.
    #
    # The actual Account ID is obtained by calling Sony’s account API with the
    # resulting token and converting the numeric user_id to 8-byte little-endian
    # base64.

    print()
    print("For a fully automated extraction you can use one of these trusted tools:")
    print("  • https://pyrosoft.pro/psn-account-id/")
    print("  • Chiaki’s original psn-account-id.py (or community ports)")
    print()
    print("Once you have the numeric Account ID, convert it with:")
    print()
    print("    import base64")
    print("    account_id = 1234567890123456789   # replace with your number")
    print("    b64 = base64.b64encode(account_id.to_bytes(8, 'little')).decode()")
    print("    print(b64)")
    print()
    print("That base64 string is what you paste into PS5-REMOTE-PLAY when")
    print("registering your console.")
    print()


if __name__ == "__main__":
    main()
