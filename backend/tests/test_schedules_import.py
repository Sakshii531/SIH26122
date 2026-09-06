from __future__ import annotations

import io
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
import openpyxl

from app.main import app

client = TestClient(app)


def test_import_valid_csv():
    """Test importing a valid CSV schedule file."""
    csv_content = (
        "Activity ID,Activity Name,WBS,Discipline,Activity Level,Planned Start,Planned End,Status\n"
        "ACT-101,Site Preparation,1.1,Civil,L5,2026-01-01,2026-01-15,Not Started\n"
        "ACT-102,Foundation Pouring,1.2,Civil,L6,2026-01-16,2026-02-01,In Progress\n"
    )
    files = {"file": ("schedule.csv", csv_content.encode("utf-8"), "text/csv")}
    response = client.post("/api/v1/schedules/import", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 2
    assert data["valid_count"] == 2
    assert data["rejected_count"] == 0
    assert len(data["activities"]) == 2
    assert data["activities"][0]["activity_code"] == "ACT-101"
    assert data["activities"][0]["discipline"] == "Civil"
    assert data["activities"][1]["level"] == "L6"


def test_import_valid_xlsx():
    """Test importing a valid Excel (.xlsx) schedule file."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Activity ID", "Activity Name", "WBS", "Discipline", "Activity Level", "Planned Start", "Planned End", "Status"])
    ws.append(["ACT-201", "Piping Installation", "2.1", "Piping", "L5", "2026-03-01", "2026-03-30", "Not Started"])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    files = {"file": ("schedule.xlsx", output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    project_id = str(uuid4())
    data_form = {"project_id": project_id}

    response = client.post("/api/v1/schedules/import", files=files, data=data_form)
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 1
    assert data["valid_count"] == 1
    assert data["rejected_count"] == 0
    assert data["activities"][0]["activity_code"] == "ACT-201"
    assert data["activities"][0]["project_id"] == project_id


def test_import_unsupported_file_format():
    """Test uploading an unsupported file format returns 400 Bad Request."""
    files = {"file": ("document.txt", b"Activity ID,Activity Name\nACT-1,Name", "text/plain")}
    response = client.post("/api/v1/schedules/import", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported file type" in data["detail"]


def test_import_missing_required_columns():
    """Test missing required columns returns 400 Bad Request."""
    csv_content = (
        "Activity ID,Discipline,Planned Start\n"
        "ACT-101,Civil,2026-01-01\n"
    )
    files = {"file": ("schedule.csv", csv_content.encode("utf-8"), "text/csv")}
    response = client.post("/api/v1/schedules/import", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "Missing required columns" in data["detail"]


def test_import_invalid_row_data():
    """Test importing file with invalid row data produces rejection counts and error messages."""
    csv_content = (
        "Activity ID,Activity Name,WBS,Discipline,Planned Start,Planned End,Status\n"
        "ACT-301,Cable Pulling,3.1,Electrical,2026-04-01,2026-04-15,Not Started\n"
        "ACT-302,Transformer Testing,3.2,Electrical,INVALID-DATE,2026-04-30,Not Started\n"
    )
    files = {"file": ("schedule.csv", csv_content.encode("utf-8"), "text/csv")}
    response = client.post("/api/v1/schedules/import", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 2
    assert data["valid_count"] == 1
    assert data["rejected_count"] == 1
    assert len(data["validation_errors"]) == 1
    assert data["validation_errors"][0]["row_number"] == 3
    assert data["validation_errors"][0]["activity_code"] == "ACT-302"


def test_import_excel_with_missing_required_cell_values():
    """Test importing Excel sheet where a row has empty cells (None) for mandatory fields."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Activity ID", "Activity Name", "WBS", "Discipline"])
    # Row 2: Valid
    ws.append(["ACT-401", "Concrete Pouring", "4.1", "Civil"])
    # Row 3: Missing Discipline (None cell)
    ws.append(["ACT-402", "Pipelining", "4.2", None])
    # Row 4: Missing Activity ID (None cell)
    ws.append([None, "Cable Laying", "4.3", "Electrical"])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    files = {"file": ("schedule.xlsx", output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = client.post("/api/v1/schedules/import", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3
    assert data["valid_count"] == 1
    assert data["rejected_count"] == 2
    assert len(data["validation_errors"]) == 2

    # Verify Row 3 error (Discipline is required)
    err_row3 = next(e for e in data["validation_errors"] if e["row_number"] == 3)
    assert err_row3["activity_code"] == "ACT-402"
    assert "Discipline is required" in err_row3["errors"][0]

    # Verify Row 4 error (Activity ID is required)
    err_row4 = next(e for e in data["validation_errors"] if e["row_number"] == 4)
    assert err_row4["activity_code"] is None
    assert "Activity ID is required" in err_row4["errors"][0]
