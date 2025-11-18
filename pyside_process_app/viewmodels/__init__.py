"""
ViewModels - Business logic layer between views and services

This module provides ViewModel classes that implement the MVVM pattern:
- AppState: Global application state management (Singleton)
- MainViewModel: Main window business logic
- ProcessViewModel: Process-specific business logic

ViewModels coordinate between services (data layer) and views (UI layer),
handling business logic, data transformation, and state management.
"""

from .app_state import AppState
from .main_viewmodel import MainViewModel
from .process_viewmodel import ProcessViewModel

__all__ = ['AppState', 'MainViewModel', 'ProcessViewModel']