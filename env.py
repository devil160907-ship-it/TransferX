FLASK_APP=app.py
FLASK_ENV=production

SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///transferx.db

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=evilb1310@gmail.com
MAIL_PASSWORD=tcbf ithi fxem szqv
MAIL_DEFAULT_SENDER=TransferX <evilb1310@gmail.com>

UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=104857600
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp,bmp,svg,tiff,mp4,avi,mkv,mov,webm,wmv,mpeg,mp3,wav,aac,ogg,flac,m4a,pdf,doc,docx,xls,xlsx,ppt,pptx,txt,csv,rtf,odt,ods,zip,rar,7z,tar,gz,html,css,js,json,xml,py,java,c,cpp,cs,php,go,rs,sql,md
BASE_URL=http://localhost:5000