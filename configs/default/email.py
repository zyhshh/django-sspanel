import os

# 是否开启邮件功能
USE_SMTP = True

# ANYMAIL = {"MAILGUN_API_KEY": "", "MAILGUN_SENDER_DOMAIN": ""}
# EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

# django anymail
ANYMAIL = {
    "SENDGRID_API_KEY": os.environ.get("SENDGRID_API_KEY"),
}
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
DEFAULT_FROM_EMAIL = "vpn@sspannel.com"
