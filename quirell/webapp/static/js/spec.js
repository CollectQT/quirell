describe('Quirell', function() {

    beforeEach(function() {
        browser.get('http://localhost:5000');
    });

    afterEach(function() {
    });

    it('should be named "Quirell" in the browser', function() {
        expect(browser.getTitle()).toEqual('Quirell');
    });

    it('should allow you to navigate to the login screen from the homepage', function() {
        element(by.linkText('Login / Signup')).click()
        expect(browser.getTitle()).toEqual('Login / Signup | Quirell');
    })

    it('should not allow you to view the /profile page while logged out', function() {
        browser.get('http://localhost:5000/profile')
        expect(browser.getTitle()).toEqual('ERROR 401');
    })

});
