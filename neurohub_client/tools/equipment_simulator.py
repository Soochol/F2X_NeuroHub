"""
Equipment Simulator for testing TCP communication.

Simulates inspection/assembly equipment sending measurement data
to the PySide app via TCP socket.

Usage:
    python equipment_simulator.py [--host HOST] [--port PORT] [--result PASS|FAIL]

Examples:
    # Send PASS result with default measurements
    python equipment_simulator.py

    # Send FAIL result
    python equipment_simulator.py --result FAIL

    # Connect to specific host/port
    python equipment_simulator.py --host 192.168.1.100 --port 9000
"""

import argparse
import json
import random
import socket
import sys
from typing import Any, Dict


def generate_pass_data() -> Dict[str, Any]:
    """Generate sample PASS measurement data."""
    return {
        "result": "PASS",
        "measurements": [
            {
                "code": "VOLTAGE",
                "name": "전압",
                "value": round(random.uniform(11.9, 12.3), 2),
                "unit": "V",
                "spec": {"min": 11.8, "max": 12.4, "target": 12.0},
                "result": "PASS"
            },
            {
                "code": "CURRENT",
                "name": "전류",
                "value": round(random.uniform(2.1, 2.8), 2),
                "unit": "A",
                "spec": {"min": 2.0, "max": 3.0, "target": 2.5},
                "result": "PASS"
            },
            {
                "code": "RESISTANCE",
                "name": "저항",
                "value": round(random.uniform(4.6, 5.4), 2),
                "unit": "Ω",
                "spec": {"min": 4.5, "max": 5.5, "target": 5.0},
                "result": "PASS"
            },
            {
                "code": "TEMPERATURE",
                "name": "온도",
                "value": round(random.uniform(23, 27), 1),
                "unit": "°C",
                "spec": {"min": 20, "max": 30, "target": 25},
                "result": "PASS"
            }
        ],
        "defects": []
    }


def generate_fail_data() -> Dict[str, Any]:
    """Generate sample FAIL measurement data."""
    # One measurement exceeds spec
    failed_voltage = round(random.uniform(12.5, 13.5), 2)  # Exceeds max 12.4

    return {
        "result": "FAIL",
        "measurements": [
            {
                "code": "VOLTAGE",
                "name": "전압",
                "value": failed_voltage,
                "unit": "V",
                "spec": {"min": 11.8, "max": 12.4, "target": 12.0},
                "result": "FAIL"
            },
            {
                "code": "CURRENT",
                "name": "전류",
                "value": round(random.uniform(2.1, 2.8), 2),
                "unit": "A",
                "spec": {"min": 2.0, "max": 3.0, "target": 2.5},
                "result": "PASS"
            },
            {
                "code": "RESISTANCE",
                "name": "저항",
                "value": round(random.uniform(4.6, 5.4), 2),
                "unit": "Ω",
                "spec": {"min": 4.5, "max": 5.5, "target": 5.0},
                "result": "PASS"
            }
        ],
        "defects": [
            {
                "code": "VOLTAGE",
                "reason": "상한 초과"
            }
        ]
    }


def generate_assembly_data() -> Dict[str, Any]:
    """Generate sample assembly process measurement data."""
    return {
        "result": "PASS",
        "measurements": [
            {
                "code": "TORQUE_01",
                "name": "토크값 #1",
                "value": round(random.uniform(11, 14), 1),
                "unit": "Nm",
                "spec": {"min": 10.0, "max": 15.0, "target": 12.0},
                "result": "PASS"
            },
            {
                "code": "TORQUE_02",
                "name": "토크값 #2",
                "value": round(random.uniform(11, 14), 1),
                "unit": "Nm",
                "spec": {"min": 10.0, "max": 15.0, "target": 12.0},
                "result": "PASS"
            },
            {
                "code": "PRESS_FORCE",
                "name": "압입력",
                "value": round(random.uniform(850, 950), 0),
                "unit": "N",
                "spec": {"min": 800, "max": 1000, "target": 900},
                "result": "PASS"
            }
        ],
        "defects": []
    }


def send_data(host: str, port: int, data: Dict[str, Any], use_length_header: bool = True) -> bool:
    """Send measurement data to PySide app."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        sock.connect((host, port))

        json_str = json.dumps(data, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')

        if use_length_header:
            # Send length header (4 bytes, big-endian)
            length = len(json_bytes)
            sock.sendall(length.to_bytes(4, 'big'))

        # Send JSON data
        sock.sendall(json_bytes)

        # Receive response
        response = sock.recv(4096).decode('utf-8')
        print(f"Server response: {response}")

        sock.close()
        return True

    except ConnectionRefusedError:
        print(f"Error: Could not connect to {host}:{port}")
        print("Make sure the PySide app is running with TCP server enabled.")
        return False
    except socket.timeout:
        print("Error: Connection timed out")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def interactive_mode(host: str, port: int) -> None:
    """Run in interactive mode for testing."""
    print("\n" + "=" * 60)
    print("Equipment Simulator - Interactive Mode")
    print("=" * 60)
    print(f"Target: {host}:{port}")
    print("\nCommands:")
    print("  1. Send PASS (inspection)")
    print("  2. Send FAIL (inspection)")
    print("  3. Send PASS (assembly)")
    print("  4. Send custom JSON")
    print("  q. Quit")
    print("=" * 60)

    while True:
        choice = input("\nEnter command (1-4, q): ").strip().lower()

        if choice == 'q':
            print("Goodbye!")
            break
        elif choice == '1':
            print("\nSending PASS inspection data...")
            data = generate_pass_data()
            print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
            send_data(host, port, data)
        elif choice == '2':
            print("\nSending FAIL inspection data...")
            data = generate_fail_data()
            print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
            send_data(host, port, data)
        elif choice == '3':
            print("\nSending assembly data...")
            data = generate_assembly_data()
            print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
            send_data(host, port, data)
        elif choice == '4':
            print("\nEnter JSON (single line):")
            json_input = input()
            try:
                data = json.loads(json_input)
                send_data(host, port, data)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")
        else:
            print("Invalid command. Enter 1-4 or q.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Equipment Simulator for TCP testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python equipment_simulator.py                     # Interactive mode
  python equipment_simulator.py --result PASS       # Send PASS once
  python equipment_simulator.py --result FAIL       # Send FAIL once
  python equipment_simulator.py --type assembly     # Send assembly data
        """
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Target host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="Target port (default: 9000)"
    )
    parser.add_argument(
        "--result",
        choices=["PASS", "FAIL"],
        help="Send single result and exit"
    )
    parser.add_argument(
        "--type",
        choices=["inspection", "assembly"],
        default="inspection",
        help="Type of measurement data"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("Equipment Simulator")
    print(f"Target: {args.host}:{args.port}")
    print("=" * 60)

    if args.result:
        # Single send mode
        if args.result == "PASS":
            if args.type == "assembly":
                data = generate_assembly_data()
            else:
                data = generate_pass_data()
        else:
            data = generate_fail_data()

        print(f"\nSending {args.result} data ({args.type})...")
        print(f"Data:\n{json.dumps(data, indent=2, ensure_ascii=False)}")

        if send_data(args.host, args.port, data):
            print("\nData sent successfully!")
        else:
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode(args.host, args.port)


if __name__ == "__main__":
    main()
