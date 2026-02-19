# Security Policy

We take the security and integrity of the **RockDeals POS System** extremely seriously. As a Point of Sale application, we understand the critical nature of data protection and operational continuity. This document outlines our security policies, supported versions, and the responsible disclosure procedure for reporting vulnerabilities.

## Supported Versions

We actively maintain and provide critical security updates for the following versions of the project. We strongly advise all users to ensure they are running a supported version to mitigate potential risks.

| Version | Supported          | Description                                              |
| ------- | ------------------ | -------------------------------------------------------- |
| 1.x.x   | :white_check_mark: | Active development, major features, and security patches |
| < 1.0   | :x:                | Deprecated. No security updates provided                 |

*(Note: The versioning table should be updated as new major versions are released.)*

## Reporting a Vulnerability

We deeply appreciate the efforts of security researchers and the broader open-source community in helping us maintain a secure ecosystem. 

If you discover a potential security vulnerability within the RockDeals POS System, **please do not disclose it publicly** by creating a standard GitHub issue. Public disclosure before a patch is available can put our users at risk. Instead, please follow our responsible disclosure process:

### 1. How to Report
Please report security vulnerabilities privately using one of the following methods:

* **[GitHub](github.com) Security Advisories:** Use the private reporting feature provided by GitHub for this repository: [Report a Vulnerability](https://github.com/CP-S-Enterprise-for-technology-s/RockDeals-POS-System/security/advisories/new)
* **Direct Email:** Send a detailed report directly to our security team at:

   | Email_addres | Info.cpsfortechnology@gmail.com |
   | ------------ | ------------------------------- |
### 2. What to Include in Your Report
To facilitate a rapid investigation and resolution, please include the following details in your report:
* A descriptive summary of the vulnerability and its potential impact.
* The specific version(s) affected.
* Detailed, step-by-step instructions to reproduce the vulnerability.
* Any relevant proof-of-concept (PoC) code, scripts, or screenshots.
* Suggested mitigation or remediation strategies (if applicable).

### 3. Our Response Commitment
Upon receiving your report, our team will adhere to the following workflow:
1.  **Acknowledgment:** We will acknowledge receipt of your vulnerability report within **48 hours**.
2.  **Triage & Assessment:** We will investigate and confirm the vulnerability, assessing its severity and impact.
3.  **Remediation:** If confirmed, we will prioritize the development of a patch or mitigation strategy.
4.  **Coordination & Disclosure:** We will keep you informed of our progress. Once a fix is deployed and users have been given appropriate time to update, we may coordinate a public disclosure and acknowledge your contribution (subject to your consent).

## Out of Scope
The following types of reports are generally considered out of scope unless they demonstrate a significant, exploitable impact:
* Theoretical vulnerabilities without a working Proof of Concept.
* Missing security headers that do not lead directly to an exploit.
* Vulnerabilities in third-party dependencies (unless the vulnerability is a direct result of our specific implementation or configuration).

---
*By contributing to this repository or reporting a vulnerability, you agree to adhere to these responsible disclosure guidelines.*
