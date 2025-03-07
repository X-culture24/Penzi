# Penzi Dating Service

Welcome to the **Penzi Dating Service** repository! This is a full-stack dating application built with **Flask** (backend) and **React** (frontend). This README will guide you through setting up, running, and navigating the app.

---
---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+** (for Flask backend)
- **React
- **npm** (Node Package Manager) 

---

## Installation
```

### 1. Set Up the Backend (Flask)

1. Navigate to the backend directory:

   ```bash
   cd matchmaker
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. Install the required Python packages:


   The `requirements.txt` file includes:
   - Flask
   - Flask-SocketIO
   - Flask-SQLAlchemy
   - Requests
   - Flask-CORS

5. Set up the database:

   - Ensure you have a database configured ( PostgreSQL)
     

6. Run database migrations (if applicable):

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

### 3. Set Up the Frontend (React)

1. Navigate to the frontend directory:

   ```bash
   cd ../penzi-app
   ```

2. Install the required npm packages:

   ```bash
   npm install
   ```


## Running the Backend (Flask)

1. Navigate to the backend directory:

   ```bash
   cd matchmaker
   ```

2. Start the Flask development server:

   ```bash
   python app.py
   ```

   By default, the backend will run on `http://localhost:5000`.

---

## Running the Frontend (React)

1. Navigate to the frontend directory:

   ```bash
   cd penzi-app
   ```

2. Start the React development server:

   ```bash
   npm start
   ```


   ```

3. The frontend will run on `http://localhost:3000`. Open this URL in your browser to access the app.

---

## Navigating the App

### Home Page
- The home page provides an overview of the Penzi Dating Service.
- Users can sign up or log in to access the app.


### Dashboard
- The dashboard displays user profiles, matches, and messages.


### Chat Feature
- Real-time chat functionality is powered by Flask-SocketIO.
- Users can send and receive messages instantly.

### Profile Management
- Users can update their profiles

---
