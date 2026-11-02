const { test, expect } = require('@playwright/test');
const PageObject = require('../pages/ModernEcommerceProductSearchandBagValidationPage.js');
test.describe('Modern Ecommerce Product Search and Bag Validation', () => {

    test('TC_POS_001: Verify successful flow of searching, adding, and removing a black shirt in size 40', async ({ page }) => {
        const pageObject = new PageObject(page);

        await pageObject.navigate("https://www.myntra.com/");
        await pageObject.waitForPageReady();

        await expect(pageObject.isVisible('headerLogo')).toBeTruthy();
        await expect(pageObject.isVisible('searchForProductsBrandsAndMore')).toBeTruthy();

        await pageObject.fillField('searchForProductsBrandsAndMore', 'black shirts for men');
        await pageObject.pressKey('searchForProductsBrandsAndMore', 'Enter');

        await pageObject.waitForUrl('**/black-shirts-for-men**');
        await expect(pageObject.isVisible('blackShirtsForMen')).toBeTruthy();

        await pageObject.clickElement('arrowSlimFitOpaqueFormalShirtRs1280Rs209939OFF');
        
        await pageObject.switchToTabByUrl('**/arrow-slim-fit-opaque-formal-shirt**');
        
        await expect(pageObject.isVisible('productName')).toBeTruthy();
        await expect(pageObject.isVisible('productPrice')).toBeTruthy();
        await expect(pageObject.isVisible('sizeOptionsContainer')).toBeTruthy();

        const isSize40Available = await pageObject.isVisible('size40Button');
        if (isSize40Available) {
            await pageObject.clickElement('size40Button');
        } else {
            await pageObject.clickElement('firstAvailableSizeButton');
        }

        await expect(pageObject.isVisible('addToBagButton')).toBeTruthy();
        await pageObject.clickElement('addToBagButton');

        await pageObject.waitForElement('bagIcon');
        await expect(pageObject.isVisible('bagIcon')).toBeTruthy();
        
        await pageObject.clickElement('bagIcon');
        
        await pageObject.waitForPageReady();
        await expect(pageObject.isVisible('bagProductItem')).toBeTruthy();
        await expect(pageObject.isVisible('bagProductName')).toBeTruthy();
        await expect(pageObject.isVisible('bagSelectedSize')).toBeTruthy();
        await expect(pageObject.isVisible('bagProductPrice')).toBeTruthy();
        await expect(pageObject.isVisible('removeActionButton')).toBeTruthy();

        await pageObject.clickElement('removeActionButton');
        await pageObject.clickElement('confirmRemoveButton');

        await pageObject.waitForElementHidden('bagProductItem');
        await expect(pageObject.isVisible('emptyBagMessage')).toBeTruthy();
    });

    test('TC_NEG_001: Verify search results for an invalid or non-existent product keyword', async ({ page }) => {
        const pageObject = new PageObject(page);

        await pageObject.navigate("https://www.myntra.com/");
        await pageObject.fillField('searchForProductsBrandsAndMore', 'xyz123nonexistentproduct');
        await pageObject.pressKey('searchForProductsBrandsAndMore', 'Enter');

        await pageObject.waitForElement('noResultsFoundMessage');
        await expect(pageObject.isVisible('noResultsFoundMessage')).toBeTruthy();
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
