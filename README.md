<p align="center">
    <img width="200" src="https://github.com/Prome-theus/django-assignment/assets/80052733/e768091a-a844-48c4-8fc0-e5a9bc3bd83d">
</p>

If you like my work, consider buying me a coffee! ☕️
<div align="center">
<a href="https://www.buymeacoffee.com/bogusdeck" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" width="150" />
</a>
</div>


## Django TaskReward

Django Web Application: Task Reward System

## Overview

This project is a simple web application built using Django, Django REST Framework, and Tailwind CSS. It allows administrators to add tasks (app details) with associated points, and users can earn points by downloading the app and uploading a screenshot.

## Features

- **Task Management**: Admins can add tasks with details such as app name, link, category, subcategory, points, and logo.
- **User Authentication**: Implemented using Django REST Framework for login and authentication.
- **Drag and Drop**: Utilizes drag and drop feature for smooth uploading of screenshots.
- **Dynamic Forms**: JavaScript is used to handle dynamic forms for task creation.
- **API Endpoints**: Django REST Framework is used to create API endpoints for user login and authentication.
- **Frontend Styling**: Tailwind CSS CDN is used for frontend styling.

## ER Diagram
```markdown
+------------------+             +----------------------+             +----------------------+
|       User       |             |        Task          |             |      user_task       |
+------------------+             +----------------------+             +----------------------+
| id (PK)          |   0..*      | id (PK)              |   0..*      | id (PK)              |
| email (unique)   | <---------  | name (unique)        | <---------  | user_id (FK)         |
| fname            |             | link                 |             | task_id (FK)         |
| lname            |             | category              |             +----------------------+
| date_joined      |             | subcategory          |             
| is_active        |             | points               |   
| is_staff         |             | logo                 |
| points           |             +----------------------+
| ifLogged         |              
| token            |              
+------------------+
```

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Frontend**: HTML, CSS (Tailwind CSS)
- **Database**: SQLite (default in Django)
- **JavaScript**: Vanilla JavaScript
- **API**: Django REST Framework

## Installation

1. Clone the repository: `git clone https://github.com/your/repository.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Run the server: `python manage.py runserver`

## Usage

1. Access the admin panel to add tasks: `http://localhost:8000/admin`
2. admin credientials is inside the urls.py file 
3. Use the provided API endpoints for user login and authentication.
4. Access the web application frontend to view and interact with tasks.
5. Download the app associated with a task and upload a screenshot to earn points.

## Contributing

Contributions are welcome! Feel free to open a pull request or submit an issue for any bugs or feature requests.

## License

This project is licensed under the [MIT License](LICENSE).
