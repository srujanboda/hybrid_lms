import requests
from django.conf import settings

def send_sms(phone, otp):
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"
        message = f"Your Hybrid LMS OTP is {otp}. It will expire in 5 minutes."

        payload = f"sender_id=TXTIND&message={message}&route=v3&numbers={phone}"
        headers = {
            'authorization': settings.FAST2SMS_API_KEY,
            'Content-Type': "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers)
        return response.json()
    except Exception as e:
        print("SMS sending error:", e)
        return None
