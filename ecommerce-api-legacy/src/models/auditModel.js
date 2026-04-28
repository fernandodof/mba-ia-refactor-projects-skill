const { db } = require('../config/database');

async function log(action) {
    await db.runAsync(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action]
    );
}

module.exports = { log };
