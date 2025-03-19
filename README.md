# Signiva - Digital Document Signing Platform

Signiva is a web-based platform that enables users to upload, manage, and digitally sign documents. It provides a secure and efficient way to handle document signatures and approvals.

## Features

### Document Management
- Upload PDF documents
- View document list and details
- Edit document properties
- Delete documents
- Download signed documents

### Signature System
- Add signature boxes to documents
- Request signatures from others via email
- Digital signature placement
- Signature status tracking
- Multiple signature support

### User Management
- User registration and authentication
- Profile management
- Password change functionality
- Secure login/logout

### Dashboard
- Overview of recent documents
- Pending signature requests
- Signed documents
- Document statistics

## Tech Stack

- **Backend**: Django 4.2
- **Frontend**: HTML, Tailwind CSS
- **Database**: SQLite (default)
- **File Storage**: Local storage
- **Email**: Django's built-in email system

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/signiva.git
cd signiva
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
DEBUG=True
SECRET_KEY=your-secret-key
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
signiva/
├── manage.py
├── requirements.txt
├── .env
├── signiva/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── web/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── utils.py
    └── templates/
        ├── layout.html
        ├── index.html
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── profile.html
        ├── document_list.html
        ├── upload_document.html
        ├── view_document.html
        ├── edit_document.html
        └── delete_document.html
```

## Usage

### User Registration
1. Visit the registration page
2. Fill in username, email, and password
3. Submit the form to create an account

### Document Management
1. Log in to your account
2. Navigate to the dashboard
3. Click "Upload Document" to add a new document
4. Use the document list to view, edit, or delete documents

### Requesting Signatures
1. Open a document
2. Click "Request Signature"
3. Enter the signer's email address
4. The signer will receive an email with a link to sign the document

### Signing Documents
1. Click the signature request link in the email
2. View the document
3. Add your signature
4. Submit the signed document

## Security Features

- Password hashing
- CSRF protection
- Secure file handling
- Email verification
- Session management
- Input validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Django framework
- Tailwind CSS
- All contributors and users of the platform
