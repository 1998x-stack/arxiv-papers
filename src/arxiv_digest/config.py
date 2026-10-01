"""Configuration: defaults, env var and CLI overrides, validation."""
from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_CATEGORIES = "cs.LG,cs.AI,cs.NE,cs.CV"
DEFAULT_MAX_RESULTS = 50
DEFAULT_SMTP_SERVER = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587


class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""


@dataclass
class Config:
    username: str
    password: str
    to_emails: str
    smtp_server: str
    smtp_port: int
    categories: str
    max_results: int
    dry_run: bool = False

    @property
    def category_list(self) -> list[str]:
        return [c.strip() for c in self.categories.split(",") if c.strip()]

    @property
    def query(self) -> str:
        return "+OR+".join(f"cat:{c}" for c in self.category_list)


def _load_env(env) -> dict:
    return {k: env[k] for k in env if k in {
        "EMAIL_USERNAME", "EMAIL_PASSWORD", "EMAIL_TO",
        "SMTP_SERVER", "SMTP_PORT", "DIGEST_CATEGORIES", "DIGEST_MAX_RESULTS"}}


def load_config(env=None, *, categories=None, max_results=None, to_emails=None, dry_run=False) -> Config:
    env = env if env is not None else os.environ
    username = env.get("EMAIL_USERNAME", "")
    password = env.get("EMAIL_PASSWORD", "")

    cats = categories or env.get("DIGEST_CATEGORIES") or DEFAULT_CATEGORIES
    mr = max_results if max_results is not None else int(env.get("DIGEST_MAX_RESULTS") or DEFAULT_MAX_RESULTS)
    to = to_emails or env.get("EMAIL_TO") or username
    smtp_server = env.get("SMTP_SERVER") or DEFAULT_SMTP_SERVER
    smtp_port = int(env.get("SMTP_PORT") or DEFAULT_SMTP_PORT)

    cfg = Config(username, password, to, smtp_server, smtp_port, cats, mr, dry_run)
    validate(cfg, dry_run)
    return cfg


def validate(cfg: Config, dry_run: bool) -> None:
    if not dry_run and (not cfg.username or not cfg.password):
        raise ConfigError(
            "EMAIL_USERNAME and EMAIL_PASSWORD are required "
            "(or use --dry-run)."
        )
    if not cfg.category_list:
        raise ConfigError("At least one DIGEST_CATEGORIES value is required.")
    if cfg.max_results < 1 or cfg.max_results > 500:
        raise ConfigError("max_results must be between 1 and 500.")
    if cfg.smtp_port < 1:
        raise ConfigError("SMTP_PORT must be a positive integer.")