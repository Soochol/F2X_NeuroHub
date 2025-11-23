"""
Migration script to add auto_print_label fields to processes table
"""
from app.database import engine
from sqlalchemy import text

def run_migration():
    conn = engine.connect()
    
    # Add auto_print_label column
    try:
        conn.execute(text('ALTER TABLE processes ADD COLUMN auto_print_label BOOLEAN DEFAULT 0'))
        print("✅ Added auto_print_label column")
    except Exception as e:
        print(f"⚠️  auto_print_label column might already exist: {e}")
    
    # Add label_template_type column
    try:
        conn.execute(text('ALTER TABLE processes ADD COLUMN label_template_type VARCHAR(50)'))
        print("✅ Added label_template_type column")
    except Exception as e:
        print(f"⚠️  label_template_type column might already exist: {e}")
    
    conn.commit()
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
