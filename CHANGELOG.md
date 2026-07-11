# Changelog

All notable changes to TransferX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
#### Authentication
- User registration with validation
- User login with remember me option
- User logout functionality
- Email verification system
- Password reset via email
- Resend verification email
- Username and email availability checks

#### Email Features
- Compose and send emails with attachments
- Multiple recipients support (CC, BCC)
- Rich text email body (HTML support)
- Draft management (save, edit, delete, send)
- Sent emails history with search
- Public email viewer with token-based access
- Email resend functionality
- Bulk delete emails

#### File Management
- File attachments for emails
- Support for multiple file types:
  - Images (jpg, jpeg, png, gif, webp, etc.)
  - Videos (mp4, avi, mkv, mov, etc.)
  - Audio (mp3, wav, aac, etc.)
  - Documents (pdf, doc, xls, ppt, etc.)
  - Archives (zip, rar, 7z, etc.)
  - Code files (html, css, js, py, etc.)
- File preview (for supported types)
- File download with original filename
- Storage usage tracking
- Automatic file type detection

#### User Features
- User profile management
- Profile information update
- Password change with current password verification
- Notification system with:
  - Real-time notifications
  - Mark as read/unread
  - Notification count badge
  - Notification deletion
  - Mark all as read

#### Admin Features
- Admin dashboard with statistics:
  - Total users and active users
  - Total emails and attachments
  - Total storage usage
  - Recent users and emails
- User management:
  - View all users
  - Toggle user activation
  - Delete users
  - View user details
- Email monitoring:
  - View all emails
  - Search emails
  - Delete emails
- Attachment management:
  - View attachment statistics
  - Category-based filtering
- Storage statistics
- Activity logs

#### Security
- Password hashing with Werkzeug
- CSRF protection (Flask-WTF)
- Login required decorators
- Admin-only route protection
- Session management with Flask-Login
- Secure cookie settings
- Environment variable configuration
- File upload validation and sanitization
- Input validation and sanitization

#### User Interface
- Responsive design for all devices
- Modern dashboard design
- Mobile-friendly interface
- Bootstrap 5 integration
- Professional color scheme
- Intuitive navigation
- Loading indicators
- Toast notifications
- Modal confirmation dialogs

### Improved
- Email handling performance
- Database query optimization
- File upload handling
- Error handling and logging
- User experience
- Code organization and structure
- Security best practices

### Fixed
- SMTP connection issues
- Attachment handling edge cases
- Database session management
- Validation improvements
- Token expiration handling
- Email template rendering

## [0.9.0] - 2024-01-01

### Added (Beta)
- Core authentication system
- Basic email sending functionality
- Simple file attachment support
- Draft system
- Admin panel
- Notification system
- Database models

### Known Issues
- File upload progress indicator missing
- Mobile layout issues on some pages
- SMTP error handling needs improvement

## [0.8.0] - 2023-12-15

### Added (Alpha)
- Initial project structure
- Flask application setup
- Basic database configuration
- User model
- Authentication routes
- Simple dashboard

### Security
- Basic CSRF protection
- Password hashing
- Login protection