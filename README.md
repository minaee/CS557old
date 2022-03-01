# CS557 - Final Project

## 1. Setup environment and install packages

0. Create a directory and clone the project:

    <code>mkdir workspace</code>

    <code>cd workspace</code>

    <code>git clone https://github.com/minaee/CS557.git</code>

1. Create virtual environment:

    <code>python3.10 -m venv venv</code>

    make sure to activate it (linux):

    <code>source venv/bin/activate</code>
    
    <code>pip install -U pip</code>

2. Install requirements:

    <code>cd CS557</code>
    
    <code>pip install -r requirements.txt</code>


3. Install [postgresql](https://www.postgresql.org/) and [pgadmin](https://www.pgadmin.org/), [example](https://www.howtoforge.com/how-to-install-postgresql-and-pgadmin4-on-ubuntu-1804-lts/)

all of dependencies should be installed automatically. In case of any misfortune, the **requirements.txt** file contains the exact version of needed packages.

---

## 2. To run the project locally:

- cd into `workspace` directory and activate the virtual environment (Linux):

    <code>source venv/bin/activate</code>

- cd into `workspace/CS557/finalProject` directory and run the django server: 

    <code>python manage.py runserver</code>

- browse `localhost:8000/` or `127.0.0.1:8000/`
- browse `localhos:8000/admin/` to access admin area

