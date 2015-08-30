describe('Quirell', function() {

    formName = element(by.model('formdata.name'))
    formNumber = element(by.model('formdata.number'))
    formSubmit = element(by.id('form-submit'))
    formDelete = element(by.id('form-delete'))
    formBack = element(by.id('form-back'))

    beforeEach(function() {
    });

    afterEach(function() {
    });

    it('should be named "Quirell" in the browser', function() {
        expect(browser.getTitle()).toEqual('Quirell');
    });
});
