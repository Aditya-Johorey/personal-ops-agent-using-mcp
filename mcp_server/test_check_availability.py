from dotenv import load_dotenv
load_dotenv()

from google_calendar import check_availability

if __name__ == "__main__":
    date = input("Enter a date (YYYY-MM-DD): ")
    slots = check_availability(date)
    print("Free slots:", slots)