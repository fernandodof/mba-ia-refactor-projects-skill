const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(32).toString('hex');
    const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha256').toString('hex');
    return `${salt}:${hash}`;
}

function verifyPassword(plain, stored) {
    const [salt, hash] = stored.split(':');
    const candidate = crypto.pbkdf2Sync(plain, salt, 100000, 64, 'sha256').toString('hex');
    return hash === candidate;
}

module.exports = { hashPassword, verifyPassword };
