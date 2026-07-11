# TransferX

> **A Modern Flask-Based Email & File Sharing Platform**

TransferX is a professional web application built with **Flask** that enables users to compose emails, manage drafts, upload attachments, verify accounts, recover passwords, and manage users through an intuitive admin dashboard. Designed with a responsive interface and modular architecture, it is suitable for learning, customization, and deployment.

---

# Features

## User Authentication

* User Registration
* Secure Login
* Logout
* Email Verification
* Forgot Password
* Password Reset via Email
* Session Management

## Email Management

* Compose Emails
* Rich Email Content
* File Attachments
* Send Emails
* Draft Saving
* View Sent Emails
* Public Email View
* Email Details Page

## Notifications

* In-App Notifications
* Notification History

## User Profile

* View Profile
* Update Profile Information

## Admin Panel

* Dashboard Overview
* User Management
* Email Monitoring
* System Statistics

## Security

* Password Hashing
* Protected Routes
* Email Verification
* Environment Variable Support

## Responsive Design

* Desktop Friendly
* Tablet Friendly
* Mobile Friendly

---

# Technology Stack

| Component      | Technology            |
| -------------- | --------------------- |
| Backend        | Python                |
| Framework      | Flask                 |
| Database       | SQLite                |
| Frontend       | HTML, CSS, JavaScript |
| Templates      | Jinja2                |
| Authentication | Flask Sessions        |
| Email          | SMTP                  |
| Styling        | Custom CSS            |

---

# Project Structure

```text
TransferX/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/
│   └── favicon.ico
│
├── templates/
│   ├── auth/
│   ├── dashboard/
│   ├── emails/
│   ├── public/
│   └── base.html
│
├── admin.py
├── app.py
├── auth.py
├── config.py
├── email_service.py
├── extensions.py
├── models.py
├── notifications.py
├── routes.py
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

---

# Requirements

* Python 3.11 or newer
* pip
* Virtual Environment (recommended)

---

# Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Open the Project

```bash
cd TransferX
```

### 3. Create a Virtual Environment

Windows

```bash
python -m venv venv
```

Linux/macOS

```bash
python3 -m venv venv
```

### 4. Activate the Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file using the provided `.env.example`.

Example:

```env
SECRET_KEY=your_secret_key

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

DATABASE_URL=sqlite:///transferx.db
```

> **Never commit your actual `.env` file or credentials.**

---

# Running the Project

Start the application using:

```bash
python run.py
```

Open your browser and navigate to:

```
http://127.0.0.1:5000
```

---

# Email Configuration

TransferX uses SMTP for sending emails.

Recommended SMTP settings:

* SMTP Server
* SMTP Port
* TLS/SSL
* Email Address
* App Password

You can use providers such as Gmail, Outlook, Zoho Mail, or any SMTP-compatible email service.

---

# Screenshots

Add screenshots before publishing your project.

Suggested screenshots:

* Login Page
* Registration Page
* Dashboard
* Compose Email
* Sent Emails
* Drafts
* Email Details
* Notifications
* User Profile
* Admin Dashboard
* Mobile View

---

# Future Enhancements

Potential improvements include:

* Dark Mode
* Two-Factor Authentication (2FA)
* OAuth Login
* Email Scheduling
* REST API
* Multiple Themes
* Cloud Storage Integration
* Activity Logs
* Multi-language Support
* Advanced Search
* Bulk Email Support

---

# Troubleshooting

### Emails are not sending

* Verify SMTP credentials.
* Ensure App Passwords are enabled (if required).
* Check firewall/network restrictions.

### Database issues

* Verify the database path.
* Ensure the database file exists.
* Check file permissions.

### Module not found

Run:

```bash
pip install -r requirements.txt
```

---

# FAQ

### Can I use this project commercially?

Yes, subject to the included license.

### Can I customize the UI?

Yes. All templates and static assets can be modified.

### Can I replace SQLite?

Yes. The project architecture can be adapted for databases such as PostgreSQL or MySQL with appropriate configuration changes.

---

# Support

If you encounter any issues or have questions regarding installation or customization, please contact the seller through the platform where you purchased the project.

---

# License

This project is distributed under the terms specified in the included **LICENSE** file.

---

# Credits

Developed using:

* Python
* Flask
* HTML5
* CSS3
* JavaScript
* SQLite
* Jinja2

---

# Thank You

Thank you for choosing **TransferX**.

If this project helps you, consider leaving a positive review and sharing your feedback. Your support is greatly appreciated.
