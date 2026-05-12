"""Tests for session endpoints."""

import io
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_llm_chat():
    """Mock LLM chat to return predictable responses."""
    with patch("app.api.v1.endpoints.session.llm.chat") as mock:
        mock.return_value = '{"answer": "这是测试回答。", "chart_suggestions": null}'
        yield mock


@pytest.mark.asyncio
async def test_create_session(client, auth_headers):
    # upload dataset first
    content = b"col1,col2\n1,2\n3,4\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("sess.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]

    resp = await client.post(
        "/api/session/create",
        json={"dataset_id": ds_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["dataset_id"] == ds_id
    assert data["conversation_history"] == []


@pytest.mark.asyncio
async def test_list_sessions(client, auth_headers):
    # create at least one session
    content = b"x,y\n1,2\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("sesslist.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]
    await client.post(
        "/api/session/create",
        json={"dataset_id": ds_id},
        headers=auth_headers,
    )

    resp = await client.get("/api/session/list", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_session(client, auth_headers):
    content = b"x,y\n1,2\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("getsess.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]
    created = await client.post(
        "/api/session/create",
        json={"dataset_id": ds_id},
        headers=auth_headers,
    )
    sess_id = created.json()["id"]

    resp = await client.get(f"/api/session/{sess_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == sess_id


@pytest.mark.asyncio
async def test_delete_session(client, auth_headers):
    content = b"x,y\n1,2\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("delsess.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]
    created = await client.post(
        "/api/session/create",
        json={"dataset_id": ds_id},
        headers=auth_headers,
    )
    sess_id = created.json()["id"]

    resp = await client.delete(f"/api/session/{sess_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_session_query(client, auth_headers, mock_llm_chat):
    content = b"city,population\nBeijing,2000\nShanghai,2500\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("query.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]
    created = await client.post(
        "/api/session/create",
        json={"dataset_id": ds_id},
        headers=auth_headers,
    )
    sess_id = created.json()["id"]

    resp = await client.post(
        f"/api/session/{sess_id}/query",
        json={"question": "哪个城市人口最多？"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["model"]


@pytest.mark.asyncio
async def test_session_query_quota(client, auth_headers, mock_llm_chat):
    content = b"a,b\n1,2\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("quota.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]
    created = await client.post(
        "/api/session/create",
        json={"dataset_id": ds_id},
        headers=auth_headers,
    )
    sess_id = created.json()["id"]

    # exhaust quota by rapid queries (mock always returns)
    for _ in range(15):
        resp = await client.post(
            f"/api/session/{sess_id}/query",
            json={"question": "test"},
            headers=auth_headers,
        )
        if resp.status_code == 403:
            break
    else:
        resp = await client.post(
            f"/api/session/{sess_id}/query",
            json={"question": "test"},
            headers=auth_headers,
        )
    assert resp.status_code == 403
    assert "上限" in resp.json()["detail"]
