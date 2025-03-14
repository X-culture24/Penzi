
#  Penzi App - Flask & React

## ** Tech Stack**
=======
This project is a **USSD-based dating service** built with **Flask (backend)** and **React (frontend)**.  
It allows users to **register, find matches, and communicate** via SMS-based interactions.

---

## **🚀 Tech Stack**
>>>>>>> 1bb3a7d (fixed selfdescription,userdetails and matchrequests routes)
### **Backend** (Flask)
- Flask
- Flask-CORS
- Flask-SQLAlchemy
- Flask-Migrate
- psycopg2 (PostgreSQL driver)

### **Frontend** (React)
- React Router
- Axios (for API calls)
```

### Set Up Virtual Environment**
=======
python3 -m venv myworld
source myworld/bin/activate
```

### Install Dependencies**
=======
### **3️⃣ Install Dependencies**
>>>>>>> 1bb3a7d (fixed selfdescription,userdetails and matchrequests routes)
```bash
pip install -r requirements.tx
### Start the Flask Server**
=======
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
bb3a7d (fixed selfdescription,userdetails and matchrequests routes)
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
``
Dependencies**
=======

## **📦 Dependencies**
### **Backend (Flask) - `requirements.txt`**
```
Flask
Flask-CORS
Flask-SQLAlchemy
Flask-Migrate
psycopg2
```



---

