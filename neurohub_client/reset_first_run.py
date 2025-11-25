"""Reset first run flag for testing purposes."""
from utils.config import AppConfig

if __name__ == "__main__":
    config = AppConfig()
    print(f"Before: first_run_completed = {config.first_run_completed}")
    config.reset_first_run()
    print(f"After:  first_run_completed = {config.first_run_completed}")
    print("First run flag has been reset. Next app launch will require login.")
