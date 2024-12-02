# World Bank Statistics Comparison Tool

This Django web application allows users to compare different World Bank statistics across countries using interactive visualizations.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Features
- Compare any two World Bank statistics
- Interactive graphs using Plotly
- Data fetched directly from World Bank API
- Support for multiple countries and years
- Dynamic data loading
