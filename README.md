# Interactive_Study_Group_Finder
SWE Project
find study group and interact
link: https://hyeonseric.github.io/Interactive_Study_Group_Finder/

To use this project:
run the mysql_setup.txt file as a script in an empty mySQL database
Download most recent "Python" code interpreter
open command window
pip install:
    fastapi
    sqlalchemy
    PyJWT
    bcrypt
run "fastapi dev main.py" in console from project file
    use "uvicorn main:app --host 127.0.0.1 --port 5000 --reload" to ensure the port is correctly set
This will initialize the uvicorn program which monitors files in the current directory for changes as well as interprets the main.py file.
Open "index.html" in your browser to begin.
From here you ca sign in as a user from the database or create a new account.

