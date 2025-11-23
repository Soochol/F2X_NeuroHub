"""
Zebra Printer Test Script
Test printing to network printer at 192.168.35.79
"""
import socket

# Printer configuration
PRINTER_IP = "192.168.35.79"
PRINTER_PORT = 9100  # Standard RAW printing port for Zebra printers

# ZPL test label
zpl_test_label = """
^XA
^FO50,50^ADN,36,20^FDTest Print^FS
^FO50,100^ADN,24,12^FDZebra ZT231-203dpi^FS
^FO50,140^ADN,24,12^FDIP: 192.168.35.79^FS
^FO50,180^GB700,3,3^FS
^FO50,200^ADN,18,10^FDDate/Time Test^FS
^FO50,230^ADN,18,10^FDConnection: SUCCESS^FS
^FO50,280^BCN,100,Y,N,N^FDTEST123456^FS
^XZ
"""

def test_printer_connection():
    """Test connection to printer"""
    print(f"Testing connection to {PRINTER_IP}:{PRINTER_PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((PRINTER_IP, PRINTER_PORT))
        print("✅ Connection successful!")
        sock.close()
        return True
    except socket.timeout:
        print("❌ Connection timeout - Printer not responding")
        return False
    except socket.error as e:
        print(f"❌ Connection failed: {e}")
        return False

def send_zpl_to_printer(zpl_code):
    """Send ZPL code to printer"""
    print(f"\nSending ZPL to printer at {PRINTER_IP}:{PRINTER_PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((PRINTER_IP, PRINTER_PORT))
        
        # Send ZPL code
        sock.send(zpl_code.encode('utf-8'))
        print("✅ ZPL sent successfully!")
        
        sock.close()
        print("✅ Print job completed!")
        return True
    except Exception as e:
        print(f"❌ Print failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Zebra Printer Test - ZT231-203dpi")
    print("=" * 60)
    
    # Test connection
    if test_printer_connection():
        print("\n" + "=" * 60)
        print("Sending test label...")
        print("=" * 60)
        
        # Send test label
        if send_zpl_to_printer(zpl_test_label):
            print("\n✅ Test label should be printing now!")
            print("\nLabel contents:")
            print("  - Title: 'Test Print'")
            print("  - Printer model: ZT231-203dpi")
            print("  - IP address")
            print("  - Barcode: TEST123456")
        else:
            print("\n❌ Failed to send print job")
    else:
        print("\n❌ Cannot connect to printer")
        print("\nTroubleshooting:")
        print("  1. Check if printer is powered on")
        print("  2. Verify IP address: 192.168.35.79")
        print("  3. Check network connectivity")
        print("  4. Ensure port 9100 is not blocked by firewall")
