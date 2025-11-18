"""Validate all imports for the PySide6 application"""

import sys
import importlib

def test_import(module_name):
    """Test importing a module"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"⚠ {module_name}: {type(e).__name__}: {e}")
        return False

def main():
    """Validate all critical imports"""
    print("=" * 60)
    print("F2X NeuroHub MES - Import Validation")
    print("=" * 60)
    print()

    # Core modules
    print("Core Modules:")
    core_modules = [
        'config',
        'main',
    ]
    core_results = [test_import(m) for m in core_modules]
    print()

    # Services
    print("Services:")
    service_modules = [
        'services.api_client',
        'services.auth_service',
        'services.process_service',
        'services.file_watcher_service',
    ]
    service_results = [test_import(m) for m in service_modules]
    print()

    # ViewModels
    print("ViewModels:")
    viewmodel_modules = [
        'viewmodels.app_state',
        'viewmodels.main_viewmodel',
    ]
    viewmodel_results = [test_import(m) for m in viewmodel_modules]
    print()

    # Views
    print("Views:")
    view_modules = [
        'views.login_dialog',
        'views.main_window',
    ]
    view_results = [test_import(m) for m in view_modules]
    print()

    # Utils
    print("Utils:")
    util_modules = [
        'utils.logger',
    ]
    util_results = [test_import(m) for m in util_modules]
    print()

    # Summary
    all_results = (
        core_results +
        service_results +
        viewmodel_results +
        view_results +
        util_results
    )
    total = len(all_results)
    passed = sum(all_results)

    print("=" * 60)
    print(f"Results: {passed}/{total} imports successful")
    print("=" * 60)

    if passed == total:
        print("✓ All imports validated successfully!")
        return 0
    else:
        print(f"✗ {total - passed} import(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
