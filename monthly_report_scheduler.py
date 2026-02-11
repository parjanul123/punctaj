# -*- coding: utf-8 -*-
"""
Weekly Report Scheduler
Salvează automat raportele săptămânal în folderul arhiva luni la 00:00 (ora României)
"""

import os
import json
import csv
import requests
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging

logger = logging.getLogger(__name__)

class WeeklyReportScheduler:
    """Scheduler pentru salvarea rapoartelor săptămânale în folderul arhiva"""
    
    def __init__(self, data_dir: str, archive_dir: str):
        """
        Initialize scheduler
        
        Args:
            data_dir: Path to data folder (d:\\punctaj\\data)
            archive_dir: Path to archive folder (d:\\punctaj\\arhiva)
        """
        self.data_dir = data_dir
        self.archive_dir = archive_dir
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(timezone=pytz.timezone('Europe/Bucharest'))
        
        # Create archive directory if it doesn't exist
        os.makedirs(archive_dir, exist_ok=True)
        
        logger.info(f"✅ WeeklyReportScheduler initialized")
        logger.info(f"   Data dir: {data_dir}")
        logger.info(f"   Archive dir: {archive_dir}")
    
    def start(self):
        """Start the scheduler"""
        if self.scheduler.running:
            logger.warning("Scheduler already running!")
            return
        
        # Schedule job to run at 00:00 every Monday (Romania time)
        # day_of_week=0 means Monday
        self.scheduler.add_job(
            self.generate_weekly_report,
            trigger=CronTrigger(hour=0, minute=0, day_of_week=0, timezone='Europe/Bucharest'),
            id='weekly_report',
            name='Weekly Report Generation',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("✅ Weekly report scheduler started")
        logger.info("   Will run at 00:00 every Monday (Romania time)")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✅ Weekly report scheduler stopped")
    
    def generate_weekly_report(self):
        """Generate and save weekly report to archive folder and Supabase"""
        try:
            print("\n" + "="*60)
            print("🔄 WEEKLY REPORT GENERATION STARTED")
            print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Romania)")
            print("="*60)
            
            # Get current date for folder name
            now = datetime.now()
            week_str = now.strftime("%Y-W%W")  # Format: 2026-W05
            monday = now - __import__('datetime').timedelta(days=now.weekday())
            week_range = f"{monday.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}"
            
            # Create weekly folder in archive
            weekly_dir = os.path.join(self.archive_dir, week_str)
            os.makedirs(weekly_dir, exist_ok=True)
            
            # Get list of all cities
            cities = self._get_cities()
            
            total_files = 0
            total_rows = 0
            
            for city in cities:
                # Get institutions for this city
                institutions = self._get_institutions(city)
                
                for institution in institutions:
                    # Load institution data
                    inst_data = self._load_institution(city, institution)
                    if not inst_data:
                        continue
                    
                    # Create city folder in weekly archive
                    city_archive = os.path.join(weekly_dir, city)
                    os.makedirs(city_archive, exist_ok=True)
                    
                    # Save as CSV
                    csv_path = os.path.join(city_archive, f"{institution}.csv")
                    self._save_as_csv(csv_path, inst_data)
                    
                    rows = inst_data.get("rows", [])
                    total_files += 1
                    total_rows += len(rows)
                    
                    # Save to Supabase weekly_reports table
                    self._save_to_supabase(city, institution, monday, now, rows)
                    
                    print(f"   ✅ Saved: {city}/{institution}.csv ({len(rows)} employees)")
            
            print("="*60)
            print("📊 WEEKLY REPORT GENERATION COMPLETED")
            print(f"   Saved to: {weekly_dir}")
            print(f"   Week: {week_range}")
            print(f"   Total files: {total_files}")
            print(f"   Total employees: {total_rows}")
            print("="*60 + "\n")
            
            logger.info(f"✅ Weekly report generated for week {week_str}")
            logger.info(f"   Location: {weekly_dir}")
            logger.info(f"   Files: {total_files}, Rows: {total_rows}")
            
        except Exception as e:
            logger.error(f"❌ Error generating weekly report: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_cities(self) -> list:
        """Get list of all cities from data directory"""
        try:
            cities = []
            for item in os.listdir(self.data_dir):
                item_path = os.path.join(self.data_dir, item)
                if os.path.isdir(item_path):
                    cities.append(item)
            return sorted(cities)
        except Exception as e:
            logger.error(f"Error getting cities: {e}")
            return []
    
    def _get_institutions(self, city: str) -> list:
        """Get list of institutions in a city"""
        try:
            city_path = os.path.join(self.data_dir, city)
            institutions = []
            
            for file in os.listdir(city_path):
                if file.endswith('.json'):
                    # Remove .json extension
                    inst_name = file[:-5]
                    institutions.append(inst_name)
            
            return sorted(institutions)
        except Exception as e:
            logger.error(f"Error getting institutions for {city}: {e}")
            return []
    
    def _load_institution(self, city: str, institution: str) -> dict:
        """Load institution data from JSON"""
        try:
            inst_path = os.path.join(self.data_dir, city, f"{institution}.json")
            
            if not os.path.exists(inst_path):
                return None
            
            with open(inst_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {city}/{institution}: {e}")
            return None
    
    def _save_as_csv(self, csv_path: str, inst_data: dict) -> bool:
        """Save institution data as CSV"""
        try:
            columns = inst_data.get("columns", [])
            rows = inst_data.get("rows", [])
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header with date
                date_header = f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                writer.writerow([date_header])
                writer.writerow([])  # Empty line
                
                # Write column headers
                writer.writerow(columns)
                
                # Write data rows
                for row in rows:
                    if isinstance(row, dict):
                        values = [str(row.get(col, "")) for col in columns]
                    else:
                        values = [str(v) for v in row]
                    
                    writer.writerow(values)
            
            return True
        except Exception as e:
            logger.error(f"Error saving CSV {csv_path}: {e}")
            return False
    
    def _save_to_supabase(self, city: str, institution: str, week_start, week_end, employees: list) -> bool:
        """Save weekly report to Supabase weekly_reports table using REST API"""
        try:
            import requests
            
            # Import SUPABASE_SYNC to get credentials
            import sys
            import os
            
            # Get the parent directory and add it to path if needed
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from supabase_sync import SUPABASE_SYNC
            
            if not SUPABASE_SYNC or not SUPABASE_SYNC.enabled:
                logger.warning(f"⚠️ Supabase not configured, skipping Supabase save for {city}/{institution}")
                return False
            
            # Prepare data for weekly_reports table
            report_data = {
                "columns": ["DISCORD", "NUME IC", "RANK", "ROLE", "PUNCTAJ", "SERIE DE BULETIN", "ULTIMA_MOD"],
                "rows": employees,
                "employee_count": len(employees)
            }
            
            report_json = {
                "week_start": week_start.strftime('%Y-%m-%d'),
                "week_end": week_end.strftime('%Y-%m-%d'),
                "city": city,
                "institution": institution,
                "employee_count": len(employees),
                "reset_by": "System",
                "discord_id": "",
                "report_data": report_data,
                "archived_at": datetime.now().isoformat()
            }
            
            # Use REST API to insert into weekly_reports
            headers = {
                "apikey": SUPABASE_SYNC.key,
                "Authorization": f"Bearer {SUPABASE_SYNC.key}",
                "Content-Type": "application/json"
            }
            
            url = f"{SUPABASE_SYNC.url}/rest/v1/weekly_reports"
            response = requests.post(url, json=report_json, headers=headers)
            
            if response.status_code == 201:
                logger.info(f"✅ Saved to Supabase: {city}/{institution} ({len(employees)} employees)")
                print(f"   ✅ Saved to weekly_reports: {city}/{institution}")
                return True
            else:
                logger.warning(f"⚠️ Failed to save to Supabase: {city}/{institution} - Status: {response.status_code}")
                logger.warning(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Could not save to Supabase {city}/{institution}: {e}")
            # Don't crash if Supabase is unavailable - just log and continue
            return False
    
    def trigger_now(self):
        """Manually trigger report generation (for testing)"""
        print("\n🔔 Manual trigger for weekly report generation\n")
        self.generate_weekly_report()


# Global scheduler instance
_scheduler_instance = None

def initialize_scheduler(data_dir: str, archive_dir: str = None) -> WeeklyReportScheduler:
    """Initialize and return scheduler instance"""
    global _scheduler_instance
    
    if archive_dir is None:
        archive_dir = os.path.join(os.path.dirname(data_dir), 'arhiva')
    
    if _scheduler_instance is None:
        _scheduler_instance = WeeklyReportScheduler(data_dir, archive_dir)
    
    return _scheduler_instance

def start_scheduler():
    """Start the global scheduler"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.start()
    else:
        logger.warning("⚠️ Scheduler not initialized. Call initialize_scheduler first.")

def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()

def get_scheduler() -> WeeklyReportScheduler:
    """Get the global scheduler instance"""
    global _scheduler_instance
    return _scheduler_instance
