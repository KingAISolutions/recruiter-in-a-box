# Recruiter In A Box

**Hire Top Talent 10x Faster**

An AI-powered SaaS recruitment platform that automates candidate sourcing, scoring, and outreach. Stop drowning in resumes and focus on finding the right fit.

![Recruiter In A Box](https://via.placeholder.com/800x400?text=Recruiter+In+A+Box)

### Pricing

| Plan | Price | Description |
|------|-------|-------------|
| **Professional** | $99/month | For individual recruiters. Up to 100 candidates/month, AI scoring, email outreach |
| **Agency** | $299/month | For recruiting teams. Unlimited candidates, 5 seats, advanced analytics, custom branding |

## Features

### Authentication
- User registration and login with JWT tokens
- Password reset functionality
- Session management

### Resume Management
- PDF resume upload with drag-and-drop
- AI-powered resume parsing
- Candidate profiles with skills, experience, education

### AI Candidate Scoring
- Skills match scoring (40% weight)
- Experience match scoring (35% weight)
- Education match scoring (25% weight)
- Overall composite score
- Scoring history tracking

### Outreach Management
- Email templates with variable interpolation
- Bulk personalized email sending
- Email tracking (sent, delivered, opened, replied)
- Email analytics and statistics

### Dashboard & Analytics
- Overview statistics
- Candidate pipeline visualization
- Hiring metrics
- Recent activity feed
- Charts and graphs

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite (Build Tool)
- Tailwind CSS
- React Router
- React Query (Server State)
- Recharts (Data Visualization)

### Backend
- Python FastAPI
- SQLAlchemy (ORM)
- Pydantic (Validation)
- JWT Authentication
- OpenAI Integration

### Database
- PostgreSQL
- SQLAlchemy Async

### Deployment
- Docker & Docker Compose
- Nginx (Production)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for development)
- Python 3.11+ (for development)

### Production Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/recruiter-in-a-box.git
cd recruiter-in-a-box
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and set your configuration:
```bash
# Generate a secure secret key
SECRET_KEY=your-super-secret-key-at-least-32-characters

# Add your OpenAI API key for AI features
OPENAI_API_KEY=sk-your-openai-api-key
```

4. Start the application:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Setup

1. Start infrastructure:
```bash
docker-compose -f docker-compose.yml up -d db
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Start backend:
```bash
cd backend
uvicorn app.main:app --reload
```

5. Start frontend:
```bash
cd frontend
npm run dev
```

## API Documentation

The API documentation is available at `/docs` (Swagger UI) or `/redoc` (ReDoc).

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/logout` | Logout user |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current user |
| PUT | `/api/auth/me` | Update current user |
| POST | `/api/auth/reset-password` | Request password reset |

### Candidate Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/candidates` | List candidates |
| POST | `/api/candidates` | Create candidate |
| GET | `/api/candidates/:id` | Get candidate |
| PUT | `/api/candidates/:id` | Update candidate |
| DELETE | `/api/candidates/:id` | Delete candidate |
| POST | `/api/candidates/upload` | Upload resume |
| PUT | `/api/candidates/:id/status` | Update status |

### Job Position Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List jobs |
| POST | `/api/jobs` | Create job |
| GET | `/api/jobs/:id` | Get job |
| PUT | `/api/jobs/:id` | Update job |
| DELETE | `/api/jobs/:id` | Delete job |

### Scoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scoring/candidate/:id` | Score candidate |
| POST | `/api/scoring/bulk` | Bulk score |
| GET | `/api/scoring/:id/history` | Score history |

### Email Template Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/templates` | List templates |
| POST | `/api/templates` | Create template |
| GET | `/api/templates/:id` | Get template |
| PUT | `/api/templates/:id` | Update template |
| DELETE | `/api/templates/:id` | Delete template |

### Outreach Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/outreach/send` | Send email |
| POST | `/api/outreach/bulk` | Bulk send |
| GET | `/api/outreach/emails` | List emails |
| GET | `/api/outreach/stats` | Email statistics |

### Dashboard Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/overview` | Overview stats |
| GET | `/api/dashboard/pipeline` | Pipeline data |
| GET | `/api/dashboard/metrics` | Hiring metrics |
| GET | `/api/dashboard/activity` | Activity log |

## Database Schema

See [SPEC.md](./SPEC.md) for the complete database schema.

## Email Template Variables

Available variables for email templates:
- `{candidate_name}` - Full name
- `{first_name}` - First name
- `{email}` - Email address
- `{position}` - Job position title
- `{company_name}` - Your company name
- `{job_title}` - Same as position
- `{department}` - Department name
- `{location}` - Job location

## Candidate Statuses

- `new` - New application
- `screening` - Being screened
- `interview` - In interview process
- `offer` - Offer extended
- `hired` - Candidate hired
- `rejected` - Not selected

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | JWT signing key (min 32 chars) |
| `OPENAI_API_KEY` | No | - | OpenAI API key for AI features |
| `OPENAI_MODEL` | No | gpt-4-turbo-preview | OpenAI model to use |
| `DEBUG` | No | false | Enable debug mode |
| `CORS_ORIGINS` | No | localhost | Allowed CORS origins |

## Testing

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm install
npm run test
```

## Project Structure

```
recruiter-in-a-box/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core configuration
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── tests/             # Tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/      # API services
│   │   └── types/        # TypeScript types
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .env.example
├── README.md
└── SPEC.md
```

## Deployment

### Docker Deployment

1. Build and start:
```bash
docker-compose up -d --build
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop:
```bash
docker-compose down
```

### Production Checklist

#### ✅ Security
- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY` (minimum 32 characters)
- [ ] Set `FRONTEND_URL` to your production domain
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Enable HTTPS (required for Stripe)
- [ ] Set up SSL certificates

#### ✅ API Keys & Services
- [ ] Configure `OPENAI_API_KEY` for AI features
- [ ] Set up Stripe account and configure price IDs:
  - `STRIPE_PRICE_PROFESSIONAL`
  - `STRIPE_PRICE_AGENCY`
- [ ] Configure `STRIPE_WEBHOOK_SECRET` for subscription events
- [ ] Set up Supabase (optional) for file storage

#### ✅ Database
- [ ] Use PostgreSQL in production
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Enable SSL connections

#### ✅ Email
- [ ] Configure SMTP settings for production
- [ ] Set up email domain verification (SPF, DKIM, DMARC)
- [ ] Configure email sending limits

#### ✅ Monitoring & Operations
- [ ] Set up application monitoring (e.g., Sentry)
- [ ] Configure log aggregation
- [ ] Set up alerts for errors and downtime
- [ ] Implement rate limiting
- [ ] Configure backup strategy

#### ✅ Stripe Webhook Setup
1. Install Stripe CLI: `brew install stripe/stripe-cli/stripe`
2. Forward webhooks: `stripe listen --forward-to localhost:8000/api/webhooks/stripe`
3. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For support, email support@recruiterinabox.com or create an issue.
