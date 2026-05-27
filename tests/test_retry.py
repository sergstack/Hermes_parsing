from app.retry import RetryPolicy


def test_default_retry_policy_preserves_sleep_schedule():
    policy = RetryPolicy()

    assert policy.sleep_seconds(1) == 2.0
    assert policy.sleep_seconds(2) == 4.0


def test_retryable_error_retries_before_max_attempts():
    policy = RetryPolicy()

    assert policy.should_retry("download_timeout", attempt=1) is True
    assert policy.should_retry("download_timeout", attempt=2) is True
    assert policy.should_retry("download_timeout", attempt=3) is False


def test_non_retryable_error_stops():
    policy = RetryPolicy()

    assert policy.should_retry("login_expired", attempt=1) is False
    assert policy.should_retry("invalid_config", attempt=1) is False
    assert policy.should_retry("unknown", attempt=1) is False


def test_unknown_error_code_stops():
    policy = RetryPolicy()

    assert policy.should_retry("not_registered", attempt=1) is False
    assert policy.should_retry(None, attempt=1) is False


def test_max_attempts_is_honored():
    policy = RetryPolicy(max_attempts=2)

    assert policy.should_retry("download_timeout", attempt=1) is True
    assert policy.should_retry("download_timeout", attempt=2) is False
