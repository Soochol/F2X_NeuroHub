try:
    from app.services.process_service import process_service
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
except IndentationError as e:
    print(f"IndentationError: {e}")
