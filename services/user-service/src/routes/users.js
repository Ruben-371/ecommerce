'use strict';

const router = require('express').Router();
const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Auth middleware
const protect = (req, res, next) => {
  const auth = req.headers.authorization;
  if (!auth?.startsWith('Bearer '))
    return res.status(401).json({ error: 'Missing or invalid token' });

  try {
    const payload = jwt.verify(auth.split(' ')[1], process.env.JWT_SECRET);
    req.userId = payload.sub;
    next();
  } catch {
    res.status(401).json({ error: 'Invalid or expired token' });
  }
};

// GET /api/users/me
router.get('/me', protect, async (req, res, next) => {
  try {
    const user = await User.findById(req.userId);
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.json({ user });
  } catch (err) {
    next(err);
  }
});

// GET /api/users/validate  (used internally by other services)
router.get('/validate', protect, (req, res) => {
  res.json({ valid: true, userId: req.userId });
});

module.exports = router;
