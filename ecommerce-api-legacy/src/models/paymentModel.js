const { db } = require('../config/database');

async function create(enrollmentId, amount, status) {
    return new Promise((resolve, reject) => {
        db.run(
            "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
            [enrollmentId, amount, status],
            function (err) { err ? reject(err) : resolve({ id: this.lastID }); }
        );
    });
}

module.exports = { create };
