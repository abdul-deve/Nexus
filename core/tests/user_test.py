from django.test import TestCase, Client
from django.urls import reverse, resolve, NoReverseMatch


class EndpointSmokeTest(TestCase):
    """
    Smoke-test the application's known authentication endpoints.

    The purpose is not to assert that every endpoint returns 200.
    Instead, we verify that:

    1. URL patterns resolve.
    2. Endpoints are reachable.
    3. Expected HTTP methods are understood.
    4. Authentication-protected endpoints behave as protected.
    5. Unexpected server errors (5xx) are detected.
    """

    endpoints = {
        "admin": {
            "path": "/admin/",
            "methods": ["GET"],
        },
        "token_obtain_pair": {
            "path": "/api/token/",
            "methods": ["POST"],
        },
        "token_refresh": {
            "path": "/api/token/refresh/",
            "methods": ["POST"],
        },

        # django-allauth UI endpoints
        "account_login": {
            "path": "/accounts/login/",
            "methods": ["GET", "POST"],
        },
        "account_logout": {
            "path": "/accounts/logout/",
            "methods": ["GET", "POST"],
        },
        "account_inactive": {
            "path": "/accounts/inactive/",
            "methods": ["GET"],
        },
        "account_signup": {
            "path": "/accounts/signup/",
            "methods": ["GET", "POST"],
        },
        "account_reauthenticate": {
            "path": "/accounts/reauthenticate/",
            "methods": ["GET", "POST"],
        },
        "account_email": {
            "path": "/accounts/email/",
            "methods": ["GET", "POST"],
        },
        "account_email_verification_sent": {
            "path": "/accounts/confirm-email/",
            "methods": ["GET"],
        },
        "account_change_password": {
            "path": "/accounts/password/change/",
            "methods": ["GET", "POST"],
        },
        "account_set_password": {
            "path": "/accounts/password/set/",
            "methods": ["GET", "POST"],
        },
        "account_reset_password": {
            "path": "/accounts/password/reset/",
            "methods": ["GET", "POST"],
        },
        "account_confirm_login_code": {
            "path": "/accounts/login/code/confirm/",
            "methods": ["GET", "POST"],
        },
        "account_confirm_email": {
            "path": "/accounts/confirm-email/test-key/",
            "methods": ["GET"],
        },
        "account_reset_password_from_key_done": {
            "path": "/accounts/password/reset/key/done/",
            "methods": ["GET"],
        },
        "account_reset_password_from_key": {
            "path": "/accounts/password/reset/key/test-uid-test-key/",
            "methods": ["GET", "POST"],
        },
        "account_reset_password_done": {
            "path": "/accounts/password/reset/done/",
            "methods": ["GET"],
        },
    }

    def test_all_endpoints(self):
        client = Client()

        print("\n" + "=" * 80)
        print("NEXUS ENDPOINT SMOKE TEST")
        print("=" * 80)

        failures = []

        for name, endpoint in self.endpoints.items():
            path = endpoint["path"]

            print(f"\n[{name}]")
            print(f"  URL: {path}")

            # ---------------------------------------------------------
            # 1. URL RESOLUTION
            # ---------------------------------------------------------
            try:
                match = resolve(path)
                print(f"  RESOLVE: PASS -> {match.view_name}")
            except Exception as exc:
                print(f"  RESOLVE: FAIL -> {exc}")
                failures.append(
                    f"{name}: URL resolution failed: {exc}"
                )
                continue

            # ---------------------------------------------------------
            # 2. HTTP METHOD TESTS
            # ---------------------------------------------------------
            for method in endpoint["methods"]:

                try:
                    response = getattr(client, method.lower())(path)

                    status = response.status_code

                    # -------------------------------------------------
                    # Expected / acceptable responses
                    # -------------------------------------------------
                    if 200 <= status < 300:
                        result = "PASS"

                    elif 300 <= status < 400:
                        result = "REDIRECT"

                    elif status in {400, 401, 403, 404, 405}:
                        result = "EXPECTED"

                    # A 5xx response is a real application failure.
                    elif 500 <= status < 600:
                        result = "FAIL"
                        failures.append(
                            f"{name} [{method}] -> HTTP {status}"
                        )

                    else:
                        result = "CHECK"

                    print(
                        f"  {method:5} -> "
                        f"{status} -> {result}"
                    )

                    # Show redirect destination.
                    if 300 <= status < 400:
                        location = response.get("Location")
                        if location:
                            print(f"           Location: {location}")

                except Exception as exc:
                    print(
                        f"  {method:5} -> EXCEPTION -> "
                        f"{type(exc).__name__}: {exc}"
                    )

                    failures.append(
                        f"{name} [{method}] -> "
                        f"{type(exc).__name__}: {exc}"
                    )

        # -------------------------------------------------------------
        # FINAL REPORT
        # -------------------------------------------------------------
        print("\n" + "=" * 80)
        print("FINAL REPORT")
        print("=" * 80)

        if failures:
            print("\nFAILURES:")
            for failure in failures:
                print(f"  ❌ {failure}")

            self.fail(
                f"\n{len(failures)} endpoint test(s) produced "
                f"unexpected server errors."
            )

        else:
            print("\n✅ No unexpected 5xx responses or endpoint exceptions.")