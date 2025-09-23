from apscheduler.schedulers.background import BackgroundScheduler
import time
import sys
import os
import subprocess

def main():
    """Run the scraper to generate JSON files, then upload to database."""
    
    print("NEWS CLUSTERING AND UPLOAD PIPELINE")
    print("-"*50)
    
    try:
        # Step 1: Run app.py to generate the JSON files
        print("\n1. Running app.py to generate clusters.json and articles.json...")
        print("-"*50)
        
        result = subprocess.run(
            [sys.executable, "app.py"],
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode != 0:
            print("\nError: app.py failed to run")
            sys.exit(1)
        
        print("-"*50)
        print("app.py completed successfully")
        
        # Step 2: Verify the JSON files were created
        print("\n2. Verifying JSON files were created...")
        
        if not os.path.exists("clusters.json"):
            print("Error: clusters.json was not created")
            sys.exit(1)
        
        if not os.path.exists("articles.json"):
            print("Error: articles.json was not created")
            sys.exit(1)
        
        print("Both JSON files found")
        
        # Step 3: Run transform_and_upload.py to upload data to database
        print("\n3. Running transform_and_upload.py to upload data to database...")
        print("-"*50)
        
        result = subprocess.run(
            [sys.executable, "transform_and_upload.py"],
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode != 0:
            print("\nError: transform_and_upload.py failed")
            sys.exit(1)
        
        print("-"*50)
        print("\nPipeline completed successfully!")
        print("   - Clusters and articles scraped")
        print("   - Data uploaded to database")
        
        # Step 4: Clean up JSON files
        print("\n4. Cleaning up temporary JSON files...")
        try:
            os.remove("clusters.json")
            print("   Deleted clusters.json")
        except Exception as e:
            print(f"   Warning: Could not delete clusters.json: {e}")
        
        try:
            os.remove("articles.json")
            print("   Deleted articles.json")
        except Exception as e:
            print(f"   Warning: Could not delete articles.json: {e}")
        
        print("\nAll done! Data is now in the database.")
        
    except FileNotFoundError as e:
        print(f"\nFile not found: {e}")
        print("   Make sure app.py and transform_and_upload.py are in the current directory")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

# ---- Scheduler Part ----
def my_function_to_time():
    main()
    print(f"Executing function at: {time.ctime()}")
    time.sleep(2)  # Simulate some work
    print("Function execution complete.")

def timed_execution_wrapper():
    start_time = time.time()
    my_function_to_time()
    end_time = time.time()
    execution_duration = end_time - start_time
    print(f"Execution duration: {execution_duration:.4f} seconds")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    
    # Run at the top of every hour
    scheduler.add_job(timed_execution_wrapper, trigger='cron', minute='0')
    
    scheduler.start()
    print("Scheduler started. Function will execute every hour.")
    
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler shut down.")
