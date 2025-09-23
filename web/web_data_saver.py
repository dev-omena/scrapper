"""
Web data saver - saves data for web interface
"""
import pandas as pd
import os
import json

class WebDataSaver:
    def __init__(self, output_format="csv", search_query="scraped_data"):
        self.output_format = output_format
        self.search_query = search_query
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def save(self, datalist):
        """Save the scraped data"""
        if len(datalist) > 0:
            print(f"[WEB_SAVER] Saving {len(datalist)} records...")
            
            # Create DataFrame
            dataFrame = pd.DataFrame(datalist)
            
            # Clean search query for filename
            clean_query = "".join(c for c in self.search_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{clean_query}_scraped_data"
            
            # Save as CSV
            csv_path = os.path.join(self.output_dir, f"{filename}.csv")
            dataFrame.to_csv(csv_path, index=False)
            
            # Save as JSON
            json_path = os.path.join(self.output_dir, f"{filename}.json")
            dataFrame.to_json(json_path, indent=4, orient="records")
            
            print(f"[WEB_SAVER] Data saved successfully! {len(datalist)} records saved.")
            return {
                'csv_file': csv_path,
                'json_file': json_path,
                'total_records': len(datalist)
            }
        else:
            print("[WEB_SAVER] No data to save!")
            return None