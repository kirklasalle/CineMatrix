import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_examples():
    response = client.get("/examples")
    assert response.status_code == 200
    examples = response.json()
    assert len(examples) == 27
    
    # Check category counts
    formats = [e for e in examples if e["category"] == "formats"]
    engines = [e for e in examples if e["category"] == "engines"]
    genres = [e for e in examples if e["category"] == "genres"]
    spectrum = [e for e in examples if e["category"] == "spectrum"]
    
    assert len(formats) == 9
    assert len(engines) == 6
    assert len(genres) == 9
    assert len(spectrum) == 3


def test_list_examples_filtered():
    response = client.get("/examples?category=engines")
    assert response.status_code == 200
    engines = response.json()
    assert len(engines) == 6
    assert all(e["category"] == "engines" for e in engines)


def test_get_example_preview():
    response = client.get("/examples/engines/10_story_doctor_15_beats.fountain")
    assert response.status_code == 200
    data = response.json()
    assert "THE ALCHEMIST'S HORIZON" in data["content"]
    assert data["format"] == "fountain"


def test_create_project_with_example():
    payload = {
        "category": "engines",
        "filename": "10_story_doctor_15_beats.fountain"
    }
    response = client.post("/projects/create-with-example", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["scene_count"] == 15
    assert "The Alchemist's Horizon" in data["title"]
    assert "project_id" in data


def test_load_example_into_existing_project():
    # 1. Create a blank project
    proj_resp = client.post("/projects", json={"name": "Blank Project", "description": "Test"})
    assert proj_resp.status_code == 200
    proj_id = proj_resp.json()["id"]
    
    # 2. Load example into it
    payload = {
        "category": "genres",
        "filename": "16_sci_fi_cyberpunk_neo_noir.fountain"
    }
    load_resp = client.post(f"/projects/{proj_id}/load-example", json=payload)
    assert load_resp.status_code == 200
    data = load_resp.json()
    assert data["status"] == "success"
    assert data["project_id"] == proj_id
    assert data["scene_count"] >= 1
    assert data.get("frame_count", 0) >= 1

    # 3. Verify frames and images were auto-generated
    proj_detail = client.get(f"/projects/{proj_id}")
    assert proj_detail.status_code == 200
    proj_data = proj_detail.json()
    assert len(proj_data["frames"]) >= 1
    first_frame = proj_data["frames"][0]
    assert first_frame["image_path"] is not None
    assert "https://" in first_frame["image_path"]


def test_batch_generate_images_endpoint():
    # Create project with example
    payload = {
        "category": "genres",
        "filename": "16_sci_fi_cyberpunk_neo_noir.fountain"
    }
    create_resp = client.post("/projects/create-with-example", json=payload)
    assert create_resp.status_code == 200
    proj_id = create_resp.json()["project_id"]

    # Trigger batch image render
    batch_resp = client.post(f"/projects/{proj_id}/generate-all-images", json={"force": True})
    assert batch_resp.status_code == 200
    batch_data = batch_resp.json()
    assert batch_data["status"] == "success"
    assert batch_data["rendered_count"] >= 1
    assert len(batch_data["frames"]) >= 1


def test_frame_generate_image_and_animatic():
    # Create project with example
    payload = {
        "category": "spectrum",
        "filename": "25_micro_scene_1min.fountain"
    }
    create_resp = client.post("/projects/create-with-example", json=payload)
    assert create_resp.status_code == 200
    proj_id = create_resp.json()["project_id"]

    proj_detail = client.get(f"/projects/{proj_id}")
    frames = proj_detail.json()["frames"]
    assert len(frames) >= 1
    target_frame = frames[0]

    # Test single frame image generation
    img_resp = client.post(f"/frames/{target_frame['id']}/generate-image")
    assert img_resp.status_code == 200
    img_data = img_resp.json()
    assert img_data["status"] == "success"
    assert "image_url" in img_data

    # Test single frame animatic generation
    anim_resp = client.post(
        f"/frames/{target_frame['id']}/generate-animatic",
        json={"motion_preset": "dolly_in", "duration": 2.0}
    )
    assert anim_resp.status_code == 200
    anim_data = anim_resp.json()
    assert anim_data["status"] == "success"
    assert "video_url" in anim_data

