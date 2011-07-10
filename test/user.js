var tests = {
    'test_sample1': function() {
        console.log('1');

    },

    'test_sample2': function() {
        console.log('2');
    }
}

var unittest = require('../utils/test');
(new unittest.UnitTest(tests)).run();
