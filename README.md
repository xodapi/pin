<div align="center">

<img src="docs/assets/logo.png" alt="Pinterest Analytics Logo" width="120">

# Pinterest Analytics

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Pinterest API](https://img.shields.io/badge/Pinterest-API%20v5-red.svg?logo=pinterest)](https://developers.pinterest.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/xodapi/pin?style=social)](https://github.com/xodapi/pin)

**Powerful analytics tool for your Pinterest account**

*Built with [python-pinterest](https://github.com/sns-sdks/python-pinterest) SDK*

[English](#features) • [Русский](docs/README.ru.md)

</div>

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🛡️ **Backup Protection** | Save all pins & images locally |
| ⚡ **Quick Status** | 30-second health check |
| 🗑️ **Smart Cleanup** | Find underperforming pins |
| 📈 **Trends Analysis** | Find your niche |
| 🔑 **SEO Keywords** | Optimize your content |
| 🖥️ **Web Dashboard** | Beautiful charts & tables |
| 📊 **Export Reports** | JSON, CSV, Excel formats |
| 🔒 **Privacy First** | All data stored locally |

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Pinterest Business Account (recommended)
- Pinterest Developer App credentials

### Installation

```bash
# Clone the repository
git clone https://github.com/xodapi/pin.git
cd pin

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Create a Pinterest App at [developers.pinterest.com](https://developers.pinterest.com/apps/)
2. Copy the example config:
   ```bash
   cp .env.example .env
   ```
3. Add your credentials to `.env`:
   ```env
   PINTEREST_APP_ID=your_app_id
   PINTEREST_APP_SECRET=your_app_secret
   ```
4. Get your access token:
   ```bash
   python get_token.py
   ```

### Usage

```bash
# Quick status check (30 seconds)
python main.py quick

# Open web dashboard
python main.py dashboard

# Backup all your content
python main.py backup
python main.py backup --images  # with images

# Find underperforming pins
python main.py cleanup
python main.py cleanup -e csv   # export list

# Analyze keywords for SEO
python main.py keywords
python main.py keywords -c "art"  # check specific

# Find your niche
python main.py trends
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/INSTALL.md) | Detailed installation instructions |
| [API Reference](docs/API.md) | Python API documentation |
| [Privacy Policy](PRIVACY.md) | How we handle your data |
| [Contributing](CONTRIBUTING.md) | How to contribute |

## 🛠️ Available Commands

```
main.py <command> [options]

Essential:
  quick       Quick 30-second status check
  dashboard   Open web dashboard with charts
  backup      Backup pins & boards (--images for images)

Analytics:
  cleanup     Find underperforming pins (-d days, -e export)
  trends      Analyze trends and find your niche
  keywords    Analyze keywords for SEO (-c to check specific)
  evening     Generate daily evening report

Data:
  test        Test Pinterest API connection
  summary     Show account summary
  boards      List all boards
  pins        List pins
  export      Export to JSON/CSV/Excel
```

## 📁 Project Structure

```
pin/
├── 📄 main.py              # CLI entry point
├── 📄 get_token.py         # OAuth helper
├── 📄 requirements.txt     # Dependencies
├── 📁 src/
│   ├── 📄 auth.py          # Authentication
│   ├── 📄 analytics.py     # Data fetching
│   └── 📄 report.py        # Report generation
├── 📁 docs/
│   ├── 📄 README.ru.md     # Russian docs
│   └── 📄 INSTALL.md       # Installation guide
└── 📁 reports/             # Generated reports
```

## 🔐 Security & Privacy

- ✅ **No data collection** — All data stays on your device
- ✅ **No third-party sharing** — We never share your data
- ✅ **Open source** — Review our code anytime
- ✅ **GDPR compliant** — Full control over your data
- ✅ **Token security** — Credentials stored locally in `.env`

Read our full [Privacy Policy](PRIVACY.md).

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pinterest API](https://developers.pinterest.com) for the amazing API
- [python-pinterest](https://github.com/sns-sdks/python-pinterest) community SDK
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ by [xodapi](https://github.com/xodapi)

</div>
