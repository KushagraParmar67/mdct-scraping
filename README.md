# mdct-scraping

A Python tool to scrape LinkedIn profiles and generate personalized outreach emails using OpenAI.

## Features

- Scrapes LinkedIn profile information including name, title, company, and about section
- Generates personalized emails using OpenAI GPT-4o-mini
- Handles authentication via LinkedIn session cookies
- Returns structured JSON output

## Requirements

- Python 3.8+
- Chrome browser installed
- LinkedIn account (for session cookie)
- OpenAI API key

## Installation

1. Clone the repository:
git clone <repository-url>
cd mdct-scraping



2. Create and activate virtual environment:
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate



3. Install dependencies:
pip install -r requirements.txt



4. Set up environment variables:
cp .env.example .env


Edit `.env` file and add your credentials:
OPENAI_API_KEY=your_openai_api_key_here
LI_AT_COOKIE=your_linkedin_cookie_here



## Getting LinkedIn Cookie

1. Log into LinkedIn in Chrome/Firefox  
2. Open Developer Tools (F12)  
3. Go to Application/Storage > Cookies > https://www.linkedin.com  
4. Find the `li_at` cookie and copy its value  
5. Paste it in the `.env` file  

## Usage

Run the script with a LinkedIn profile URL:
python linkedin_scraper.py "https://www.linkedin.com/in/username/"



## Output

The script returns a JSON object with the following structure:
`{
"name": "John Doe",
"title": "Software Engineer",
"company": "Example Corp",
"about": "Profile about section ...",
"email": {
"subject": "Personalized email subject",
"body": "Personalized email body ..."
}
}`



## Error Handling

- Invalid LinkedIn URLs are rejected
- Missing or invalid cookies trigger appropriate errors
- Profile accessibility issues are caught and reported
- OpenAI API errors are handled gracefully
