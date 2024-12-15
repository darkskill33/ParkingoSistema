#### Step-by-Step Guide to Running the ParkingoSistema Locally:

1. Clone the repository and set up a virtual environment.
2. Install dependencies via `pip install django celery redis`.
3. Make sure **SQLite** is set up in your `settings.py`.
4. Run `python manage.py migrate` to create the database.
5. Create a superuser via `python manage.py createsuperuser`.
6. Start the server with `python manage.py runserver`.
7. Log in to the admin panel at `http://127.0.0.1:8000/admin/`.

#### 1. **Clone the Repository**
   ```bash
   git clone https://github.com/darkskill33/ParkingoSistema.git
   cd ParkingoSistema
   ```

#### 2. **Set Up a Virtual Environment**
   
   **For Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **For macOS/Linux:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
