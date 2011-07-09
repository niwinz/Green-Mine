var crypto = require('../libs/crypto');

exports.encrypt_password = function(raw_password) {
    return (new crypto.Hash).init("sha1").update(raw_password).digest("hex");
}
