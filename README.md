# Repository for UCD COMP30910 (2023)
## *Data Center Dashboard*

**Student Name**: Nicholas Hamm

**Student Number**: 19439854

---
### Overview

The aim of this project is to highlight the significant energy consumption of data centres (DC) and develop a dashboard to analysis the cost of their carbon footprint and electricity consumption. This dashboard is developed as a web application to provide administrators of smaller scale DCs with a toolkit that will improve their insight of not only their hourly electricity consumption but the hourly carbon emissions as well. The dashboard utilises the capabilities of the Papillon software in conjunction with Django to calculate the varying hourly tariffs (both carbon and cost tariffs) of hosts running in the DC, offering financial and ecological understanding.

---
### Previous Work

Sengments of code have been adapted from *Daniel Houlihan's* FYP which also utilises the Papillon system.
- **Source**: https://csgitlab.ucd.ie/danielhoulihan/fyp_datacenter_management 

---
### PAPILLON
- [PAPILLON](https://www.beeyon.com/)
---
### Python

- [Python 3.7+](https://www.python.org/downloads/release/python-370/)

---
### Python Requirements

All requirements can be installed from the requirements.txt file, which includes:
- Django
- numpy
- matplotlib
- pandas
- requests
---

## How to Run the **Data Center Dashboard** Application:

Naviagte to the 'app' directory where the Django application is stored:
```
cd app
```

Install the Python requirements
```
pip3 install -r requirements.txt
```

Once the requirements are installed, the app can start running
```
python3 manage.py runserver
```

Django web application available at http://localhost:8000

The data center with PAPILLON installed must also be running and available for the dashboard to communicate via it's IP address 
---

## Dashboard Screenshots

Home Page

![](/screenshots/home.png)

Tags Page

![](/screenshots/tag.png)

Analysis Page

![](/screenshots/analysis.png)