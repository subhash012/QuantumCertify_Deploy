# QuantumCertify Security Configuration Guide

## Environment Variables Security

This document outlines the security measures implemented in QuantumCertify and how to properly configure environment variables.

## 🔒 Sensitive Information Protection

All sensitive information has been moved to environment variables to prevent accidental exposure:

### AI Service Configuration
- `GEMINI_API_KEY`: Google Gemini AI API key ⚠️ **CRITICAL - Keep Secure**

### Database Credentials
- `DB_SERVER`: Azure SQL Server hostname
- `DB_NAME`: Database name
- `DB_USERNAME`: Database username  
- `DB_PASSWORD`: Database password ⚠️ **CRITICAL - Keep Secure**
- `DB_PORT`: Database port (default: 1433)
- `DB_DRIVER`: ODBC driver specification (default: SQL+Server)

### Application Configuration
- `CONTACT_EMAIL`: Support/contact email address
- `DEVELOPER_NAME`: Developer or organization name
- `PROJECT_VERSION`: Application version number

### Security Configuration
- `SECRET_KEY`: Application secret key ⚠️ **CRITICAL - Keep Secure**
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)
- `DEBUG`: Debug mode flag (true/false)

### Environment Variables Security

1. **Never commit `.env` files**: Always add `.env` to `.gitignore`
2. **Use strong secrets**: Generate cryptographically secure keys for SECRET_KEY
3. **Rotate credentials regularly**: Change API keys, database passwords, and secret keys periodically
4. **Validate environment variables**: All required variables are validated at startup
5. **Production vs Development**: Use different configurations for different environments
6. **Debug mode**: Always set DEBUG=false in production
7. **CORS configuration**: Restrict ALLOWED_ORIGINS to your actual domains

## 🛡️ Security Best Practices

### 1. Environment File Security
```bash
# Set proper file permissions (Linux/macOS)
chmod 600 .env

# On Windows, right-click .env → Properties → Security → Advanced
# Remove inheritance and grant access only to your user account
```

### 2. Secret Key Generation
Generate a strong secret key:
```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

### 3. Database Security
- Use strong passwords (minimum 12 characters, mixed case, numbers, symbols)
- Enable Azure SQL firewall rules
- Use connection encryption (already configured)
- Regularly rotate passwords

### 4. API Key Management
- Store Gemini API keys securely
- Monitor API usage and set quotas
- Rotate keys periodically
- Never commit API keys to version control

## 📁 File Structure

```
backend/
├── .env                 # Your actual environment variables (NEVER COMMIT)
├── .env.example        # Template file (safe to commit)
└── app/
    ├── database.py     # Now uses environment variables
    └── main.py         # Configuration from environment
```

## 🚀 Production Deployment

### Environment Variable Setup

**Option 1: Docker Environment**
```dockerfile
# In your Dockerfile or docker-compose.yml
ENV DB_SERVER=your-server.database.windows.net
ENV DB_NAME=YourDatabaseName
ENV DB_USERNAME=your_username
# ... etc
```

**Option 2: Cloud Platform (Azure, AWS, etc.)**
Set environment variables in your cloud platform's configuration:
- Azure: App Service → Configuration → Application Settings
- AWS: Elastic Beanstalk → Configuration → Environment Properties
- Heroku: Settings → Config Vars

**Option 3: System Environment Variables**
```bash
# Linux/macOS
export DB_SERVER="your-server.database.windows.net"
export DB_PASSWORD="your-secure-password"

# Windows PowerShell
$env:DB_SERVER="your-server.database.windows.net"
$env:DB_PASSWORD="your-secure-password"
```

## ⚠️ Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] Database password is strong and unique
- [ ] Secret key is randomly generated and secure
- [ ] API keys are valid and have appropriate quotas
- [ ] CORS origins are restricted to your domains
- [ ] File permissions are set correctly on .env
- [ ] Environment variables are set in production
- [ ] No sensitive data in source code or logs
- [ ] Regular security updates and key rotation

## 🔧 Development vs Production

### Development
```env
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=DEBUG
```

### Production
```env
DEBUG=false
ALLOWED_ORIGINS=https://your-production-domain.com
LOG_LEVEL=WARNING
SECRET_KEY=super-secure-randomly-generated-key
```

## 📞 Support

If you have security concerns or questions:
- Email: subhashsubu106@gmail.com
- Review code for security issues
- Follow security best practices
- Report vulnerabilities responsibly

## 🔄 Regular Maintenance

1. **Monthly**: Review access logs and API usage
2. **Quarterly**: Rotate API keys and passwords
3. **Annually**: Update dependencies and security configurations
4. **As needed**: Respond to security advisories

Remember: Security is not a one-time setup but an ongoing process!