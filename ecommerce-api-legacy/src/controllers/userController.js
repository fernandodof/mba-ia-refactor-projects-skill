const userModel = require('../models/userModel');

async function deleteUser(id) {
    const user = await userModel.findById(id);
    if (!user) {
        return { error: 'Usuário não encontrado' };
    }
    await userModel.remove(id);
    return { msg: 'Usuário e registros relacionados deletados com sucesso' };
}

module.exports = { deleteUser };
