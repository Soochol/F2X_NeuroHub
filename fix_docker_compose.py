"""Fix docker-compose.yml - add networks section"""

# Read the original file
with open('docker-compose.yml', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if networks section already exists
if 'networks:' not in content:
    # Add networks section at the end
    networks_section = """
networks:
  f2x-network:
    driver: bridge
"""
    content = content.rstrip() + '\n' + networks_section
    
    # Write back
    with open('docker-compose.yml', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added networks section to docker-compose.yml")
else:
    print("⚠️  Networks section already exists")

# Verify
print("\nLast 10 lines of docker-compose.yml:")
with open('docker-compose.yml', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines[-10:]:
        print(line.rstrip())
