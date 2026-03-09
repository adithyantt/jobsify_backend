#!/usr/bin/env python
"""Test script to identify issues in the backend code."""

import sys
import traceback

def test_imports():
    """Test all imports to find issues."""
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    errors = []
    
    # Test database import
    try:
        from app.database import Base, engine, get_db
        print("✓ app.database imported successfully")
    except Exception as e:
        errors.append(f"app.database: {e}")
        print(f"✗ app.database: {e}")
    
    # Test models
    try:
        from app.models.user import User
        print("✓ app.models.user imported successfully")
    except Exception as e:
        errors.append(f"app.models.user: {e}")
        print(f"✗ app.models.user: {e}")
    
    try:
        from app.models.job import Job, SavedJob
        print("✓ app.models.job imported successfully")
    except Exception as e:
        errors.append(f"app.models.job: {e}")
        print(f"✗ app.models.job: {e}")
    
    try:
        from app.models.workers import Worker
        print("✓ app.models.workers imported successfully")
    except Exception as e:
        errors.append(f"app.models.workers: {e}")
        print(f"✗ app.models.workers: {e}")
    
    try:
        from app.models.review import Review
        print("✓ app.models.review imported successfully")
    except Exception as e:
        errors.append(f"app.models.review: {e}")
        print(f"✗ app.models.review: {e}")
    
    try:
        from app.models.notification import Notification
        print("✓ app.models.notification imported successfully")
    except Exception as e:
        errors.append(f"app.models.notification: {e}")
        print(f"✗ app.models.notification: {e}")
    
    try:
        from app.models.report import Report
        print("✓ app.models.report imported successfully")
    except Exception as e:
        errors.append(f"app.models.report: {e}")
        print(f"✗ app.models.report: {e}")
    
    # Test schemas
    try:
        from app.schemas.user import UserCreate, UserLogin
        print("✓ app.schemas.user imported successfully")
    except Exception as e:
        errors.append(f"app.schemas.user: {e}")
        print(f"✗ app.schemas.user: {e}")
    
    try:
        from app.schemas.job import JobCreate, JobResponse
        print("✓ app.schemas.job imported successfully")
    except Exception as e:
        errors.append(f"app.schemas.job: {e}")
        print(f"✗ app.schemas.job: {e}")
    
    try:
        from app.schemas.workers import WorkerCreate, WorkerResponse
        print("✓ app.schemas.workers imported successfully")
    except Exception as e:
        errors.append(f"app.schemas.workers: {e}")
        print(f"✗ app.schemas.workers: {e}")
    
    try:
        from app.schemas.review import ReviewCreate, ReviewResponse
        print("✓ app.schemas.review imported successfully")
    except Exception as e:
        errors.append(f"app.schemas.review: {e}")
        print(f"✗ app.schemas.review: {e}")
    
    try:
        from app.schemas.report import ReportCreate, ReportResponse
        print("✓ app.schemas.report imported successfully")
    except Exception as e:
        errors.append(f"app.schemas.report: {e}")
        print(f"✗ app.schemas.report: {e}")
    
    # Test routers
    try:
        from app.routers import auth, jobs, workers, reports, reviews
        print("✓ app.routers (base) imported successfully")
    except Exception as e:
        errors.append(f"app.routers (base): {e}")
        print(f"✗ app.routers (base): {e}")
    
    try:
        from app.routers import admin_reports, admin_workers, notifications, admin
        print("✓ app.routers (admin) imported successfully")
    except Exception as e:
        errors.append(f"app.routers (admin): {e}")
        print(f"✗ app.routers (admin): {e}")
    
    # Test main app
    try:
        from app.main import app
        print("✓ app.main imported successfully")
    except Exception as e:
        errors.append(f"app.main: {e}")
        print(f"✗ app.main: {e}")
        traceback.print_exc()
    
    return errors


def test_database_tables():
    """Test database table creation."""
    print("\n" + "=" * 60)
    print("TESTING DATABASE TABLES")
    print("=" * 60)
    
    from app.database import engine, Base
    from app.models.user import User
    from app.models.job import Job, SavedJob
    from app.models.workers import Worker
    from app.models.review import Review
    from app.models.notification import Notification
    from app.models.report import Report
    
    # Get all tables
    tables = Base.metadata.tables.keys()
    print(f"Tables defined in Base.metadata: {list(tables)}")
    
    # Check each model
    models = [
        ("User", User),
        ("Job", Job),
        ("SavedJob", SavedJob),
        ("Worker", Worker),
        ("Review", Review),
        ("Notification", Notification),
        ("Report", Report),
    ]
    
    errors = []
    for model_name, model in models:
        table_name = model.__tablename__
        if table_name in tables:
            print(f"✓ {model_name} table exists")
        else:
            errors.append(f"{model_name} table missing")
            print(f"✗ {model_name} table MISSING")
    
    return errors


def test_api_routes():
    """Test API routes."""
    print("\n" + "=" * 60)
    print("TESTING API ROUTES")
    print("=" * 60)
    
    from app.main import app
    
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                routes.append(f"{method}: {route.path}")
    
    print(f"Total routes: {len(routes)}")
    
    # List important routes
    important_routes = [r for r in routes if any(x in r for x in ['/auth', '/jobs', '/workers', '/reviews', '/admin'])]
    print("\nImportant routes:")
    for r in important_routes[:30]:
        print(f"  {r}")
    
    return []


def main():
    print("TESTING JOBSIFY BACKEND")
    print("=" * 60)
    
    all_errors = []
    
    # Test imports
    errors = test_imports()
    all_errors.extend(errors)
    
    # Test database tables
    if not errors:
        errors = test_database_tables()
        all_errors.extend(errors)
    
    # Test API routes
    if not errors:
        errors = test_api_routes()
        all_errors.extend(errors)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if all_errors:
        print(f"Found {len(all_errors)} errors:")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    else:
        print("✓ All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
