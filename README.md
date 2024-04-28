# DonateWhere

## Requirements for the project
### 1) Python
### 2) Postgres
### 3) Redis

## Instructions

1. Create a new database in postgres
2. Open the file 'settings.py' and change the value of the 'SECRET_KEY'. Get a new secret key from https://djecrety.ir. Be sure not change the value of this secret key or to commit this.
3. Look up DATABASES in the 'settings.py' file and change the value of NAME, USER, PASSWORD to the values of your database
4. Open the terminal in the root directory of the project and run the command `python3 -m venv env` and `source env/bin/activate`.
5. Once the virtual environment is activated. Run the command `pip install -r requirements.txt`
6. Once the requirements for the project have been installed.
7. Migrate the models of the project to the database by executing the command `python manage.py migrate`
8. You can start the server by running the command `python manage.py runserver`


