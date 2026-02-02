from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import get_db
from app.routes.auth import router as auth
from app.routes.registration import router as registration
from app.routes.users import router as users
from app.routes.accounting import router as accounting
from app.routes.crm import router as crm
from app.routes.invoices import router as invoices
from app.routes.dashboard import router as dashboard
from app.routes.dashboard_enhanced import router as dashboard_enhanced
from app.routes.templates import router as templates
from app.routes.simple_ml import router as simple_ml
from app.routes.tasks import router as tasks
from app.routes.kpi_population import router as kpi_population
from app.routes.email_verification import router as email_verification
from app.routes.drafts import router as drafts
from app.routes.usage import router as usage

from app.config import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="BizCore SaaS API",
    description="SaaS platform for Uzbekistan SMEs - Accounting, CRM, and Invoicing",
    version="1.0.0"
)

# Set up rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Trusted Host middleware - Prevents Host header attacks
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "localhost",
        "127.0.0.1", 
        "biznesassistant.uz",
        "www.biznesassistant.uz",
        "*.biznesassistant.uz"  # Allow subdomains
    ]
)

# Security Headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Force HTTPS in production
    if not (request.client.host.startswith("localhost") or request.client.host.startswith("127.0.0.1")):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    # Content Security Policy
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Allow inline scripts for React
        "style-src 'self' 'unsafe-inline'",  # Allow inline styles for Tailwind
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'"
    ]
    response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
    
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions policy
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
        "magnetometer=(), gyroscope=(), accelerometer=(), autoplay=()"
    )
    
    return response

# CORS middleware configuration - Secure but flexible
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:3001",  # Alternative React port
        "http://127.0.0.1:3000",  # Localhost alternative
        "https://biznesassistant.uz",  # Production domain
        "https://www.biznesassistant.uz",  # WWW subdomain
        "https://your-app-name.netlify.app",  # Netlify preview/production
        # Add your staging domain here when ready
        # "https://staging.biznesassistant.uz",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth, prefix="/api/auth", tags=["Authentication"])
app.include_router(registration, prefix="/api/registration", tags=["Registration"])
app.include_router(users, prefix="/api/users", tags=["Users"])
app.include_router(accounting, prefix="/api/accounting", tags=["Accounting"])
app.include_router(crm, prefix="/api/crm", tags=["CRM"])
app.include_router(invoices, prefix="/api/invoices", tags=["Invoices"])
app.include_router(dashboard, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(dashboard_enhanced, prefix="/api/analytics", tags=["Analytics"])
app.include_router(templates, prefix="/api/templates", tags=["Templates"])
app.include_router(simple_ml, prefix="/api/ml", tags=["Machine Learning"])
app.include_router(tasks, prefix="/api/tasks", tags=["Tasks"])
app.include_router(kpi_population, prefix="/api/kpi", tags=["KPI Population"])
app.include_router(email_verification, prefix="/api/email", tags=["Email Verification"])
app.include_router(drafts, prefix="/api/drafts", tags=["Drafts"])
app.include_router(usage, prefix="/api/usage", tags=["Usage"])

@app.get("/")
async def root():
    return {"message": "BizCore SaaS API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
