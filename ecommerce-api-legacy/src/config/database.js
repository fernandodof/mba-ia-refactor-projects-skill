const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');

const db = new sqlite3.Database(':memory:');

db.getAsync = promisify(db.get.bind(db));
db.allAsync = promisify(db.all.bind(db));
db.runAsync = promisify(db.run.bind(db));

async function initDb() {
    await new Promise((resolve, reject) => {
        db.serialize(() => {
            db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
            db.run("CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
            db.run("CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
            db.run("CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
            db.run("CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)", resolve);
        });
    });

    const { hashPassword } = require('./crypto');
    const seedPass = hashPassword('123');

    await db.runAsync(
        "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
        ['Leonan', 'leonan@fullcycle.com.br', seedPass]
    );
    await db.runAsync(
        "INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)",
        ['Clean Architecture', 997.00, 1, 'Docker', 497.00, 1]
    );
    await db.runAsync("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]);
    await db.runAsync(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [1, 997.00, 'PAID']
    );
}

module.exports = { db, initDb };
