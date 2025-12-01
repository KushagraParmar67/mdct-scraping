import os
import time
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import openai

load_dotenv()

LI_AT_COOKIE = os.getenv("LI_AT_COOKIE")
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPEN_AI_KEY

def scrape_linkedin_profile(url):
    """Scrape LinkedIn profile with all 4 fields"""
    if not LI_AT_COOKIE:
        print("ERROR: LI_AT_COOKIE not set!")
        return None
    
    # Setup Chrome with bigger window
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Go to LinkedIn to set domain
        driver.get("https://www.linkedin.com")
        time.sleep(2)
        
        # Add cookie
        driver.add_cookie({
            'name': 'li_at',
            'value': LI_AT_COOKIE,
            'domain': '.linkedin.com'
        })
        
        # Go to profile
        driver.get(url)
        time.sleep(5)
        
        # Maximize window and scroll
        driver.maximize_window()
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # Expand "see more" buttons
        see_more_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'see more')]")
        for button in see_more_buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
            except:
                continue
        
        data = {
            "name": None,
            "title": None, 
            "company": None,
            "about": None
        }
        
        # Extract NAME
        name_selectors = [
            "h1.text-heading-xlarge",
            "h1.inline.t-24.t-black.t-normal.break-words",
            "h1.t-24",
            "h1"
        ]
        
        for selector in name_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                name = element.text.strip()
                if name and len(name) > 2:
                    data['name'] = name
                    break
            except:
                continue
        
        # Extract TITLE/HEADLINE
        title_selectors = [
            "div.text-body-medium.break-words",
            "div.inline-show-more-text--is-collapsed-with-line-clamp",
            "div.t-18.t-black.t-normal",
            "div.text-heading-medium"
        ]
        
        for selector in title_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                title = element.text.strip()
                if title and len(title) > 10:
                    data['title'] = title
                    
                    # Clean company name from title
                    if ' at ' in title:
                        parts = title.split(' at ')
                        if len(parts) > 1:
                            company = parts[1].split('-')[0].split(',')[0].split('•')[0].strip()
                            data['company'] = company
                    break
            except:
                continue
        
        # If company not found in title, look for it separately
        if not data.get('company'):
            company_selectors = [
                "span.t-16.t-black.t-normal",
                "div.inline-show-more-text",
                "span.pv-text-details__right-panel-item"
            ]
            
            for selector in company_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 3 and ' at ' not in text and 'HR Manager' not in text:
                            data['company'] = text
                            break
                    if data.get('company'):
                        break
                except:
                    continue
        
        # Extract ABOUT section
        about_selectors = [
            "section#about",
            "div#about ~ div",
            "section[data-section='summary']",
            "div.inline-show-more-text--is-collapsed",
            "div.inline-show-more-text"
        ]
        
        for selector in about_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    about_text = elem.text.strip()
                    if about_text and len(about_text) > 50:
                        about_text = about_text.replace('About', '').strip()
                        about_text = about_text.replace('see more', '').replace('see less', '').strip()
                        data['about'] = about_text
                        break
                if data.get('about'):
                    break
            except:
                continue
        
        # If about not found with selectors, try XPath
        if not data.get('about'):
            about_xpaths = [
                "//section[contains(@class, 'pv-profile-card')]//div[contains(@class, 'inline-show-more-text')]",
                "//div[contains(@class, 'inline-show-more-text--is-collapsed')]",
                "//section[.//h2[contains(text(), 'About')]]//div[contains(@class, 'inline-show-more-text')]"
            ]
            
            for xpath in about_xpaths:
                try:
                    elem = driver.find_element(By.XPATH, xpath)
                    about_text = elem.text.strip()
                    if about_text and len(about_text) > 50:
                        data['about'] = about_text
                        break
                except:
                    continue
        
        # Clean up data
        if data.get('title') and ' at ' in data['title']:
            data['title'] = data['title'].split(' at ')[0].strip()
        
        return data
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None
        
    finally:
        driver.quit()


def generate_email(result):
    """Generate personalized email using OpenAI"""
    if not result:
        return {"subject": "Email Generation Failed", "body": "No profile data available"}
    
    name = result.get("name", "")
    title = result.get("title", "")
    company = result.get("company", "")
    about = result.get("about", "")[:1000]  # Limit about section
    
    prompt = f"""
    The person who is going to send this email is Kushagra Parmar working in Logiqlink technologies as Python Developer and the contact information is kushagraparmar1228@gmail.com
    Create a personalized outreach email for this LinkedIn profile:
    
    Name: {name}
    Title: {title}
    Company: {company}
    About: {about}
    
    The email should be professional, personalized, and reference specific details from the profile.
    Return the response in this EXACT JSON format:
    {{
        "subject": "email subject line here",
        "body": "email body text here"
    }}
    
    Only return the JSON, nothing else.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional recruiter writing personalized outreach emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content.strip()
        
        # Clean response (remove markdown code blocks if present)
        content = content.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        email_data = json.loads(content)
        
        return email_data
        
    except Exception as e:
        print(f"Error generating email: {e}")
        return {"subject": f"Hello {name if name else 'there'}", 
                "body": f"Hi {name if name else 'there'},\n\nI came across your profile and was impressed by your work as a {title} at {company}.\n\nBest regards"}
        
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python scraping_linkedln.py <linkedin_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = scrape_linkedin_profile(url)
    
    if result:
        # Save to JSON For testing
        with open("profile_data.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(json.dumps(result, indent=2))
        
        print(generate_email(result=result))
    else:
        print("Failed to scrape profile")