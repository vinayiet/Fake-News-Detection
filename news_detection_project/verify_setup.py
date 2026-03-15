#!/usr/bin/env python

import sys
import os
from pathlib import Path

def check_python_version():
    version = sys.version_info
    required = (3, 8)
    
    if version[:2] >= required:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Need 3.8 or higher")
        return False

def check_directory_structure():
    project_root = Path(__file__).parent
    required_dirs = [
        project_root / "backend",
        project_root / "frontend",
        project_root / "data",
        project_root / "models"
    ]
    
    all_ok = True
    for directory in required_dirs:
        if directory.exists():
            print(f"✅ Directory {directory.name}/ - OK")
        else:
            print(f"❌ Directory {directory.name}/ - MISSING")
            all_ok = False
    
    return all_ok

def check_files():
    project_root = Path(__file__).parent
    required_files = [
        project_root / "backend" / "main.py",
        project_root / "backend" / "train_model.py",
        project_root / "backend" / "config.py",
        project_root / "frontend" / "app.py",
        project_root / "requirements.txt",
        project_root / "README.md",
    ]
    
    all_ok = True
    for file in required_files:
        if file.exists():
            print(f"✅ File {file.name} - OK")
        else:
            print(f"❌ File {file.name} - MISSING")
            all_ok = False
    
    return all_ok

def check_packages():
    required_packages = [
        'fastapi',
        'uvicorn',
        'streamlit',
        'pandas',
        'sklearn',
        'requests',
        'plotly'
    ]
    
    print("\n📦 Checking installed packages...")
    all_ok = True
    
    for package in required_packages:
        try:
            __import__(package if package != 'sklearn' else 'sklearn')
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - NOT installed")
            all_ok = False
    
    return all_ok

def check_data_files():
    """Check if data files exist"""
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    
    print("\n📊 Checking data files...")
    
    fake_csv = data_dir / "Fake.csv"
    true_csv = data_dir / "True.csv"
    
    all_ok = True
    
    if fake_csv.exists():
        size_mb = fake_csv.stat().st_size / (1024 * 1024)
        print(f"✅ Fake.csv - Found ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  Fake.csv - NOT found (required for training)")
        all_ok = False
    
    if true_csv.exists():
        size_mb = true_csv.stat().st_size / (1024 * 1024)
        print(f"✅ True.csv - Found ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  True.csv - NOT found (required for training)")
        all_ok = False
    
    return all_ok

def check_models():
    """Check if trained models exist"""
    project_root = Path(__file__).parent
    models_dir = project_root / "models"
    
    print("\n🤖 Checking trained models...")
    
    model_file = models_dir / "news_detection_model.pkl"
    vectorizer_file = models_dir / "tfidf_vectorizer.pkl"
    
    model_exists = model_file.exists()
    vectorizer_exists = vectorizer_file.exists()
    
    if model_exists:
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print(f"✅ Model file - Found ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  Model file - NOT found (run training first)")
    
    if vectorizer_exists:
        size_mb = vectorizer_file.stat().st_size / (1024 * 1024)
        print(f"✅ Vectorizer file - Found ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  Vectorizer file - NOT found (run training first)")
    
    return model_exists and vectorizer_exists

def check_virtual_env():
    """Check if running in virtual environment"""
    print("\n🔒 Checking virtual environment...")
    
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print(f"✅ Virtual environment active")
        print(f"   Python: {sys.executable}")
        return True
    else:
        print(f"⚠️  NOT in virtual environment")
        print(f"   Current Python: {sys.executable}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("🔍 Fake News Detection System - Verification Script")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_files),
        ("Virtual Environment", check_virtual_env),
        ("Installed Packages", check_packages),
        ("Data Files", check_data_files),
        ("Trained Models", check_models),
    ]
    
    results = {}
    
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error checking {name}: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Verification Summary:")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "⚠️  PARTIAL/FAIL"
        print(f"{status} - {name}")
    
    all_critical = all([
        results["Python Version"],
        results["Directory Structure"],
        results["Required Files"],
        results["Installed Packages"],
    ])
    
    print("\n" + "=" * 60)
    
    if all_critical:
        print("✅ Setup looks good! Ready to proceed.")
        print("\n📝 Next steps:")
        print("1. Place Fake.csv and True.csv in data/ folder")
        print("2. Run: python backend/train_model.py")
        print("3. Run: python -m uvicorn backend.main:app --reload")
        print("4. Run: streamlit run frontend/app.py")
        return 0
    else:
        print("❌ Some critical checks failed. Please fix them first.")
        print("\n💡 Run setup:")
        print("  ./setup.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())
