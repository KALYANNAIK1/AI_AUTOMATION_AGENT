const { test, expect } = require('@playwright/test');
const PageObject = require('../pages/ModernEcommerceProductSearchandBagValidationPage.js');
test.describe('Modern Ecommerce Product Search and Bag Validation', () => {

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

    test('TC_MYNTRA_001: Verify successful end-to-end product flow', async ({ page }) => {
        const pageObject = new PageObject(page);

        await pageObject.navigate("https://www.myntra.com/");
        await pageObject.waitForPageReady();
        
        await expect(pageObject.isVisible('headerLogo')).toBeTruthy();
        await expect(pageObject.isVisible('searchForProductsBrandsAndMore')).toBeTruthy();
        
        await pageObject.fillField('searchForProductsBrandsAndMore', 'black shirts for men');
        await pageObject.pressKey('searchForProductsBrandsAndMore', 'Enter');
        
        await pageObject.waitForElement('blackShirtsForMen');
        await expect(pageObject.urlContains('black-shirts-for-men')).toBeTruthy();
        
        await pageObject.clickElement('arrowSlimFitOpaqueFormalShirtRs1280Rs209939OFF');
        
        await pageObject.switchToTabByUrl(/.*\/buy.*/);
        await pageObject.waitForElement('productDetailsHeader');
        
        await expect(pageObject.isVisible('productName')).toBeTruthy();
        await expect(pageObject.isVisible('productPrice')).toBeTruthy();
        await expect(pageObject.isVisible('sizeOptionsContainer')).toBeTruthy();
        
        const isSize40Available = await pageObject.isVisible('size40Option');
        if (isSize40Available) {
            await pageObject.clickElement('size40Option');
        } else {
            await pageObject.clickElement('firstAvailableSizeOption');
        }
        
        await pageObject.clickElement('addToBagButton');
        await pageObject.waitForElement('bagIconUpdated');
        
        await expect(pageObject.isVisible('bagLink')).toBeTruthy();
        await pageObject.clickElement('bagLink');
        
        await pageObject.waitForElement('shoppingBagPage');
        await expect(pageObject.isVisible('bagItemName')).toBeTruthy();
        await expect(pageObject.isVisible('bagItemSize')).toBeTruthy();
        await expect(pageObject.isVisible('bagItemPrice')).toBeTruthy();
        
        await pageObject.clickElement('removeBagItemButton');
        await pageObject.clickElement('confirmRemoveButton');
        
        await pageObject.waitForElementHidden('bagItemName');
        await expect(pageObject.isVisible('emptyBagMessage')).toBeTruthy();
    });

    test('TC_MYNTRA_004: Verify system behavior when adding an item to the bag without selecting a size', async ({ page }) => {
        const pageObject = new PageObject(page);

        await pageObject.navigate("https://www.myntra.com/");
        await pageObject.fillField('searchForProductsBrandsAndMore', 'black shirts for men');
        await pageObject.pressKey('searchForProductsBrandsAndMore', 'Enter');
        
        await pageObject.clickElement('arrowSlimFitOpaqueFormalShirtRs1280Rs209939OFF');
        await pageObject.switchToTabByUrl(/.*\/buy.*/);
        
        await pageObject.waitForElement('addToBagButton');
        await pageObject.clickElement('addToBagButton');
        
        await expect(pageObject.isVisible('sizeSelectionErrorMessage')).toBeTruthy();
    });
});
