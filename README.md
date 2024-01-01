# Attendance Tracking System Using Face Recognition

## Overview

This project is an Attendance Tracking System developed as a university project, utilizing face recognition technology. The system is designed to automate the process of employee check-in and check-out, as well as calculate the total worked hours based on facial recognition.

## Features

- **Face Recognition:** Utilizes facial recognition to identify and authenticate employees.
- **Webcam Integration:** Captures images from webcams to perform face recognition.
- **Check-In and Check-Out:** Records employee attendance by marking their entry and exit times.
- **Worked Hours Calculation:** Automatically calculates the total worked hours for each employee.
- **Database Integration:** Stores attendance records in a PostgreSQL database for future reference.

## Technologies Used

- **Python:** The core programming language used for developing the system.
- **OpenCV:** Employed for webcam integration and image processing.
- **dlib:** Utilized for facial landmark detection and recognition.
- **PostgreSQL:** The chosen relational database for storing attendance data.

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/attendance-tracking.git
2. **Database Setup:**
  Create a PostgreSQL database.
  Update the configuration in config.py accordingly.
5. **Run the Application:**
   ```bash
   python main.py
## Configuration:
1. Update the database connection details and other configurations in the config.py file to suit your environment.
   ```bash
   DB_HOST = 'your_database_host'
   DB_PORT = 'your_database_port'
   DB_NAME = 'your_database_name'
   DB_USER = 'your_database_user'
   DB_PASSWORD = 'your_database_password'
2. Usage:
Run the application, and it will start capturing images from the webcam.
Employees can check in and check out by having their faces recognized.
The system will automatically calculate the worked hours and store the attendance records in the database.
