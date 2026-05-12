"""Tests for dataset endpoints."""

import io

import pytest


@pytest.mark.asyncio
async def test_upload_csv(client, auth_headers):
    content = b"name,age,city\nAlice,30,Beijing\nBob,25,Shanghai\n"
    resp = await client.post(
        "/api/dataset/upload",
        files={"file": ("test.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "test"
    assert data["row_count"] == 2
    assert len(data["columns_meta"]) == 3


@pytest.mark.asyncio
async def test_upload_invalid_extension(client, auth_headers):
    content = b"some content"
    resp = await client.post(
        "/api/dataset/upload",
        files={"file": ("test.pdf", io.BytesIO(content), "application/pdf")},
        headers=auth_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_datasets(client, auth_headers):
    # upload a dataset first
    content = b"col1,col2\n1,2\n3,4\n"
    await client.post(
        "/api/dataset/upload",
        files={"file": ("list_test.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    resp = await client.get("/api/dataset/list", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_dataset_detail(client, auth_headers):
    # upload first
    content = b"x,y\n1,2\n3,4\n5,6\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("detail.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]

    resp = await client.get(f"/api/dataset/{ds_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == ds_id
    assert data["row_count"] == 3


@pytest.mark.asyncio
async def test_preview_dataset(client, auth_headers):
    content = b"a,b\n1,2\n3,4\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("preview.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]

    resp = await client.get(f"/api/dataset/{ds_id}/preview", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "columns" in data
    assert "rows" in data


@pytest.mark.asyncio
async def test_delete_dataset(client, auth_headers):
    content = b"x,y\n1,2\n"
    upload = await client.post(
        "/api/dataset/upload",
        files={"file": ("del.csv", io.BytesIO(content), "text/csv")},
        headers=auth_headers,
    )
    ds_id = upload.json()["id"]

    resp = await client.delete(f"/api/dataset/{ds_id}", headers=auth_headers)
    assert resp.status_code == 204

    # verify deleted
    resp = await client.get(f"/api/dataset/{ds_id}", headers=auth_headers)
    assert resp.status_code == 404
