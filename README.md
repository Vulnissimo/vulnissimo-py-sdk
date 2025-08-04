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
2. **Initialize the client with your API key**
3. **Start a scan**
4. **Poll for results (manual or auto)**

---

## 📦 Usage Examples

### 1️⃣ Fully Automated

Use the `run_scan` method to quickly run a scan without needing to handle polling manually. The method will automatically handle the scan lifecycle and return the results when the scan is done.

```python
from vulnissimo import Vulnissimo

v = Vulnissimo()

# Run a passive scan with public visibility
scan = v.run_scan("https://pentest-ground.com:4280")

# List vulnerabilities found in the scan
for vulnerability in scan.vulnerabilities:
    print(f"[{vulnerability.risk_level.value}] {vulnerability.title}")
print(f"Scan completed with {len(scan.vulnerabilities)} vulnerabilities found.")

```

---

### 2️⃣ Manual Control (more advanced)

Use the `start_scan` method to initiate a scan and poll for results manually. This gives you more control allowing you to process partial results as they come in.

```python
from time import sleep

from vulnissimo import Vulnissimo

v = Vulnissimo()

# Start the scan
scan = v.start_scan("https://pentest-ground.com:4280")
all_vulnerabilities = []

# Manually poll for scan results
while not scan.is_finished():
    scan = v.poll(scan)

    for vulnerability in scan.vulnerabilities:
        if vulnerability not in all_vulnerabilities:
            print(f"[{vulnerability.risk_level.value}] {vulnerability.title}")
            all_vulnerabilities.append(vulnerability)

    sleep(5)

print(f"Scan completed with {len(scan.vulnerabilities)} vulnerabilities found.")
```

---

### 3️⃣ Active Scan (API Key Required)

Provide a Vulnissimo API key and run active scans.

```python
# First, get an authenticated Vulnisismo instance by providing an API token...
v = Vulnissimo(api_token=API_TOKEN)  # Replace with your API token

# ... then, run an Active Scan using `run_scan` or `start_scan`, as in the examples above.
scan = v.run_scan(
    "https://pentest-ground.com:4280", type=ScanType.ACTIVE, is_private=True
)
# or
scan = v.start_scan(
    "https://pentest-ground.com:4280", type=ScanType.ACTIVE, is_private=True
)
```

---

## 🔑 Getting an API Key

Most features of Vulnissimo are available for free and do not require an API key—just use Passive Scanning and your results will be publicly listed. If you want to use Active Scanning or keep your scan results private, you’ll need an API key.

- To request an API key and get early access to new features, you can join the [Vulnissimo Early Adopter Program](https://vulnissimo.io/join).
- If you’d like to help shape Vulnissimo or have feedback, you’re welcome to join our [Slack community](https://vulnissimo.io/join-slack).

We’re building Vulnissimo in the open and value feedback from all users—no API key required to get started!

---

## 📚 Documentation

See the [full Vulnissimo API reference](https://vulnissimo.io/api-reference) for more details and advanced usage of Vulnissimo API.

---

## 📝 License

MIT
