FreeUltraCV - Professional Resume Builder
==========================================

A free, production-ready CV/resume maker website with AI-powered features.

## Features

### User Features
- 🔐 Secure authentication (JWT)
- 📝 Step-by-step CV builder
- 🤖 AI resume content generator
- ✨ Grammar & skill suggestions
- 📊 ATS score checker
- 💾 Multiple export formats (PDF, DOCX, PNG)
- 🔗 Shareable resume links
- 📱 Fully responsive design

### Admin Features
- 👥 User management
- 📈 Download statistics
- 🎨 Template management
- ⚙️ Feature toggles
- 🔒 Security dashboard

## Tech Stack

### Frontend
- HTML5, CSS3 (Glassmorphism + Neumorphism)
- JavaScript (ES6+)
- Fully responsive design

### Backend
- Python (Flask)
- REST API
- JWT Authentication

### Database
- PostgreSQL (Production)
- SQLite (Development)

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+ (optional)
- PostgreSQL 13+ (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/FreeUltraCV.git
cd FreeUltraCV
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

4. Configure environment:
```bash
cp backend/.env.example backend/.env
# Edit .env with your settings
```

5. Initialize database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run development server:
```bash
cd backend
python app.py
```

7. Access the application:
- Frontend: http://localhost:5000
- API: http://localhost:5000/api

## Project Structure

```
FreeUltraCV/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment template
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── database/           # Database schema
├── frontend/               # Frontend files
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # User dashboard
│   ├── builder.html        # CV builder
│   ├── preview.html        # Resume preview
│   ├── admin.html          # Admin panel
│   ├── assets/             # Static assets
│   └── templates/          # Resume templates
├── admin_panel/            # Admin panel files
├── deployment/             # Deployment configs
├── README.md              # This file
├── LICENSE                # MIT License
└── .gitignore             # Git ignore rules
```

## API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

### Resume Management
- `GET /api/resumes` - List user resumes
- `POST /api/resumes` - Create resume
- `GET /api/resumes/<id>` - Get resume
- `PUT /api/resumes/<id>` - Update resume
- `DELETE /api/resumes/<id>` - Delete resume

### AI Tools
- `POST /api/ai/generate` - Generate resume content
- `POST /api/ai/suggest` - Get suggestions
- `POST /api/ai/ats-check` - ATS score check

### Export
- `POST /api/export/pdf` - Export as PDF
- `POST /api/export/docx` - Export as DOCX
- `POST /api/export/png` - Export as PNG

## Resume Templates

1. **Modern** - Clean, professional design
2. **Professional** - Traditional corporate style
3. **Creative** - Eye-catching unique layout
4. **ATS-Optimized** - Designed for applicant tracking systems
5. **Dark** - Modern dark theme design

## Deployment

### Production (VPS)
See [deployment/nginx.conf](deployment/nginx.conf) and [deployment/install.sh](deployment/install.sh)

### Docker
```bash
docker-compose up -d
```

### Heroku
```bash
heroku create
git push heroku main
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key | Required |
| DATABASE_URL | Database connection | sqlite:///freultracv.db |
| JWT_SECRET_KEY | JWT secret key | Required |
| JWT_ACCESS_TOKEN_EXPIRES | Token expiration | 24 hours |
| AI_API_KEY | AI service API key | Optional |
| MAIL_SERVER | SMTP server | localhost |
| MAIL_PORT | SMTP port | 587 |

## Security Features

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ CSRF protection
- ✅ XSS prevention
- ✅ Rate limiting
- ✅ Input sanitization
- ✅ Secure headers

## Performance

- ✅ Lighthouse score 90+
- ✅ Lazy loading
- ✅ Optimized images
- ✅ Fast PDF rendering

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email mahdiislam237@gmail.com or open an issue.

---

Built with ❤️ by MAHDI Team

