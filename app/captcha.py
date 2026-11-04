import os

import requests

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
TEST_SITE_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
TEST_SECRET_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"


def site_key():
    return os.environ.get("RECAPTCHA_SITE_KEY", TEST_SITE_KEY)


def verify_captcha(token):
    if not token:
        return False
    secret = os.environ.get("RECAPTCHA_SECRET_KEY", TEST_SECRET_KEY)
    try:
        response = requests.post(VERIFY_URL, data={"secret": secret, "response": token}, timeout=5)
        return response.json().get("success", False)
    except requests.RequestException:
        return False
