import os
import pytest
import types
import typing
import dataclasses

from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

from betdex import BetDexClient, BetDexError
from betdex.markets import Market
from betdex.resources import Response
from betdex.utils import get_fields, parse_datetime, to_snake_case


load_dotenv(Path(__file__).parents[1] / ".env")


R = typing.TypeVar("R", bound=Response)
SANDBOX_URL = "https://sandbox.api.btdx.io"
NOW = datetime.now(timezone.utc)
WEEK_AGO = NOW - timedelta(days=7)
CREDENTIALS = ("BETDEX_SANDBOX_APP_ID", "BETDEX_SANDBOX_API_SECRET", "BETDEX_SANDBOX_WALLET_ID")


@pytest.fixture(scope="session")
def client() -> BetDexClient:
    """
    A logged-in client on the sandbox; skips when credentials are missing.
    """
    missing = [name for name in CREDENTIALS if not os.environ.get(name)]
    if missing:
        pytest.skip(f"sandbox credentials not set: {', '.join(missing)}")
    sandbox = BetDexClient(*(os.environ[name] for name in CREDENTIALS), environment="sandbox")
    sandbox.create_session()
    return sandbox


@pytest.fixture(scope="session")
def wallet_id(client: BetDexClient) -> str:
    """
    The sandbox wallet the tests trade from.
    """
    assert client.conn.wallet_id
    return client.conn.wallet_id


@pytest.fixture(scope="session")
def app_id(client: BetDexClient) -> str:
    """
    The sandbox app the tests log in as.
    """
    assert client.conn.app_id
    return client.conn.app_id


@pytest.fixture(scope="session")
def open_market(client: BetDexClient) -> Market:
    """
    An open, unsuspended, pre-play market locking at least two hours from now.
    """
    soon = datetime.now(timezone.utc) + timedelta(hours=2)
    page = client.get_markets(statuses=["Open"], published=True, size=200)
    for market in page.markets:
        if (not market.suspended and market.in_play_status != "InPlay"
                and market.lock_at and market.lock_at > soon and market.market_outcomes.ids):
            return market
    pytest.skip("no open sandbox market to trade on")


def schema_errors(tp: typing.Any, value: typing.Any, path: str = "$") -> list[str]:
    """
    Ways a decoded JSON ``value`` doesn't match type ``tp``: keys the model doesn't
    declare, required fields missing or null, wrong types, unparseable timestamps
    and enum values outside the declared set.
    """
    args = [a for a in typing.get_args(tp) if a is not type(None)]
    origin = typing.get_origin(tp)
    optional = origin in (typing.Union, types.UnionType) and len(args) < len(typing.get_args(tp))
    if value is None:
        return [] if optional or tp is typing.Any else [f"{path}: null for non-optional {tp}"]
    if origin in (typing.Union, types.UnionType):
        models = [a for a in args if dataclasses.is_dataclass(a)]
        if models and isinstance(value, dict):
            keys = {to_snake_case(k) for k in value}
            best = max(models, key=lambda m: len(keys & set(get_fields(m))))
            return schema_errors(best, value, path)
        return schema_errors(args[0], value, path) if len(args) == 1 else []
    if origin is typing.Literal:
        return [] if value in typing.get_args(tp) else [f"{path}: {value!r} not in {tp}"]
    if origin is list:
        if not isinstance(value, list):
            return [f"{path}: expected a list, got {type(value).__name__}"]
        return [p for i, v in enumerate(value) for p in schema_errors(args[0], v, f"{path}[{i}]")]
    if origin is dict:
        if not isinstance(value, dict):
            return [f"{path}: expected an object, got {type(value).__name__}"]
        return [p for k, v in value.items() for p in schema_errors(args[1], v, f"{path}.{k}")]
    if dataclasses.is_dataclass(tp):
        model: typing.Any = tp
        if not isinstance(value, dict):
            return [f"{path}: expected an object, got {type(value).__name__}"]
        model_fields = get_fields(tp)
        given = {to_snake_case(k): (k, v) for k, v in value.items()}
        found = [f"{path}.{k}: not declared by {model.__name__}"
                 for name, (k, _) in given.items() if name not in model_fields]
        for field in dataclasses.fields(tp):
            if not field.init or field.name == "raw":
                continue
            required = (field.default is dataclasses.MISSING
                        and field.default_factory is dataclasses.MISSING)
            if field.name not in given:
                if required:
                    found.append(f"{path}: {model.__name__}.{field.name} missing")
                continue
            key, sub = given[field.name]
            found += schema_errors(model_fields[field.name], sub, f"{path}.{key}")
        return found
    if tp is datetime:
        try:
            parse_datetime(value)
        except BetDexError:
            return [f"{path}: {value!r} is not a timestamp"]
        return []
    if tp is float:
        ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        return [] if ok else [f"{path}: expected a number, got {value!r}"]
    if tp in (int, str, bool):
        ok = isinstance(value, tp) and not (tp is int and isinstance(value, bool))
        return [] if ok else [f"{path}: expected {tp.__name__}, got {value!r}"]
    return []


def check(result: R) -> R:
    """
    Assert a live response matches its model exactly, and return it.
    """
    found = schema_errors(type(result), result.raw)
    assert not found, f"{type(result).__name__} doesn't match the API:\n" + "\n".join(found[:20])
    return result
