const { db } = require('../config/database');

async function findByEmail(email) {
    return db.getAsync("SELECT * FROM users WHERE email = ?", [email]);
}

async function findById(id) {
    return db.getAsync("SELECT id, name, email FROM users WHERE id = ?", [id]);
}

async function create(name, email, passHash) {
    const result = await new Promise((resolve, reject) => {
        db.run(
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, passHash],
            function (err) { err ? reject(err) : resolve({ id: this.lastID }); }
        );
    });
    return result;
}

async function remove(id) {
    await db.runAsync("DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)", [id]);
    await db.runAsync("DELETE FROM enrollments WHERE user_id = ?", [id]);
    await db.runAsync("DELETE FROM users WHERE id = ?", [id]);
}

module.exports = { findByEmail, findById, create, remove };
