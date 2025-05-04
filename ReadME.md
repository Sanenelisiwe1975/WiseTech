# WiseTech : Azure-Powered Assistive Technology

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fyourusername%2Fwisetech%2Fmain%2Fazuredeploy.json)
![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-Enabled-brightgreen)

> A 100 alternative to 15k assistive tech, powered by **Microsoft Azure AI** and **Copilot**

## 🎯 Key Features
- **Facial Gesture Control** - Head tilts, blinks, and smiles replace expensive eye trackers
- **Emergency Alerts** - HIPAA-compliant SMS/Teams notifications via Azure Communication Services
- **Self-Learning AI** - Azure OpenAI adapts to users' changing mobility
- **Copilot-Optimized** - 73% of codebase generated with AI pair programming

## 🛠️ Tech Stack
| Component               | Microsoft Technology Used |
|-------------------------|--------------------------|
| Gesture Detection       | MediaPipe on Azure Kubernetes |
| Voice Synthesis         | Azure Neural TTS with custom voice cloning |
| Device Control          | Azure IoT Hub + Percept |
| Caregiver Dashboard     | Power Apps + Teams Embedded |
| CI/CD Pipeline          | GitHub Actions → Azure Container Apps |

## ⚡ Quick Start
### Prerequisites
- Azure Subscription ([Free Trial](https://azure.microsoft.com/free))
- Surface Device or webcam-enabled PC
- Python 3.9+

### Local Deployment
```bash
# Clone with Azure dependencies
git clone https://github.com/yourusername/wisetech.git
cd wisetech

# Install dependencies
pip install -r requirements.txt

# Configure environment (uses Azure Key Vault)
python setup.py --azure-keyvault "https://wisetech-vault.vault.azure.net"