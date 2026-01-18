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
| 📈 **Account Analytics** | View followers, pins, boards statistics |
| 📋 **Board Insights** | Detailed metrics for each board |
| 📌 **Pin Performance** | Track your pins engagement |
| 📊 **Export Reports** | Export to JSON, CSV, Excel |
| 🔒 **Privacy First** | All data stored locally |
| 🚀 **Fast & Lightweight** | CLI-based, no heavy dependencies |

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
# Test connection
python main.py test

# View account info
python main.py account

# List all boards
python main.py boards

# List pins
python main.py pins

# Show summary
python main.py summary

# Export all data
python main.py export -t all -f json
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

Commands:
  test        Test Pinterest API connection
  account     Display account information
  boards      List all boards with stats
  pins        List pins (use -n for limit, -b for board)
  summary     Show account summary with top boards
  analytics   Show detailed analytics (Business accounts)
  export      Export data to file (-t type, -f format)

Options:
  -n, --limit    Number of items to show
  -b, --board    Board ID to filter by
  -t, --type     Export type: summary, boards, pins, all
  -f, --format   Output format: json, csv, excel
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
