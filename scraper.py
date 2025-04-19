from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time

def scrape_redbus_data():
    # Set up Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Navigate to Redbus website
    driver.get("https://www.redbus.in/")
    
    # Allow time for page to load
    time.sleep(10)
    
    # Example: Search for a specific route (modify as necessary)
    # Entering source and destination
    source = driver.find_element(By.ID, "src")
    destination = driver.find_element(By.ID, "dest")
    
    source.send_keys("Bangalore")
    destination.send_keys("Mysore")
    
    # Click on Search button
    search_button = driver.find_element(By.CLASS_NAME, "search-btn")
    search_button.click()
    
    time.sleep(5)  # Allow time for results to load
    
    # Scrape bus details
    buses = []
    
    bus_elements = driver.find_elements(By.CLASS_NAME, "bus-item")
    
    for bus in bus_elements:
        try:
            route_name = bus.find_element(By.CLASS_NAME, "route-name").text
            route_link = bus.find_element(By.TAG_NAME, 'a').get_attribute('href')
            bus_name = bus.find_element(By.CLASS_NAME, "bus-name").text
            bustype = bus.find_element(By.CLASS_NAME, "bus-type").text
            departing_time = bus.find_element(By.CLASS_NAME, "departing-time").text
            duration = bus.find_element(By.CLASS_NAME, "duration").text
            reaching_time = bus.find_element(By.CLASS_NAME, "reaching-time").text
            star_rating = float(bus.find_element(By.CLASS_NAME, "rating").text)
            price = float(bus.find_element(By.CLASS_NAME, "price").text.replace('₹', '').replace(',', '').strip())
            seats_available = int(bus.find_element(By.CLASS_NAME, "seats-available").text.split()[0])
            
            buses.append({
                'route_name': route_name,
                'route_link': route_link,
                'busname': bus_name,
                'bustype': bustype,
                'departing_time': departing_time,
                'duration': duration,
                'reaching_time': reaching_time,
                'star_rating': star_rating,
                'price': price,
                'seats_available': seats_available
            })
        except Exception as e:
            print(f"Error scraping bus details: {e}")
    
    driver.quit()
    
    return buses

if __name__ == "__main__":
    scraped_data = scrape_redbus_data()
    
    # Convert to DataFrame and save to CSV (or directly to SQL)
    df = pd.DataFrame(scraped_data)
    df.to_csv('redbus_data.csv', index=False)



