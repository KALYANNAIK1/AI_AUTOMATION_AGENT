const { test, expect } = require('@playwright/test');
const PageObject = require('../pages/ModernEcommerceProductSearchandBagValidationPage.js');
test.describe('Modern Ecommerce Product Search and Bag Validation', () => {

    test('TC_POS_001: Verify successful product addition to bag', async ({ page }) => {
        const pageObject = new PageObject(page);

        await pageObject.navigate("https://www.myntra.com/");
        await pageObject.waitForPageReady();
        
        await expect(await pageObject.isVisible('headerLogo')).toBeTruthy();
        await expect(await pageObject.isVisible('searchForProductsBrandsAndMore')).toBeTruthy();
        
        await pageObject.fillField('searchForProductsBrandsAndMore', 'black shirts for men');
        await pageObject.pressKey('searchForProductsBrandsAndMore', 'Enter');
        
        await pageObject.waitForElement('blackShirtsForMen');
        await expect(await pageObject.getCurrentUrl()).toContain('black-shirts-for-men');
        
        await expect(await pageObject.isVisible('raymondPureCottonFormalShirtRs1112Rs209947OFF')).toBeTruthy();
        
        await pageObject.clickAndSwitchToNewTab('raymondPureCottonFormalShirtRs1112Rs209947OFF');
        
        await pageObject.waitForPageReady();
        await expect(await pageObject.isVisible('productNameHeading')).toBeTruthy();
        await expect(await pageObject.isVisible('productPrice')).toBeTruthy();
        await expect(await pageObject.isVisible('sizeOptions')).toBeTruthy();
        
        await pageObject.selectOption('size40', '40');
        await pageObject.clickElement('addToBagButton');
        
        await pageObject.waitForElement('bagIcon');
        await expect(await pageObject.isVisible('bagIcon')).toBeTruthy();
        
        await pageObject.clickElement('bagIcon');
        await pageObject.waitForPageReady();
        
        await expect(await pageObject.isVisible('productInBagName')).toBeTruthy();
        await expect(await pageObject.isVisible('productInBagSize')).toBeTruthy();
        await expect(await pageObject.isVisible('productInBagPrice')).toBeTruthy();
        await expect(await pageObject.isVisible('removeProductButton')).toBeTruthy();
        
        await pageObject.clickElement('removeProductButton');
        await pageObject.clickElement('confirmRemoveButton');
        
        await pageObject.waitForElement('emptyBagMessage');
        await expect(await pageObject.isVisible('emptyBagMessage')).toBeTruthy();
    });

    test('TC_NEG_001: Verify search results for non-existent product', async ({ page }) => {
        const pageObject = new PageObject(page);

        await pageObject.navigate("https://www.myntra.com/");
        await pageObject.waitForPageReady();
        
        await pageObject.fillField('searchForProductsBrandsAndMore', 'nonexistentproductxyz123');
        await pageObject.pressKey('searchForProductsBrandsAndMore', 'Enter');
        
        await pageObject.waitForElement('noResultsMessage');
        await expect(await pageObject.isVisible('noResultsMessage')).toBeTruthy();
    });

    test.afterEach(async ({ page }, testInfo) => {
        if (testInfo.status !== testInfo.expectedStatus) {
            const timestamp = new Date()
                .toISOString()
                .replace(/[:.]/g, '-');
            const safeTitle = testInfo.title
                .replace(/[^a-zA-Z0-9_-]/g, '_');
            await page.screenshot({
                path: `Agent_AUTOMATION_AI/generated/screenshots/${safeTitle}_${timestamp}.png`,
                fullPage: true
            });
        }
    });
});
