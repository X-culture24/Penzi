
#  Penzi App - Flask & React

This project is a **USSD-based dating service** built with **Flask (backend)** and **React (frontend)**.  
It allows users to **register, find matches, and communicate** via SMS-based interactions.

---

## **🚀 Tech Stack**
### **Backend** (Flask)
- Flask
- Flask-CORS
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- psycopg2 (PostgreSQL driver)

### **Frontend** (React)
- React (with Vite)
- React Router
- Bootstrap (for UI styling)
- Axios (for API calls)


---

## **🔧 Backend Setup (Flask)**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/yourusername/penzi-app.git
cd penzi-app
```

### **2️⃣ Set Up Virtual Environment**
```bash
python3 -m venv myworld
source myworld/bin/activate  # (On Windows, use `myworld\Scripts\activate`)
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Set Up PostgreSQL Database**
- Ensure you have PostgreSQL installed.
- Create a database:
  ```sql
  CREATE DATABASE penzi_app;
  ```
- Update `app.py` with your PostgreSQL credentials:
  ```python
  app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kevin:kevin123@localhost/penzi_app"
  ```

### **5️⃣ Run Database Migrations**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### **6️⃣ Start the Flask Server**
```bash
flask run
```
By default, the API will be available at:  
**`http://127.0.0.1:5000`**

---

## **🖥️ Frontend Setup (React)**
### **1️⃣ Navigate to the Frontend Directory**
```bash
cd dating-frontend
```

### **2️⃣ Install Dependencies**
```bash
npm install
```


---

## **📦 Dependencies**
### **Backend (Flask) - `requirements.txt`**
```
Flask
Flask-CORS
Flask-SQLAlchemy
Flask-Migrate
Flask-JWT-Extended
psycopg2
```

### **Frontend (React) - `package.json`**
```json
"dependencies": {
  "axios": "^1.6.2",
  "bootstrap": "^5.3.2",
  "react": "^18.2.0",
  "react-bootstrap": "^2.9.2",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.22.1",
  "react-toastify": "^9.1.3"
}
```

---

