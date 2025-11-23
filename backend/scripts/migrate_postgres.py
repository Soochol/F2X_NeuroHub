import psycopg2
import sys

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "f2x_neurohub_mes"
DB_USER = "postgres"
DB_PASSWORD = "password"

def migrate():
    print(f"Connecting to database: {DB_NAME} at {DB_HOST}:{DB_PORT}")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        sys.exit(1)

    # Add parent_spring_lot column
    print("Adding parent_spring_lot column...")
    try:
        cursor.execute("ALTER TABLE lots ADD COLUMN parent_spring_lot VARCHAR(50);")
        print("Successfully added parent_spring_lot")
    except psycopg2.errors.DuplicateColumn:
        print("Column parent_spring_lot already exists")
    except Exception as e:
        print(f"Error adding parent_spring_lot: {e}")

    # Add sma_spring_lot column
    print("Adding sma_spring_lot column...")
    try:
        cursor.execute("ALTER TABLE lots ADD COLUMN sma_spring_lot VARCHAR(50);")
        print("Successfully added sma_spring_lot")
    except psycopg2.errors.DuplicateColumn:
        print("Column sma_spring_lot already exists")
    except Exception as e:
        print(f"Error adding sma_spring_lot: {e}")

    # Check if product_model_id=1 exists (for testing)
    print("Checking for product_model_id=1...")
    try:
        cursor.execute("SELECT id FROM product_models WHERE id = 1;")
        if cursor.fetchone():
            print("ProductModel ID 1 exists.")
        else:
            print("ProductModel ID 1 does NOT exist. Creating it...")
            # Create a dummy product model if missing
            cursor.execute("""
                INSERT INTO product_models (id, model_code, model_name, status, created_at, updated_at)
                VALUES (1, 'TEST-MODEL', 'Test Model', 'ACTIVE', NOW(), NOW())
                ON CONFLICT (id) DO NOTHING;
            """)
            print("Created ProductModel ID 1.")
            
            # Also check production_line_id=1
            cursor.execute("SELECT id FROM production_lines WHERE id = 1;")
            if not cursor.fetchone():
                print("ProductionLine ID 1 does NOT exist. Creating it...")
                cursor.execute("""
                    INSERT INTO production_lines (id, line_code, line_name, is_active, created_at, updated_at)
                    VALUES (1, 'KR01', 'Test Line', TRUE, NOW(), NOW())
                    ON CONFLICT (id) DO NOTHING;
                """)
                print("Created ProductionLine ID 1.")

    except Exception as e:
        print(f"Error checking/creating test data: {e}")

    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
