const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

// Security middleware
app.use((req, res, next) => {
  // Security headers
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.quantumcertify.tech; frame-ancestors 'none';");
  
  next();
});

// Serve static files from build directory
app.use(express.static(path.join(__dirname, 'build')));

// Handle React Router - serve index.html for all non-asset requests
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`QuantumCertify frontend server running on port ${port}`);
  console.log(`Security headers enabled for production deployment`);
});