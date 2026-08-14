import pytest
from arxiv_digest.config import ConfigError, load_config


def test_defaults_with_credentials():
    env = {"EMAIL_USERNAME": "me@gmail.com", "EMAIL_PASSWORD": "secret"}
    cfg = load_config(env)
    assert cfg.username == "me@gmail.com"
    assert cfg.password == "secret"
    assert cfg.to_emails == "me@gmail.com"  # defaults to sender
    assert cfg.smtp_server == "smtp.gmail.com"
    assert cfg.smtp_port == 587
    assert cfg.max_results == 50
    assert "cs.LG" in cfg.category_list and "cs.CV" in cfg.category_list


def test_env_email_to_and_overrides():
    env = {
        "EMAIL_USERNAME": "me@gmail.com",
        "EMAIL_PASSWORD": "secret",
        "EMAIL_TO": "a@x.com, b@x.com",
        "DIGEST_MAX_RESULTS": "100",
        "DIGEST_CATEGORIES": "cs.CL",
    }
    cfg = load_config(env, max_results=25)
    assert cfg.to_emails == "a@x.com, b@x.com"
    assert cfg.category_list == ["cs.CL"]
    assert cfg.max_results == 25  # CLI beats env


def test_cli_categories_override_env():
    env = {"EMAIL_USERNAME": "m", "EMAIL_PASSWORD": "p", "DIGEST_CATEGORIES": "cs.AI"}
    assert load_config(env, categories="cs.LG").category_list == ["cs.LG"]


def test_query_built_from_categories():
    env = {"EMAIL_USERNAME": "m", "EMAIL_PASSWORD": "p"}
    cfg = load_config(env, categories="cs.LG, cs.AI")
    assert cfg.query == "cat:cs.LG+OR+cat:cs.AI"


def test_dry_run_allows_missing_credentials():
    env = {}
    cfg = load_config(env, dry_run=True)
    assert cfg.username == ""


def test_missing_credentials_raise():
    with pytest.raises(ConfigError):
        load_config({})


def test_invalid_max_results_raise():
    env = {"EMAIL_USERNAME": "m", "EMAIL_PASSWORD": "p"}
    with pytest.raises(ConfigError):
        load_config(env, max_results=0)
    with pytest.raises(ConfigError):
        load_config(env, max_results=501)