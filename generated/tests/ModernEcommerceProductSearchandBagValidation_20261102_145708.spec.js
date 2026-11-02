const { test, expect } = require('@playwright/test');
const PageObject = require('../pages/ModernEcommerceProductSearchandBagValidationPage.js');
test.describe('Modern Ecommerce Product Search and Bag Validation', () => {

    test('TC_MYNTRA_001: Verify search results display when entering valid keyword', async ({ page }) => {
        const pageObject = new PageObject(page);

        await pageObject.navigate('https://www.myntra.com/');
        await pageObject.waitForPageReady();
        
        await pageObject.isVisible('headerLogo');
        await pageObject.isVisible('searchForProductsBrandsAndMore');
        
        await pageObject.fillField('searchForProductsBrandsAndMore', 'black shirts for men');
        await pageObject.pressKey('searchForProductsBrandsAndMore', 'Enter');
        
        await pageObject.waitForElement('blackShirtsForMen');
        const isUrlValid = await pageObject.urlContains('black-shirts-for-men');
        expect(isUrlValid).toBeTruthy();
        
        await pageObject.isVisible('arrow');
        const searchResultsCount = await pageObject.isVisible('highlander');
        expect(searchResultsCount).toBeTruthy();
    });

    test('TC_MYNTRA_002: Verify Add to Bag functionality and removal', async ({ page }) => {
        const pageObject = new PageObject(page);

        await pageObject.navigate('https://www.myntra.com/');
        await pageObject.fillField('searchForProductsBrandsAndMore', 'black shirts for men');
        await pageObject.pressKey('searchForProductsBrandsAndMore', 'Enter');
        
        await pageObject.clickElement('highlanderMenSlimFitShirt');
        await pageObject.switchToTabByUrl('https://www.myntra.com/');
        
        await pageObject.waitForPageReady();
        
        const productName = await pageObject.isVisible('productTitle');
        const productPrice = await pageObject.isVisible('productPrice');
        expect(productName).toBeTruthy();
        expect(productPrice).toBeTruthy();

        const size40 = 'size40';
        const isSize40Visible = await pageObject.isVisible(size40);
        if (isSize40Visible) {
            await pageObject.clickElement(size40);
        } else {
            await pageObject.clickElement('firstAvailableSize');
        }

        await pageObject.clickElement('addToBagButton');
        await pageObject.waitForElement('bagIcon');
        
        await pageObject.clickElement('bagIcon');
        await pageObject.waitForElement('bagPageContainer');
        
        await pageObject.isVisible('bagItemName');
        await pageObject.isVisible('bagItemSize');
        await pageObject.isVisible('bagItemPrice');
        
        await pageObject.clickElement('removeBagItemButton');
        await pageObject.clickElement('confirmRemoveButton');
        
        await pageObject.waitForElementHidden('bagItemName');
        await pageObject.isVisible('emptyBagMessage');
    });

    test.afterEach(
        async ({ page }, testInfo) => {
    
            if (
                testInfo.status !==
                testInfo.expectedStatus
            ) {
    
                const timestamp = new Date()
                    .toISOString()
                    .replace(/[:.]/g, '-');
    
                const safeTitle = testInfo.title
                    .replace(/[^a-zA-Z0-9_-]/g, '_');
    
                await page.screenshot({
                    path:
                        `Agent_AUTOMATION_AI/generated/screenshots/${safeTitle}_${timestamp}.png`,
                    fullPage: true
                });
    
            }
    
        }
    );
});
