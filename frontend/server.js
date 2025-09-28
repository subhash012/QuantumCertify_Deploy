const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

// Essential security headers middleware
app.use((req, res, next) => {
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
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