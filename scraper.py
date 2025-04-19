from database import store_data_to_sql
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from datetime import datetime
import re

def scrape_redbus_data():
    today = datetime.now()
    day = today.day
    month_year = today.strftime('%b %Y')  # Month in abbreviated form (e.g., "Apr")
    print(month_year)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    
    try:
        driver.get("https://www.redbus.in/")
        time.sleep(5)

        
        src = driver.find_element(By.ID, "src")
        s='Bangalore'
        src.send_keys(s)
        time.sleep(1)
        src.send_keys(Keys.DOWN, Keys.ENTER)

        
        dest = driver.find_element(By.ID, "dest")
        d='Chennai'
        dest.send_keys(d)
        time.sleep(1)
        dest.send_keys(Keys.DOWN, Keys.ENTER)

        calendar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onwardCal"))
        )
        calendar_button.click()
        
        # Wait for calendar to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".DatePicker__CalendarContainer-sc-1kf43k8-0"))
        )
        
        # Navigate to correct month/year
        date_selected = False
        while not date_selected:
            # Find the month/year element
            month_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "div.DayNavigator__IconBlock-qj8jdz-2.iZpveD[style*='flex-grow: 2']"))
            )
            
            current_month = month_element.text.split('\n')[0]
            print("scraper moonth/year", current_month)
            
            if current_month == month_year:
                day_spans = driver.find_elements(By.CSS_SELECTOR, "span.DayTiles__CalendarDaysSpan-sc-1xum02u-1")
                
                for span in day_spans:
                    if span.text == str(day):
                        class_name = span.get_attribute("class")
                        if "dkWAbH" not in class_name:  # dkWAbH appears to be used for disabled dates
                            span.click()
                            print(f"Selected day {day}")
                            date_selected = True
                            break
                        else:
                            day += 1
                            if day > 31:  # Simple overflow handling
                                day = 1
                            continue

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "search_button"))
        )
        search_button.click()
        print("Search button clicked!")
        

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bus-item"))
        )
        time.sleep(5)

        # Collect bus data
        buses = []
        SCROLL_PAUSE_TIME = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Get all bus items
        bus_items = driver.find_elements(By.CSS_SELECTOR, "div.bus-item")
        print(f"Found {len(bus_items)} bus entries")
        
        for bus_item in bus_items:
            try:
                # Extract bus details using the exact classes from the HTML template
                bus_name = bus_item.find_element(By.CSS_SELECTOR, "div.travels").text
                
                # Bus type
                try:
                    bus_type = bus_item.find_element(By.CSS_SELECTOR, "div.bus-type").text
                except:
                    bus_type = "Not specified"
                
                # Departure time
                departure_time = bus_item.find_element(By.CSS_SELECTOR, "div.dp-time").text
                
            
                
                # Duration
                try:
                    duration = bus_item.find_element(By.CSS_SELECTOR, "div.dur").text
                except:
                    duration = "Not specified"
                
                # Arrival time
                arrival_time = bus_item.find_element(By.CSS_SELECTOR, "div.bp-time").text
                
               
                
                # Rating
                try:
                    rating_element = bus_item.find_element(By.CSS_SELECTOR, "div.rating span")
                    rating = float(rating_element.text)
                except:
                    rating = None
                
                # Number of ratings
                try:
                    ratings_count_element = bus_item.find_element(By.CSS_SELECTOR, "div.no-ppl span")
                    ratings_count = int(ratings_count_element.text)
                except:
                    ratings_count = None
                
                # Price
                try:
                    fare_element = bus_item.find_element(By.CSS_SELECTOR, "div.fare span.f-19")
                    # Extract only the numeric part
                    fare_text = fare_element.text
                    # Remove all non-numeric characters
                    fare = float(re.sub(r'[^\d.]', '', fare_text))
                except:
                    try:
                        # Alternative selector for fare
                        fare_element = bus_item.find_element(By.CSS_SELECTOR, "div.fare")
                        fare_text = fare_element.text
                        fare = float(re.sub(r'[^\d.]', '', fare_text))
                    except:
                        fare = None
                
                
                
                # Seats available
                try:
                    seats_element = bus_item.find_element(By.CSS_SELECTOR, "div.seat-left")
                    seats_text = seats_element.text
                    # Extract the number before "Seats available"
                    seats_match = re.search(r'(\d+)', seats_text)
                    seats = int(seats_match.group(1)) if seats_match else None
                except:
                    seats = None
                
            
                
                
                # Collect all the data
                bus_info = {
                    'route_name': f"{s} - {d}",
                    'route_link': driver.current_url,
                    'bus_name': bus_name,
                    'bus_type': bus_type,
                    'departure_time': departure_time,
                    
                    'reaching_time': arrival_time,
                    
                    'duration': duration,
                    'rating': rating,
                    'ratings_count': ratings_count,
                    'price': fare,
                    'seats_available': seats
                }
                
                buses.append(bus_info)
                
                
            except Exception as e:
                print(f"Error scraping a bus: {str(e)}")
        
        
        return buses
        
    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")
        return []
    
    finally:
        # Always close the driver
        driver.quit()
        print("WebDriver closed")

if __name__ == "__main__":
    data = scrape_redbus_data()
    
    if data:
        df = pd.DataFrame(data)
        df.to_csv("redbus_data.csv", index=False)
        store_data_to_sql('redbus_data.csv')
        print(f"Saved {len(df)} records to redbus_data.csv.")
    else:
        print("No data collected. Check the logs for errors.")