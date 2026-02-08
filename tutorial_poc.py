#!/usr/bin/env python3
"""
Tutorial / PoC for TradingAgents HTTP API

This script demonstrates how to interact with the TradingAgents Docker container
via HTTP API.

Usage:
    python tutorial_poc.py
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:11360"

def test_health_check():
    """Test the health endpoint"""
    print("=" * 60)
    print("Testing Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to TradingAgents server.")
        print("Make sure the Docker container is running:")
        print("  ./invoke.sh")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_get_stock_info():
    """Test getting stock information"""
    print("\n" + "=" * 60)
    print("Testing Stock Information Retrieval")
    print("=" * 60)

    # Example: Get stock info for NVIDIA
    stock_symbol = "NVDA"
    print(f"Requesting information for {stock_symbol}...")

    # Note: The actual endpoint depends on the TradingAgents API
    # This is a placeholder showing how to structure the request
    try:
        response = requests.get(
            f"{BASE_URL}/api/stock/{stock_symbol}",
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to TradingAgents server.")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_trading_decision():
    """Test getting a trading decision"""
    print("\n" + "=" * 60)
    print("Testing Trading Decision")
    print("=" * 60)

    stock_symbol = "NVDA"
    period = "2024-05-10"
    print(f"Requesting trading decision for {stock_symbol} on {period}...")

    try:
        # POST request with stock symbol and date
        response = requests.post(
            f"{BASE_URL}/api/decision",
            json={"symbol": stock_symbol, "date": period},
            timeout=60
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to TradingAgents server.")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function to run all tests"""
    print("TradingAgents Docker Container API Tutorial/PoC")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)

    # Test health first
    if not test_health_check():
        print("\n" + "!" * 60)
        print("WARNING: Could not connect to TradingAgents server.")
        print("!" * 60)
        print("\nTo start the TradingAgents server:")
        print("1. Make sure Docker is running")
        print("2. Run: ./invoke.sh")
        print("3. Wait for the server to start")
        print("\nThen run this script again.")
        return 1

    # Run other tests
    test_get_stock_info()
    test_trading_decision()

    print("\n" + "=" * 60)
    print("Tutorial Complete")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    exit(main())
