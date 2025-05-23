#!/usr/bin/env python3
"""
E3 Technical HaynesPro Web Scraper using MechanicalSoup
This script logs into e3technical.haynespro.com, searches for a vehicle by VRM,
and extracts the vehicle data.
"""

import mechanicalsoup
from bs4 import BeautifulSoup
from typing import Dict, Any

class E3TechnicalScraper:
    """
    A scraper for e3technical.haynespro.com that retrieves vehicle data by VRM.
    """
    def __init__(self, username: str, password: str):
        """
        Initialize the scraper with login credentials.
        
        Args:
            username (str): Username for e3technical.haynespro.com
            password (str): Password for e3technical.haynespro.com
        """
        self.username = username
        self.password = password
        self.url = "https://e3technical.haynespro.com/"
        
        # Create a browser object
        self.browser = mechanicalsoup.StatefulBrowser(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            raise_on_404=True,
            soup_config={'features': 'lxml'}
        )
    
    def login(self) -> bool:
        """
        Log in to e3technical.haynespro.com.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Open the login page
            self.browser.open(self.url)
            
            # Select the login form
            try:
                self.browser.select_form('form[action="./Login.aspx"]')
            except mechanicalsoup.utils.LinkNotFoundError:
                forms = self.browser.get_current_page().find_all('form')
                if forms:
                    self.browser.select_form(forms[0])
                else:
                    return False
            
            # Fill in the login form with correct field names
            self.browser["ctl00$MainContentPlaceHolder$Username"] = self.username
            self.browser["ctl00$MainContentPlaceHolder$Password"] = self.password
            
            # Submit the form
            response = self.browser.submit_selected()
            
            # Check if login was successful
            return "Welcome to e3 technical" in response.text
                
        except Exception:
            return False
    
    def search_vrm(self, vrm: str) -> bool:
        """
        Search for a vehicle by VRM.
        
        Args:
            vrm (str): Vehicle Registration Mark
            
        Returns:
            bool: True if search successful, False otherwise
        """
        try:
            self.browser.select_form('form#aspnetForm')
            self.browser["ctl00$SearchContentPlaceHolder$Search$SearchKey"] = vrm
            self.browser.form["__EVENTTARGET"] = "ctl00$SearchContentPlaceHolder$Search$SearchVehicle"
            self.browser.form["__EVENTARGUMENT"] = ""

            response = self.browser.submit_selected()

            return "Vehicle Registration Mark (Current)" in response.text or bool(self.browser.get_current_page().find('table', class_='data-table'))
                
        except Exception:
            return False
    
    def extract_vehicle_data(self) -> Dict[str, Any]:
        """
        Extract vehicle data from the search results page.
        
        Returns:
            dict: Dictionary containing vehicle data
        """
        try:
            page = self.browser.get_current_page()
            vehicle_data_container = page.find(id="ctl00_MainContentPlaceHolder_VehicleDataContainer")
            
            if not vehicle_data_container:
                return {}
            
            vehicle_data = {}
            rows = vehicle_data_container.find_all("tr")
            
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    key = cells[0].get_text(separator=" ", strip=True)
                    value = cells[1].get_text(separator=" ", strip=True)
                    if key and value:
                        vehicle_data[key] = value

            return vehicle_data
            
        except Exception:
            return {}
    
    def get_vehicle_data(self, vrm: str) -> Dict[str, Any]:
        """
        Get vehicle data for a given VRM.
        
        Args:
            vrm (str): Vehicle Registration Mark
            
        Returns:
            dict: Dictionary containing vehicle data or error message
        """
        try:
            # Clean the VRM
            vrm = vrm.upper().strip().replace(" ", "")
            
            # Login
            if not self.login():
                return {"error": "Login failed"}
            
            # Search for VRM
            if not self.search_vrm(vrm):
                return {"error": "VRM search failed"}
            
            # Extract vehicle data
            data = self.extract_vehicle_data()
            
            if not data:
                return {"error": "No vehicle data found"}
            
            return data
            
        except Exception as e:
            return {"error": f"Scraping failed: {str(e)}"}
