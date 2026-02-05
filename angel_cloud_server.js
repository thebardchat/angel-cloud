// server.js - Angel Cloud Backend Server
require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const logger = require('./utils/logger');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  next();
});

// Database connection
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => {
  logger.info('Connected to MongoDB - Angel Cloud database ready');
})
.catch((error) => {
  logger.error('MongoDB connection failed:', error);
  process.exit(1);
});

// Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/users', require('./routes/users'));
app.use('/api/messaging', require('./routes/messaging'));
app.use('/api/angels', require('./routes/angels'));
app.use('/api/ai', require('./routes/ai'));
app.use('/api/weaviate', require('./routes/weaviate'));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'Angel Cloud Backend is running',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: '1.0.0'
  });
});

// Welcome message
app.get('/', (req, res) => {
  res.json({
    message: 'Welcome to Angel Cloud API',
    description: 'Mental wellness platform where people become digital angels helping others',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      auth: '/api/auth',
      users: '/api/users',
      messaging: '/api/messaging',
      angels: '/api/angels',
      ai: '/api/ai',
      weaviate: '/api/weaviate'
    }
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  
  res.status(error.status || 500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Angel Cloud endpoint not found',
    path: req.originalUrl
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down Angel Cloud backend gracefully');
  mongoose.connection.close(() => {
    logger.info('MongoDB connection closed');
    process.exit(0);
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Angel Cloud Backend running on port ${PORT}`);
  console.log(`
  🌟 Angel Cloud Backend Started 🌟
  
  Port: ${PORT}
  Environment: ${process.env.NODE_ENV || 'development'}
  Database: ${process.env.MONGODB_URI ? 'Connected' : 'Not configured'}
  
  API Endpoints:
  - Health: http://localhost:${PORT}/health
  - Auth: http://localhost:${PORT}/api/auth
  - Angels: http://localhost:${PORT}/api/angels
  - Messaging: http://localhost:${PORT}/api/messaging
  - AI: http://localhost:${PORT}/api/ai
  - Weaviate: http://localhost:${PORT}/api/weaviate
  
  Ready to help angels support people in crisis! 😇
  `);
});

module.exports = app;