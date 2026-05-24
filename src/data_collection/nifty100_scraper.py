import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from typing import List, Dict, Any
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Nifty100Scraper:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.nifty100_url = f"{self.base_url}/market-data/live-equity-market?index=NIFTY%20100"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def get_nifty100_stocks(self) -> pd.DataFrame:
        try:
            logger.info("Fetching Nifty 100 stocks...")
            
            # Alternative approach: Use NSE's API endpoint
            api_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100"
            
            response = requests.get(api_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            stocks = data.get('data', [])
            
            stock_list = []
            for stock in stocks:
                stock_info = {
                    'symbol': stock.get('symbol', ''),
                    'company_name': stock.get('companyName', ''),
                    'industry': stock.get('industry', ''),
                    'last_price': stock.get('lastPrice', 0),
                }
                stock_list.append(stock_info)
            
            df = pd.DataFrame(stock_list)
            logger.info(f"Successfully fetched {len(df)} Nifty 100 stocks")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch Nifty 100 stocks: {e}")
            # Return a sample list as fallback for development
            logger.info("Using sample Nifty 100 stocks for development")
            return self._get_sample_stocks()

    def _get_sample_stocks(self) -> pd.DataFrame:
        sample_stocks = [
            {'symbol': 'RELIANCE', 'company_name': 'Reliance Industries Ltd', 'industry': 'Oil & Gas', 'last_price': 0},
            {'symbol': 'TCS', 'company_name': 'Tata Consultancy Services', 'industry': 'IT', 'last_price': 0},
            {'symbol': 'HDFCBANK', 'company_name': 'HDFC Bank Ltd', 'industry': 'Banking', 'last_price': 0},
            {'symbol': 'INFY', 'company_name': 'Infosys Ltd', 'industry': 'IT', 'last_price': 0},
            {'symbol': 'ICICIBANK', 'company_name': 'ICICI Bank Ltd', 'industry': 'Banking', 'last_price': 0},
            {'symbol': 'HINDUNILVR', 'company_name': 'Hindustan Unilever Ltd', 'industry': 'FMCG', 'last_price': 0},
            {'symbol': 'SBIN', 'company_name': 'State Bank of India', 'industry': 'Banking', 'last_price': 0},
            {'symbol': 'BHARTIARTL', 'company_name': 'Bharti Airtel Ltd', 'industry': 'Telecom', 'last_price': 0},
            {'symbol': 'ITC', 'company_name': 'ITC Ltd', 'industry': 'FMCG', 'last_price': 0},
            {'symbol': 'KOTAKBANK', 'company_name': 'Kotak Mahindra Bank Ltd', 'industry': 'Banking', 'last_price': 0},
        ]
        return pd.DataFrame(sample_stocks)

    def get_company_reports_url(self, symbol: str) -> List[str]:
        try:
            # NSE reports URL pattern
            reports_url = f"{self.base_url}/companies/{symbol}/reports"
            
            response = requests.get(reports_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract PDF links for quarterly results
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'pdf' in href.lower() and ('quarterly' in href.lower() or 'earnings' in href.lower()):
                    if href.startswith('/'):
                        href = self.base_url + href
                    pdf_links.append(href)
            
            logger.info(f"Found {len(pdf_links)} report links for {symbol}")
            return pdf_links
            
        except Exception as e:
            logger.error(f"Failed to get reports for {symbol}: {e}")
            return []

    def download_report(self, url: str, save_path: str) -> bool:
        try:
            response = requests.get(url, headers=self.headers, timeout=60)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded report to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download report from {url}: {e}")
            return False

    def scrape_all_reports(
        self,
        output_dir: str = "./data/companies",
        max_stocks: int = 5
    ):
        stocks_df = self.get_nifty100_stocks()
        
        # Limit to max_stocks for initial development
        stocks_df = stocks_df.head(max_stocks)
        
        logger.info(f"Starting to scrape reports for {len(stocks_df)} stocks")
        
        for _, stock in stocks_df.iterrows():
            symbol = stock['symbol']
            company_name = stock['company_name']
            
            logger.info(f"Processing {symbol} - {company_name}")
            
            # Create company directory
            company_dir = os.path.join(output_dir, symbol)
            os.makedirs(company_dir, exist_ok=True)
            
            # Get report URLs
            report_urls = self.get_company_reports_url(symbol)
            
            # Download reports
            for i, url in enumerate(report_urls[:3]):  # Limit to 3 reports per company
                filename = f"report_{i+1}.pdf"
                save_path = os.path.join(company_dir, filename)
                self.download_report(url, save_path)
            
            # Rate limiting
            time.sleep(2)
        
        logger.info("Scraping completed")


if __name__ == "__main__":
    scraper = Nifty100Scraper()
    scraper.scrape_all_reports(max_stocks=5)
