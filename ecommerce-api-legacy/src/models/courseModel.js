const { db } = require('../config/database');

async function findActiveById(id) {
    return db.getAsync("SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
}

async function listAll() {
    return db.allAsync("SELECT * FROM courses", []);
}

module.exports = { findActiveById, listAll };
