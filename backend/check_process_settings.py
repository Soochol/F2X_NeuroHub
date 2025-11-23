"""Check current process auto-print settings"""
from app.database import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text('SELECT id, process_number, process_name_en, auto_print_label, label_template_type FROM processes ORDER BY process_number'))

print('\n✅ Current Process Settings:')
print('=' * 80)
for row in result:
    auto_print = '✅ ON' if row[3] else '❌ OFF'
    label_type = row[4] or 'None'
    print(f'  {row[1]}. {row[2]:20s} | Auto Print: {auto_print:6s} | Label: {label_type}')

conn.close()
print('=' * 80)
