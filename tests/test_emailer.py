from unittest import mock
from arxiv_digest.emailer import build_message, send
from arxiv_digest.config import load_config


def _cfg():
    env = {
        "EMAIL_USERNAME": "me@gmail.com",
        "EMAIL_PASSWORD": "secret",
        "EMAIL_TO": "a@x.com, b@x.com",
    }
    return load_config(env)


def test_build_message_headers_and_attachment(tmp_path):
    attach = tmp_path / "wc.png"
    attach.write_bytes(b"PNGDATA")
    msg = build_message(_cfg(), "Subject X", "<p>body</p>", attachment_path=str(attach))
    assert msg["From"] == "me@gmail.com"
    assert msg["To"] == "a@x.com, b@x.com"
    assert msg["Subject"] == "Subject X"
    types = [p.get_content_type() for p in msg.get_payload()]
    assert "text/html" in types
    assert "application/octet-stream" in types


def test_send_uses_smtp_with_starttls():
    cfg = _cfg()
    with mock.patch("arxiv_digest.emailer.smtplib.SMTP") as smtp:
        send(cfg, "Subj", "<p>Body</p>")
        smtp.assert_called_once()
        server = smtp.return_value.__enter__.return_value
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("me@gmail.com", "secret")
        server.send_message.assert_called_once()