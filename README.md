# Reddit Scraper

A comprehensive tool for scraping Reddit data with both command-line and graphical user interfaces for data collection, analysis, and visualization in a local development environment.

## Features

- Simple and advanced UI options
- Search multiple subreddits simultaneously
- Filter posts by keywords and various criteria
- Visualize data with interactive charts
- Export results to CSV or JSON
- Track search history

## Installation

1. Clone this repository
2. Make sure you have Python 3.7+ installed
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the script to launch the UI:

```bash
./run_scraper.sh
```

For the basic UI mode:

```bash
./run_scraper.sh basic
```

### Manual Launch

Alternatively, you can run either UI directly:

```bash
# Basic UI
streamlit run scraper_ui.py

# Advanced UI
streamlit run advanced_scraper_ui.py
```

## Requirements

- Python 3.7+
- Reddit API credentials (provided by default for testing)
- Dependencies listed in requirements.txt

## Development

This project includes:

- `google_adk.py` - Core file with Reddit scraper functionality
- `enhanced_scraper.py` - Extended scraper with advanced features
- `scraper_ui.py` - Basic Streamlit UI
- `advanced_scraper_ui.py` - Advanced UI with visualizations and filtering

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Note

The included Reddit API credentials are for demonstration purposes only. For production use, please obtain your own credentials from the [Reddit Developer Portal](https://www.reddit.com/prefs/apps).
