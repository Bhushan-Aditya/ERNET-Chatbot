import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Set
import re
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin, urlparse
import PyPDF2
import io

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class ERNETScraper:
    def __init__(self):
        self.base_url = "https://www.registry.ernet.in"
        self.data = {
            "pricing": {},
            "policies": {},
            "registration_process": {},
            "faq": {},
            "contact_info": {},
            "general_info": {}
        }
        # Initialize session with SSL verification disabled
        self.session = requests.Session()
        self.session.verify = False
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Keep track of visited URLs to avoid infinite loops
        self.visited_urls: Set[str] = set()

    def _make_request(self, url: str) -> BeautifulSoup:
        """Make a request to the given URL with proper error handling."""
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check if the response is a PDF
            if response.headers.get('content-type', '').lower() == 'application/pdf':
                return self._handle_pdf_response(response)
            
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return None

    def _handle_pdf_response(self, response: requests.Response) -> BeautifulSoup:
        """Handle PDF responses by converting them to text."""
        try:
            # Read PDF content
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Create a simple HTML structure with the PDF content
            html_content = f"<div class='pdf-content'><pre>{text}</pre></div>"
            return BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error handling PDF response: {str(e)}")
            return None

    def _find_relevant_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Find relevant links on the page based on keywords."""
        relevant_links = {}
        keywords = {
            'pricing': ['pricing', 'fee', 'cost', 'charge', 'rate', 'tariff'],
            'policies': ['policy', 'rule', 'term', 'condition', 'guideline'],
            'registration': ['register', 'registration', 'apply', 'application', 'domain', 'renewal'],
            'faq': ['faq', 'question', 'help', 'support', 'guide'],
            'contact': ['contact', 'address', 'phone', 'email', 'support'],
            'about': ['about', 'overview', 'introduction']
        }

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue

            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Skip external links
            if not full_url.startswith(self.base_url):
                continue

            # Check link text and URL against keywords
            link_text = link.get_text().lower()
            url_path = full_url.lower()
            
            for category, words in keywords.items():
                if any(word in link_text or word in url_path for word in words):
                    # Don't overwrite existing links unless the new one is more specific
                    if category not in relevant_links or len(url_path) > len(relevant_links[category]):
                        relevant_links[category] = full_url
                    break

        return relevant_links

    def scrape_website(self) -> Dict:
        """Scrape all relevant information from the ERNET website."""
        try:
            # Start with the main page
            main_page = self._make_request(self.base_url)
            if not main_page:
                logger.warning("Could not access main page. Using fallback data.")
                self._use_fallback_data()
                return self.data

            # Find relevant links from the main page
            relevant_links = self._find_relevant_links(main_page, self.base_url)
            logger.info(f"Found relevant links: {relevant_links}")

            # Extract information from the main page
            self._extract_from_main_page(main_page)

            # Follow relevant links and extract information
            for category, url in relevant_links.items():
                page = self._make_request(url)
                if page:
                    if category == 'pricing':
                        self._extract_pricing_info(page)
                    elif category == 'policies':
                        self._extract_policy_info(page)
                    elif category == 'registration':
                        self._extract_registration_info(page)
                    elif category == 'faq':
                        self._extract_faq_info(page)
                    elif category == 'contact':
                        self._extract_contact_info(page)
                    elif category == 'about':
                        self._extract_about_info(page)

            # Check if we got any data
            total_items = sum(len(section) for section in self.data.values())
            if total_items == 0:
                logger.warning("No data was scraped from the website. Using fallback data.")
                self._use_fallback_data()
            
            logger.info("Successfully scraped ERNET website data")
            return self.data
        except Exception as e:
            logger.error(f"Error scraping website: {str(e)}")
            self._use_fallback_data()
            return self.data

    def _extract_from_main_page(self, soup: BeautifulSoup):
        """Extract information from the main page."""
        try:
            # Look for pricing information
            pricing_section = soup.find('div', string=re.compile(r'pricing|cost|fee', re.I))
            if pricing_section:
                self._extract_pricing_info(pricing_section)

            # Look for registration process
            process_section = soup.find('div', string=re.compile(r'registration|process|steps', re.I))
            if process_section:
                self._extract_registration_info(process_section)

            # Look for contact information
            contact_section = soup.find('div', string=re.compile(r'contact|address|phone', re.I))
            if contact_section:
                self._extract_contact_info(contact_section)

            # Look for general information
            about_section = soup.find('div', string=re.compile(r'about|overview|introduction', re.I))
            if about_section:
                self._extract_about_info(about_section)
        except Exception as e:
            logger.error(f"Error extracting from main page: {str(e)}")

    def _extract_pricing_info(self, soup: BeautifulSoup):
        """Extract pricing information from a page."""
        try:
            # Look for tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        domain_type = cols[0].text.strip()
                        price = cols[1].text.strip()
                        self.data["pricing"][domain_type] = price

            # Look for pricing in text
            pricing_text = soup.find_all(string=re.compile(r'₹|rs\.|rupees|inr|tariff|fee', re.I))
            for text in pricing_text:
                parent = text.parent
                if parent:
                    content = parent.get_text().strip()
                    if any(word in content.lower() for word in ['domain', 'registration', 'renewal']):
                        # Try to extract the price
                        price_match = re.search(r'₹\s*\d+(?:,\d+)*(?:\.\d+)?|\d+(?:,\d+)*(?:\.\d+)?\s*(?:rs\.|rupees|inr)', content, re.I)
                        if price_match:
                            price = price_match.group(0)
                            # Extract the domain type or service
                            domain_type = re.sub(r'₹\s*\d+(?:,\d+)*(?:\.\d+)?|\d+(?:,\d+)*(?:\.\d+)?\s*(?:rs\.|rupees|inr)', '', content, flags=re.I).strip()
                            self.data["pricing"][domain_type] = price
                        else:
                            self.data["pricing"][content] = "Found in text"
        except Exception as e:
            logger.error(f"Error extracting pricing info: {str(e)}")

    def _extract_policy_info(self, soup: BeautifulSoup):
        """Extract policy information from a page."""
        try:
            # Look for policy sections
            policy_sections = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'policy|rule|term', re.I))
            for section in policy_sections:
                title = section.find(['h1', 'h2', 'h3', 'h4'])
                if title:
                    policy_name = title.text.strip()
                    policy_content = section.get_text().strip()
                    self.data["policies"][policy_name] = policy_content

            # Look for policy content in PDF
            if soup.find('div', class_='pdf-content'):
                text = soup.get_text()
                # Split text into sections based on headings or numbers
                sections = re.split(r'\n(?=\d+\.|\w+\.|\n)', text)
                for section in sections:
                    if any(word in section.lower() for word in ['policy', 'rule', 'term', 'condition']):
                        # Try to extract a title
                        title_match = re.search(r'^[^\n]+', section)
                        if title_match:
                            title = title_match.group(0).strip()
                            content = section[len(title):].strip()
                            self.data["policies"][title] = content
        except Exception as e:
            logger.error(f"Error extracting policy info: {str(e)}")

    def _extract_registration_info(self, soup: BeautifulSoup):
        """Extract registration process information from a page."""
        try:
            # Look for steps or process sections
            steps = soup.find_all(['div', 'section', 'li', 'article'], class_=re.compile(r'step|process|registration|renewal', re.I))
            for step in steps:
                step_number = step.find(['span', 'div'], class_=re.compile(r'number', re.I))
                step_content = step.get_text().strip()
                if step_number:
                    self.data["registration_process"][step_number.text.strip()] = step_content
                else:
                    self.data["registration_process"][f"step_{len(self.data['registration_process']) + 1}"] = step_content

            # Look for registration content in PDF
            if soup.find('div', class_='pdf-content'):
                text = soup.get_text()
                # Split text into steps based on numbers or bullet points
                steps = re.split(r'\n(?=\d+\.|\*|\-|\n)', text)
                for step in steps:
                    if any(word in step.lower() for word in ['register', 'apply', 'domain', 'renewal']):
                        # Try to extract a step number
                        number_match = re.search(r'^\d+\.', step)
                        if number_match:
                            step_number = number_match.group(0)
                            content = step[len(step_number):].strip()
                            self.data["registration_process"][step_number] = content
                        else:
                            self.data["registration_process"][f"step_{len(self.data['registration_process']) + 1}"] = step.strip()
        except Exception as e:
            logger.error(f"Error extracting registration info: {str(e)}")

    def _extract_faq_info(self, soup: BeautifulSoup):
        """Extract FAQ information from a page."""
        try:
            # Look for FAQ items
            faq_items = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'faq|question|answer', re.I))
            for item in faq_items:
                question = item.find(['h3', 'h4', 'strong'])
                answer = item.find(['p', 'div'], class_=re.compile(r'answer|content', re.I))
                if question and answer:
                    self.data["faq"][question.text.strip()] = answer.text.strip()

            # Look for FAQ content in PDF
            if soup.find('div', class_='pdf-content'):
                text = soup.get_text()
                # Split text into Q&A pairs
                qa_pairs = re.split(r'\n(?=Q:|Question:|FAQ)', text)
                for pair in qa_pairs:
                    if '?' in pair:
                        # Try to extract question and answer
                        q_match = re.search(r'^(?:Q:|Question:|FAQ)?\s*([^?]+\?)', pair)
                        if q_match:
                            question = q_match.group(1).strip()
                            answer = pair[len(q_match.group(0)):].strip()
                            if answer:
                                self.data["faq"][question] = answer
        except Exception as e:
            logger.error(f"Error extracting FAQ info: {str(e)}")

    def _extract_contact_info(self, soup: BeautifulSoup):
        """Extract contact information from a page."""
        try:
            # Look for contact sections
            contact_sections = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'contact|info|address', re.I))
            for section in contact_sections:
                info_type = section.find(['h3', 'h4', 'strong'])
                if info_type:
                    info_content = section.get_text().strip()
                    self.data["contact_info"][info_type.text.strip()] = info_content

            # Look for specific contact information
            email = soup.find(string=re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', re.I))
            if email:
                self.data["contact_info"]["Email"] = email.strip()

            phone = soup.find(string=re.compile(r'\+?\d{10,}', re.I))
            if phone:
                self.data["contact_info"]["Phone"] = phone.strip()

            # Look for address
            address = soup.find(string=re.compile(r'ERNET|Lodhi Road|New Delhi', re.I))
            if address:
                self.data["contact_info"]["Address"] = address.strip()
        except Exception as e:
            logger.error(f"Error extracting contact info: {str(e)}")

    def _extract_about_info(self, soup: BeautifulSoup):
        """Extract general information from a page."""
        try:
            # Look for about sections
            info_sections = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'about|info|overview', re.I))
            for section in info_sections:
                title = section.find(['h2', 'h3', 'h4'])
                if title:
                    content = section.get_text().strip()
                    self.data["general_info"][title.text.strip()] = content

            # Look for about content in PDF
            if soup.find('div', class_='pdf-content'):
                text = soup.get_text()
                # Split text into sections based on headings
                sections = re.split(r'\n(?=[A-Z][^\n]+:)', text)
                for section in sections:
                    if any(word in section.lower() for word in ['about', 'overview', 'introduction']):
                        # Try to extract a title
                        title_match = re.search(r'^[^\n]+:', section)
                        if title_match:
                            title = title_match.group(0).strip(':')
                            content = section[len(title_match.group(0)):].strip()
                            self.data["general_info"][title] = content
        except Exception as e:
            logger.error(f"Error extracting about info: {str(e)}")

    def _use_fallback_data(self):
        """Use fallback data when scraping fails."""
        self.data = {
            "pricing": {
                "Standard Domain (.ernet.in)": "₹5000 per year",
                "Premium Domain (.ernet.in)": "₹10000 per year",
                "Additional Services": "DNS Management: Free, Email Forwarding: Free, Domain Transfer: ₹1000"
            },
            "policies": {
                "Domain Registration Policy": "Domains are registered on a first-come, first-served basis. All registrations must comply with ERNET's policies and guidelines.",
                "Acceptable Use Policy": "Domains must be used for legitimate educational and research purposes. Commercial use is not permitted.",
                "Domain Name Policy": "Domain names must be between 3-63 characters, can contain letters, numbers, and hyphens, but cannot start or end with a hyphen.",
                "Renewal Policy": "Domains must be renewed before expiration. A grace period of 30 days is provided after expiration."
            },
            "registration_process": {
                "step_1": "Choose your domain name and check availability",
                "step_2": "Complete the online registration form with organization details",
                "step_3": "Submit required documents (Organization registration proof, ID proof, etc.)",
                "step_4": "Make payment through the provided payment gateway",
                "step_5": "Wait for approval (typically 24-48 hours)",
                "step_6": "Configure DNS settings after approval"
            },
            "faq": {
                "Who can register a .ernet.in domain?": "Only educational institutions, research organizations, and government bodies in India can register .ernet.in domains.",
                "How long does domain registration take?": "Domain registration typically takes 24-48 hours after payment confirmation and document verification.",
                "What documents are required?": "You need to provide proof of organization registration, authorized signatory details, and a valid government ID.",
                "Can I transfer my domain to another registrar?": "Yes, domain transfers are allowed. A transfer fee of ₹1000 applies.",
                "What happens if I don't renew my domain?": "Your domain will enter a 30-day grace period after expiration. If not renewed within this period, it will be released for public registration."
            },
            "contact_info": {
                "Email": "support@registry.ernet.in",
                "Phone": "+91-11-2576-0000",
                "Address": "ERNET India, 5th Floor, Block-I, CGO Complex, Lodhi Road, New Delhi - 110003",
                "Working Hours": "Monday to Friday, 9:00 AM to 5:30 PM IST",
                "Support": "Technical support is available 24/7 for critical issues"
            },
            "general_info": {
                "About ERNET": "ERNET (Education and Research Network) is the National Research and Education Network (NREN) of India, established in 1986. It provides high-speed network connectivity and domain registration services to educational and research institutions across India.",
                "Domain Services": "ERNET provides .ernet.in domain registration services exclusively for educational and research institutions in India. The service includes DNS management, email forwarding, and technical support.",
                "Network Coverage": "ERNET's network covers over 1500 institutions across India, including universities, research labs, and educational organizations.",
                "Security": "ERNET implements strict security measures to protect domain registrations and ensure the integrity of the .ernet.in namespace."
            }
        }

    def get_formatted_data(self) -> str:
        """Format the scraped data into a string for the chatbot's context."""
        formatted_data = "ERNET Domain Registry Information:\n\n"
        
        # Add pricing information
        formatted_data += "Domain Pricing:\n"
        for domain_type, price in self.data["pricing"].items():
            formatted_data += f"- {domain_type}: {price}\n"
        
        # Add policies
        formatted_data += "\nDomain Policies:\n"
        for policy, content in self.data["policies"].items():
            formatted_data += f"- {policy}: {content}\n"
        
        # Add registration process
        formatted_data += "\nRegistration Process:\n"
        for step, content in self.data["registration_process"].items():
            formatted_data += f"- {step}: {content}\n"
        
        # Add FAQ
        formatted_data += "\nFrequently Asked Questions:\n"
        for question, answer in self.data["faq"].items():
            formatted_data += f"Q: {question}\nA: {answer}\n"
        
        # Add contact information
        formatted_data += "\nContact Information:\n"
        for info_type, content in self.data["contact_info"].items():
            formatted_data += f"- {info_type}: {content}\n"
        
        # Add general information
        formatted_data += "\nGeneral Information:\n"
        for title, content in self.data["general_info"].items():
            formatted_data += f"- {title}: {content}\n"
        
        return formatted_data 