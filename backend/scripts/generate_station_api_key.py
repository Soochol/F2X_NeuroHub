#!/usr/bin/env python3
"""
Generate Station API key for sequence pull authentication.

Usage:
    python scripts/generate_station_api_key.py STATION-01
    python scripts/generate_station_api_key.py STATION-01 --days 365
    python scripts/generate_station_api_key.py STATION-01 --days 30 --output /path/to/key.txt

The generated API key should be configured in the Station Service's
environment or configuration file as STATION_API_KEY.
"""

import argparse
import sys
import os

# Add parent directory to path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import create_station_api_key, decode_access_token
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Generate Station API key for sequence pull authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s STATION-01
    %(prog)s STATION-01 --days 365
    %(prog)s STATION-01 --days 30 --output /etc/station/api_key.txt

The API key should be used in X-API-Key header when calling:
    POST /api/v1/sequences/{name}/pull
        """,
    )
    parser.add_argument(
        "station_id",
        help="Station identifier (e.g., STATION-01, LINE-A-STATION-1)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Expiration in days (default: 365)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (prints to stdout if not specified)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the generated key by decoding it",
    )

    args = parser.parse_args()

    # Generate API key
    api_key = create_station_api_key(args.station_id, expires_days=args.days)

    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(api_key)
        print(f"API key written to: {args.output}")
        print(f"Station ID: {args.station_id}")
        print(f"Expires in: {args.days} days")
    else:
        print("=" * 70)
        print("STATION API KEY GENERATED")
        print("=" * 70)
        print(f"Station ID: {args.station_id}")
        print(f"Expires in: {args.days} days")
        print("-" * 70)
        print("API Key:")
        print(api_key)
        print("-" * 70)
        print("\nUsage in Station Service configuration:")
        print("  STATION_API_KEY=" + api_key[:50] + "...")
        print("\nUsage in HTTP request:")
        print("  curl -X POST \\")
        print("    -H 'X-API-Key: <api_key>' \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{\"station_id\": \"" + args.station_id + "\"}' \\")
        print("    http://localhost:8000/api/v1/sequences/psa_sensor_test/pull")
        print("=" * 70)

    # Verify if requested
    if args.verify:
        print("\nVerifying generated key...")
        payload = decode_access_token(api_key)
        if payload:
            print("Verification: SUCCESS")
            print(f"  type: {payload.get('type')}")
            print(f"  station_id: {payload.get('station_id')}")
            exp = payload.get("exp")
            if exp:
                exp_dt = datetime.utcfromtimestamp(exp)
                print(f"  expires: {exp_dt.isoformat()}Z")
        else:
            print("Verification: FAILED - Could not decode token")
            sys.exit(1)


if __name__ == "__main__":
    main()
