"""
Resilience primitives: color logging, graceful fallback, and mode detection.

Companion repository for "Building Reliable AI-Assisted Software Systems"
Chapter 3: Defining Correctness and Golden Datasets
Author: Imran Ahmad

Same API as Chapter 2's resilience module: @graceful_fallback is the
deterministic shell at the scale of a single call.
"""

from __future__ import annotations

import functools
import getpass
import os
from typing import Any, Callable

import colorama
from colorama import Fore, Style
from dotenv import load_dotenv

# Windows-safe ANSI handling. strip=False keeps the color codes when stdout is
# not a TTY (Jupyter/CI streams); autoreset is done explicitly per message,
# because stream-level autoreset corrupts multi-part print output.
colorama.init(strip=False)

__author__ = "Imran Ahmad"

# --------------------------------------------------------------------------- #
# Visual logging schema: Blue = INFO, Green = SUCCESS, Red = HANDLED.          #
# --------------------------------------------------------------------------- #


def log_info(msg: str) -> None:
    """Blue informational line, e.g. tool-initialization progress."""
    print(f"{Fore.BLUE}[INFO] {msg}{Style.RESET_ALL}")


def log_success(msg: str) -> None:
    """Green success line, e.g. a step completing with valid output."""
    print(f"{Fore.GREEN}[SUCCESS] {msg}{Style.RESET_ALL}")


def log_error(msg: str) -> None:
    """Red handled-error line: the failure was contained, not fatal."""
    print(f"{Fore.RED}[HANDLED ERROR] {msg}{Style.RESET_ALL}")


# --------------------------------------------------------------------------- #
# The graceful_fallback decorator (exact Chapter 2 contract).                  #
# --------------------------------------------------------------------------- #


def graceful_fallback(
    fallback: Any, section: str, label: str = ""
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Wrap any risky call in a miniature deterministic shell.

    On success: log_success and return the result.
    On Exception: log_error in red, citing `section`, then return `fallback`
    (if callable, invoke it with the original *args/**kwargs).
    Re-raises KeyboardInterrupt and SystemExit. NEVER lets the notebook die.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        display = label or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = fn(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit):
                raise  # a human asked to stop; the shell never overrides that
            except Exception as exc:
                log_error(
                    f"{display} failed: {exc.__class__.__name__}. "
                    f"Falling back to Mock Logic for {section}."
                )
                if callable(fallback):
                    return fallback(*args, **kwargs)
                return fallback
            log_success(f"{display} succeeded.")
            return result

        return wrapper

    return decorator


# --------------------------------------------------------------------------- #
# Mode detection: never blocks, never prompts, never echoes a key.            #
# --------------------------------------------------------------------------- #

_SIM_BANNER = (
    "SIMULATION MODE - no API key detected, running fully offline. Every "
    "response comes from the committed snapshot and the deterministic mock "
    "layer, and every number in this notebook is reproducible without a key."
)


def detect_mode() -> str:
    """Return 'LIVE' or 'SIMULATION' and print a color banner.

    Reads `.env` via load_dotenv(), then checks OPENAI_API_KEY /
    ANTHROPIC_API_KEY with os.getenv. NEVER prompts stdin.
    """
    load_dotenv()
    key_source = next(
        (name for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY") if os.getenv(name)),
        None,
    )
    if key_source:
        print(
            f"{Fore.BLUE}{Style.BRIGHT}LIVE MODE - {key_source} detected via "
            "environment/.env. The key value is never printed; any failed live "
            f"call falls back to the deterministic mock layer.{Style.RESET_ALL}"
        )
        return "LIVE"
    print(f"{Fore.GREEN}{Style.BRIGHT}{_SIM_BANNER}{Style.RESET_ALL}")
    return "SIMULATION"


def enable_live_mode(provider: str = "openai") -> str:
    """Explicit opt-in helper: getpass a key, set os.environ, re-detect.

    Documented in the README; NEVER auto-invoked by the notebook. Some notebook
    frontends implement getpass poorly, so every input failure is contained and
    the current mode is preserved.
    """
    env_var = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}.get(
        provider.lower()
    )
    if env_var is None:
        log_error(f"unknown provider '{provider}'. Use 'openai' or 'anthropic'.")
        return detect_mode()
    try:
        key = getpass.getpass(f"Paste your {env_var} (input is hidden): ")
    except Exception as exc:  # e.g. StdinNotImplementedError, EOFError
        log_error(
            f"enable_live_mode failed: {exc.__class__.__name__}. "
            "Staying in the current mode; the .env route always works."
        )
        return detect_mode()
    if key.strip():
        os.environ[env_var] = key.strip()
    else:
        log_info("Empty input - no key stored.")
    return detect_mode()
