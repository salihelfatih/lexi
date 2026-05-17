#!/usr/bin/env python3
"""Validate Lexi setup and configuration."""

import os
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

def check_file(path: str, description: str) -> bool:
    """Check if file exists."""
    if Path(path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - MISSING: {path}")
        return False

def check_directory(path: str, description: str) -> bool:
    """Check if directory exists."""
    if Path(path).is_dir():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - MISSING: {path}")
        return False

def main():
    """Run validation checks."""
    # Ensure relative checks resolve against repository root, not caller cwd.
    os.chdir(REPO_ROOT)

    print("🔍 Validating Lexi Setup...\n")

    checks = []

    # Core files
    print("📁 Core Files:")
    checks.append(check_file("pyproject.toml", "Poetry configuration"))
    checks.append(check_file("backend/requirements.txt", "Requirements file"))
    checks.append(check_file(".env.example", "Environment template"))
    checks.append(check_file("docker-compose.yml", "Docker Compose"))
    checks.append(check_file("backend/Makefile", "Makefile"))
    checks.append(check_file("backend/alembic.ini", "Alembic config"))

    print("\n📦 Application Structure:")
    checks.append(check_directory("backend", "Main package"))
    checks.append(check_file("backend/__init__.py", "Package init"))
    checks.append(check_file("backend/main.py", "FastAPI app"))
    checks.append(check_file("backend/config.py", "Configuration"))
    checks.append(check_file("backend/models.py", "Database models"))
    checks.append(check_file("backend/schemas.py", "Pydantic schemas"))
    checks.append(check_file("backend/database.py", "Database setup"))
    checks.append(check_file("backend/celery_app.py", "Celery config"))

    print("\n🌐 API Layer:")
    checks.append(check_directory("backend/api", "API package"))
    checks.append(check_directory("backend/api/v1", "API v1"))
    checks.append(check_file("backend/api/v1/documents.py", "Documents endpoints"))
    checks.append(check_file("backend/api/v1/jobs.py", "Jobs endpoints"))

    print("\n⚙️ Services:")
    checks.append(check_directory("backend/services", "Services package"))
    checks.append(check_file("backend/services/upload_service.py", "Upload service"))
    checks.append(check_file("backend/services/consent_service.py", "Consent service"))
    checks.append(check_file("backend/services/extraction_service.py", "Extraction service"))
    checks.append(check_file("backend/services/classification_service.py", "Classification service"))
    checks.append(check_file("backend/services/clause_service.py", "Clause service"))
    checks.append(check_file("backend/services/metadata_service.py", "Metadata service"))
    checks.append(check_file("backend/services/storage_service.py", "Storage service"))
    checks.append(check_file("backend/services/job_service.py", "Job service"))
    checks.append(check_file("backend/services/results_service.py", "Results service"))

    print("\n🔄 Tasks:")
    checks.append(check_directory("backend/tasks", "Tasks package"))
    checks.append(check_file("backend/tasks/processing.py", "Processing tasks"))

    print("\n🗄️ Database:")
    checks.append(check_directory("backend/alembic", "Alembic directory"))
    checks.append(check_directory("backend/alembic/versions", "Migrations directory"))
    checks.append(check_file("backend/alembic/versions/001_initial_schema.py", "Initial migration"))

    print("\n🧪 Tests:")
    checks.append(check_directory("backend/tests", "Tests directory"))
    checks.append(check_file("backend/tests/test_api.py", "API tests"))

    print("\n🛠️ Onboarding Scripts:")
    checks.append(check_directory("scripts/onboarding", "Onboarding scripts directory"))
    checks.append(check_file("scripts/onboarding/setup-dev.sh", "Setup script"))
    checks.append(check_file("scripts/onboarding/start-dev.sh", "Start script"))
    checks.append(check_file("scripts/onboarding/check-health.sh", "Health check script"))

    print("\n📚 Documentation:")
    checks.append(check_file("README.md", "README"))
    checks.append(check_file("docs/technical/SETUP.md", "Setup guide"))
    checks.append(check_file("docs/technical/CHANGELOG.md", "Implementation changelog"))

    # Summary
    total = len(checks)
    passed = sum(checks)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("✅ All checks passed! Setup is complete.")
        return 0
    else:
        print(f"⚠️  {total - passed} checks failed. Please review above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
