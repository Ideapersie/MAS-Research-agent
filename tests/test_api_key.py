"""
Test script to verify OpenRouter API key is valid.
Run: python test_api_key.py
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_api_key():
    """Test if OpenRouter API key is valid."""
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("[ERROR] No API key found in .env file")
        print("Make sure you have:")
        print("  OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        return False

    print(f"[INFO] Testing API key: {api_key[:20]}...{api_key[-10:]}")
    print("[INFO] Making test request to OpenRouter...")

    # Test with a simple request
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",  # Optional
    }

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "user", "content": "Say 'test successful' if you receive this."}
        ],
        "max_tokens": 10,
        "usage": {
            "include": True
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        print(f"[INFO] Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] API key is valid!")
            print(f"[SUCCESS] Response: {result['choices'][0]['message']['content']}")

            if 'usage' in result:
                print(f"[INFO] Tokens used: {result['usage']}")

            return True

        elif response.status_code == 401:
            print("\n[ERROR] Authentication failed - API key is invalid")
            print("[ERROR] Response:", response.json())
            print("\nPossible issues:")
            print("1. API key is incorrect or expired")
            print("2. API key doesn't have the 'sk-or-v1-' prefix")
            print("3. Account has insufficient credits")
            print("\nTo fix:")
            print("- Go to https://openrouter.ai/keys")
            print("- Create a new API key")
            print("- Make sure it starts with 'sk-or-v1-'")
            print("- Update your .env file")
            return False

        elif response.status_code == 402:
            print("\n[ERROR] Payment required - No credits on your account")
            print("[ERROR] Response:", response.json())
            print("\nTo fix:")
            print("- Go to https://openrouter.ai/credits")
            print("- Add credits to your account")
            return False

        elif response.status_code == 429:
            print("\n[ERROR] Rate limit exceeded")
            print("[ERROR] Response:", response.json())
            print("\nWait a few seconds and try again")
            return False

        else:
            print(f"\n[ERROR] Unexpected error: {response.status_code}")
            print("[ERROR] Response:", response.text)
            return False

    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out")
        print("Check your internet connection")
        return False

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection failed")
        print("Check your internet connection")
        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("OpenRouter API Key Test")
    print("=" * 60)
    print()

    success = test_openrouter_api_key()

    print("\n" + "=" * 60)
    if success:
        print("Result: API key is working correctly!")
        print("\nYou can now run:")
        print('  python src/main.py "Analyze the ReAct framework"')
    else:
        print("Result: API key test failed")
        print("\nPlease fix the issue and run this test again:")
        print("  python test_api_key.py")
    print("=" * 60)
