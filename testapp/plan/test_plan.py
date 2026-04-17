import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
import pandas as pd
from fastapi import HTTPException, UploadFile
from app.service.plan_service import PlanService


@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def plan_service(mock_repo):
    return PlanService(plan_repo=mock_repo)

def create_mock_excel(data: list, columns: list):
    df = pd.DataFrame(data, columns=columns)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


def test_import_plans_success(plan_service, mock_repo):
    mock_repo.get_category_by_name.return_value = MagicMock(id=1)
    mock_repo.check_plan_exists.return_value = None

    excel_data = [["01.05.2021", "issuance", 10000]]
    excel_file = create_mock_excel(excel_data, ['period', 'category_name', 'sum'])

    upload_file = MagicMock(spec=UploadFile)
    upload_file.file = excel_file

    result = plan_service.import_plans_from_excel(upload_file)

    assert result["status"] == "success"
    mock_repo.create_plan.assert_called_once()
    mock_repo.commit.assert_called_once()


def test_import_plans_missing_columns(plan_service):
    excel_file = create_mock_excel([["01.05.2021", "cat"]], ['period', 'category_name'])
    upload_file = MagicMock(spec=UploadFile)
    upload_file.file = excel_file

    with pytest.raises(HTTPException) as exc:
        plan_service.import_plans_from_excel(upload_file)

    assert exc.value.status_code == 400
    assert "Missing required columns" in exc.value.detail


def test_import_plans_invalid_date_not_first_day(plan_service, mock_repo):
    excel_file = create_mock_excel([["10.05.2021", "issuance", 500]], ['period', 'category_name', 'sum'])
    upload_file = MagicMock(spec=UploadFile)
    upload_file.file = excel_file

    with pytest.raises(HTTPException) as exc:
        plan_service.import_plans_from_excel(upload_file)

    assert "Date must be begin of first day month" in exc.value.detail


def test_import_plans_category_not_found(plan_service, mock_repo):
    mock_repo.get_category_by_name.return_value = None

    excel_file = create_mock_excel([["01.01.2021", "unknown", 100]], ['period', 'category_name', 'sum'])
    upload_file = MagicMock(spec=UploadFile)
    upload_file.file = excel_file

    with pytest.raises(HTTPException) as exc:
        plan_service.import_plans_from_excel(upload_file)

    assert "Category 'unknown' not found" in exc.value.detail
    mock_repo.rollback.assert_called_once()


def test_import_plans_already_exists(plan_service, mock_repo):
    mock_repo.get_category_by_name.return_value = MagicMock(id=1)
    mock_repo.check_plan_exists.return_value = MagicMock()

    excel_file = create_mock_excel([["01.01.2021", "issuance", 100]], ['period', 'category_name', 'sum'])
    upload_file = MagicMock(spec=UploadFile)
    upload_file.file = excel_file

    with pytest.raises(HTTPException) as exc:
        plan_service.import_plans_from_excel(upload_file)

    assert "already exists" in exc.value.detail