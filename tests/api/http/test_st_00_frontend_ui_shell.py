# tests/api/http/test_st_00_frontend_ui_shell.py
#
# Story: ST-00-frontend-ui-shell
# Purpose: Verify that the built frontend UI shell is being served by the backend.

import os

from fastapi.testclient import TestClient

from app_backend.main import app, FRONTEND_DIST  # type: ignore[import]

client = TestClient(app)


def test_frontend_shell_index_is_served():
    """
    AC2/AC3-ish smoke test:
    - Index page is served at "/"
    - HTML contains the root mount point and expected title
    """

    # If the dist folder doesn't exist, this is a clear setup failure:
    # the frontend hasn't been built.
    assert os.path.isdir(
        FRONTEND_DIST
    ), "Frontend dist missing – run `npm run build` in app_frontend first."

    response = client.get("/")
    assert response.status_code == 200

    body = response.text
    # From app_frontend/index.html
    assert "<div id=\"root\">" in body
    assert "<title>SCV Frontend</title>" in body
