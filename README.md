# 🛡️ vulnissimo-py-sdk

Vulnissimo is a powerful web application vulnerability scanner that helps you automate the detection of security issues in websites exposed to the Internet. This Python SDK lets you interact with the Vulnissimo API to launch and monitor vulnerability scans for your web applications, right from your code.

## 🔍 About Vulnissimo

Vulnissimo offers two scanning modes:

- **Passive Scanning** 🟢

  - Fast, lightweight, and non-intrusive.
  - Detects vulnerabilities without sending attack payloads (e.g., outdated software, exposed secrets, misconfigurations).
  - **No API token required**. Results are publicly listed on [vulnissimo.io](https://vulnissimo.io/).
- **Active Scanning** 🔴

  - Performs in-depth security testing by injecting attack payloads to find issues like XSS, SQL injection, and more.
  - **API token required**. Results are private.
  - May trigger security alerts on the target and should only be used with permission.

---

## 🚀 Installation

```bash
pip install vulnissimo
```

---

## 🏁 Getting Started

1. **Import the SDK**
2. **Initialize the client with your API Token**
3. **Start a scan**
4. **Poll for results (manual or auto)**

---

## 📦 Usage Examples

### 1️⃣ Passive Scan (Free)

```python
from vulnissimo import Vulnissimo
from vulnissimo.models import ScanType

v = Vulnissimo()

# Run a passive scan with private visibility
scan = v.run_scan(
    "https://pentest-ground.com:4280", type=ScanType.PASSIVE, is_private=True
)

# List vulnerabilities found in the scan
for vulnerability in scan.vulnerabilities:
    print(f"[{vulnerability.risk_level.value}] {vulnerability.title}")
print(f"Scan completed with {len(scan.vulnerabilities)} vulnerabilities found.")

```

---

### 2️⃣ Active Scan (API Token Required)

Provide a Vulnissimo API Token and run active scans.

```python
from vulnissimo import Vulnissimo
from vulnissimo.models import ScanType

# First, get an authenticated Vulnisismo instance by providing an API token...
v = Vulnissimo(api_token=API_TOKEN)  # Replace with your API token

# Run a passive scan with private visibility
scan = v.run_scan(
    "https://pentest-ground.com:4280", type=ScanType.ACTIVE, is_private=True
)

# List vulnerabilities found in the scan
for vulnerability in scan.vulnerabilities:
    print(f"[{vulnerability.risk_level.value}] {vulnerability.title}")
print(f"Scan completed with {len(scan.vulnerabilities)} vulnerabilities found.")
```

---

## 🔑 Getting an API Token

Running Active Scans requires an API Token, which can be obtained by registering a Vulnissimo account. It is not mandatory to have an API Token for Passive Scans but you will be subject to more strict rate limiting.

- To request an API Token and get early access to new features, you can join the [Vulnissimo Early Adopter Program](https://vulnissimo.io/join).
- If you’d like to help shape Vulnissimo or have feedback, you’re welcome to join our [Slack community](https://vulnissimo.io/join-slack).

We’re building Vulnissimo in the open and value feedback from all users—no API Token required to get started!

---

## 📚 Documentation

See the [full Vulnissimo API reference](https://vulnissimo.io/api-reference) for more details and advanced usage of Vulnissimo API.

---

## 📝 License

MIT
