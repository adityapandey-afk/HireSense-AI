import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def test_jobs_and_applications_flow(client, recruiter_token, candidate_token):
    # 1. Create a Job (Recruiter)
    headers_rec = {"Authorization": f"Bearer {recruiter_token}"}
    job_payload = {
        "title": "Backend Python Engineer",
        "company": "FastAPI Inc",
        "description": "Must know Python, FastAPI, and PostgreSQL.",
        "required_skills": "Python, FastAPI, SQL"
    }
    resp = client.post("/jobs/", json=job_payload, headers=headers_rec)
    assert resp.status_code == 201
    job_id = resp.json()["job_id"]
    
    # 2. List Jobs (Candidate)
    headers_cand = {"Authorization": f"Bearer {candidate_token}"}
    resp = client.get("/jobs/", headers=headers_cand)
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) > 0
    assert jobs[0]["id"] == job_id
    
    # 3. Match resume against Job (Candidate)
    import io
    fake_file = io.BytesIO(b"%PDF-1.4 ... artificial content ... Python and FastAPI skills ...")
    files = {"file": ("resume.pdf", fake_file, "application/pdf")}
    
    resp = client.post(
        f"/rank/candidate?job_id={job_id}",
        files=files,
        headers=headers_cand
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert "match_id" in res_data
    match_id = res_data["match_id"]
    assert match_id is not None
    
    # 4. View candidate applications
    resp = client.get("/candidate/applications", headers=headers_cand)
    assert resp.status_code == 200
    apps = resp.json()
    assert len(apps) == 1
    assert apps[0]["match_id"] == match_id
    assert apps[0]["status"] == "pending"
    
    # 5. View recruiter applications list
    resp = client.get(f"/recruiter/jobs/{job_id}/applications", headers=headers_rec)
    assert resp.status_code == 200
    rec_apps = resp.json()
    assert len(rec_apps) == 1
    assert rec_apps[0]["match_id"] == match_id
    
    # 6. Recruiter updates status
    resp = client.post(f"/recruiter/applications/{match_id}/status?status=shortlist", headers=headers_rec)
    assert resp.status_code == 200
    assert resp.json()["status"] == "shortlist"
    
    # 7. Candidate checks updated status
    resp = client.get("/candidate/applications", headers=headers_cand)
    assert resp.status_code == 200
    apps = resp.json()
    assert apps[0]["status"] == "shortlist"
