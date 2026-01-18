# Installation Guide

## Prerequisites

Before installing, ensure you have:

- **Python 3.8+** — [Download Python](https://python.org/downloads/)
- **Git** — [Download Git](https://git-scm.com/downloads)
- **Pinterest Account** — Business account recommended

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/xodapi/pin.git
cd pin
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Pinterest Developer App

1. Go to [developers.pinterest.com/apps/](https://developers.pinterest.com/apps/)
2. Click **Create app**
3. Fill in the required fields:
   - **App name**: Pinterest Analytics (or any name)
   - **Website URL**: `https://github.com/xodapi/pin`
   - **Privacy Policy URL**: `https://github.com/xodapi/pin/blob/main/PRIVACY.md`
   - **Purpose**: Analytics / Personal use
4. Save and copy your **App ID** and **App Secret**

### 5. Configure Credentials

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file:
```env
PINTEREST_APP_ID=your_app_id_here
PINTEREST_APP_SECRET=your_app_secret_here
```

### 6. Get Access Token

```bash
python get_token.py
```

This will:
- Open your browser for Pinterest authorization
- Automatically save the token to `.env`

### 7. Verify Installation

```bash
python main.py test
```

You should see:
```
Testing Pinterest Authentication

OK Access Token: pina_xxxx...
OK Connected to Pinterest API
OK Username: your_username
```

## Troubleshooting

### "Access Token not configured"
- Make sure `.env` file exists
- Check that `PINTEREST_ACCESS_TOKEN` is set

### "401 Unauthorized"
- Your token may have expired
- Run `python get_token.py` to get a new token

### "Module not found"
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

## Updating

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstalling

Simply delete the `pin` folder. All data is stored locally.
