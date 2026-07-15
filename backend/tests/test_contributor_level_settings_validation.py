from copy import deepcopy

import pytest

from app.api.services.settings import (
    DEFAULT_CONTRIBUTOR_LEVEL_SETTINGS,
    validate_contributor_level_settings,
)


def valid_settings():
    return deepcopy(DEFAULT_CONTRIBUTOR_LEVEL_SETTINGS)


def test_valid_settings_are_accepted():
    assert validate_contributor_level_settings(valid_settings()) == valid_settings()


@pytest.mark.parametrize("count", [9, 11])
def test_settings_must_contain_exactly_ten_levels(count):
    with pytest.raises(ValueError):
        validate_contributor_level_settings(
            valid_settings()[:count] + ([valid_settings()[-1]] if count == 11 else [])
        )


def test_missing_level_is_rejected():
    payload = valid_settings()
    payload.pop(4)
    payload.append({"level": 10, "name": "另一稱號", "min_exp": 60})
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


def test_duplicate_level_is_rejected():
    payload = valid_settings()
    payload[4]["level"] = 4
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


def test_out_of_order_level_is_rejected():
    payload = valid_settings()
    payload[3], payload[4] = payload[4], payload[3]
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


def test_blank_name_is_rejected():
    payload = valid_settings()
    payload[2]["name"] = "\u200b  "
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


def test_duplicate_name_is_rejected():
    payload = valid_settings()
    payload[2]["name"] = payload[1]["name"]
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


def test_unknown_field_is_rejected():
    payload = valid_settings()
    payload[0]["unknown"] = "value"
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


@pytest.mark.parametrize("value", [-1, 2.5, True])
def test_invalid_min_exp_is_rejected(value):
    payload = valid_settings()
    payload[2]["min_exp"] = value
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


@pytest.mark.parametrize("value", [2, 1])
def test_non_increasing_min_exp_is_rejected(value):
    payload = valid_settings()
    payload[2]["min_exp"] = value
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


def test_level_one_must_start_at_zero():
    payload = valid_settings()
    payload[0]["min_exp"] = 1
    with pytest.raises(ValueError):
        validate_contributor_level_settings(payload)


def test_level_ten_highest_threshold_is_accepted():
    payload = valid_settings()
    payload[9]["min_exp"] = 100
    assert validate_contributor_level_settings(payload)[9]["min_exp"] == 100
