var UnitTest = function UnitTest(tests){
    this._tests = tests;
}

UnitTest.prototype.run = function() {
    for(testname in this._tests){
        console.log('---> Executing test: ', testname);
        this._tests[testname]();
    }
}

exports.UnitTest = UnitTest;
