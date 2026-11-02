class PageObject {

    constructor(page) {

        this.page = page;

        this.defaultTimeout = 20000;
        this.navigationTimeout = 30000;
        this.assertionTimeout = 15000;

        this._resolveLocator = (
            locatorName
        ) => {

            if (!locatorName) {
                return null;
            }

            if (this[locatorName]) {
                return this[locatorName];
            }

            const normalized = String(
                locatorName
            )
                .toLowerCase()
                .replace(
                    /[^a-z0-9]/g,
                    ''
                );

            for (
                const propertyName
                of Object.keys(this)
            ) {

                if (
                    propertyName === 'page'
                    || propertyName ===
                        '_resolveLocator'
                    || propertyName ===
                        'defaultTimeout'
                    || propertyName ===
                        'navigationTimeout'
                    || propertyName ===
                        'assertionTimeout'
                ) {
                    continue;
                }

                const candidate = propertyName
                    .toLowerCase()
                    .replace(
                        /[^a-z0-9]/g,
                        ''
                    );

                if (
                    candidate === normalized
                ) {
                    return this[propertyName];
                }

            }

            const semanticButtonName = String(
                locatorName
            ).match(/^(.+?)Button$/i);

            if (semanticButtonName) {
                const buttonName = semanticButtonName[1]
                    .replace(
                        /([a-z0-9])([A-Z])/g,
                        '$1 $2'
                    )
                    .replace(
                        /[_-]+/g,
                        ' '
                    )
                    .trim();

                if (buttonName) {
                    const accessibleName =
                        buttonName[0].toUpperCase()
                        + buttonName.slice(1);

                    return this.page.getByRole(
                        'button',
                        {
                            name: accessibleName,
                            exact: true
                        }
                    );
                }
            }

            return null;
        };

        this.onlineSHOPPINGMADEEASYATMYNTRA = page.getByText("ONLINE SHOPPING MADE EASY AT MYNTRA", { exact: true }).first();
        this.bestONLINESHOPPINGSITEININDIAFORFASHION = page.getByText("BEST ONLINE SHOPPING SITE IN INDIA FOR FASHION", { exact: true }).first();
        this.affordableFASHIONATYOURFINGERTIPS = page.getByText("AFFORDABLE FASHION AT YOUR FINGERTIPS", { exact: true }).first();
        this.myntraINSIDER = page.getByText("MYNTRA INSIDER", { exact: true }).first();
        this.myntraStudioThePersonalisedFashionFeedYouWouldnTWantToMissOutOn = page.getByText("Myntra Studio - The Personalised Fashion Feed You Wouldn’t Want To Miss Out On", { exact: true }).first();
        this.myntraAPP = page.getByText("MYNTRA APP", { exact: true }).first();
        this.historyOFMYNTRA = page.getByText("HISTORY OF MYNTRA", { exact: true }).first();
        this.shopONLINEATMYNTRAWITHCOMPLETECONVENIENCE = page.getByText("SHOP ONLINE AT MYNTRA WITH COMPLETE CONVENIENCE", { exact: true }).first();
        this.img4 = page.locator("img").first();
        this.searchForProductsBrandsAndMore = page.getByPlaceholder("Search for products, brands and more");
        this.item1Button = page.getByText("1", { exact: true }).first();
        this.item2Button = page.getByText("2", { exact: true }).first();
        this.item3Button = page.getByText("3", { exact: true }).first();
        this.item4Button = page.getByText("4", { exact: true }).first();
        this.headerLogo = page.locator("[class~=\"sprites-headerLogo\"]").first();
        this.men = page.getByText("MEN", { exact: true }).first();
        this.women = page.getByText("WOMEN", { exact: true }).first();
        this.kids = page.getByText("KIDS", { exact: true }).first();
        this.home = page.getByText("HOME", { exact: true }).first();
        this.beauty = page.getByText("BEAUTY", { exact: true }).first();
        this.genz = page.getByText("GENZ", { exact: true }).first();
        this.studio = page.getByText("STUDIO", { exact: true }).first();
        this.a437 = page.locator("a").first();
        this.onlineSHOPPING = page.getByText("ONLINE SHOPPING", { exact: true }).first();
        this.men2 = page.getByText("Men", { exact: true }).first();
        this.women2 = page.getByText("Women", { exact: true }).first();
        this.kids2 = page.getByText("Kids", { exact: true }).first();
        this.home2 = page.getByText("Home", { exact: true }).first();
        this.beauty2 = page.getByText("Beauty", { exact: true }).first();
        this.genz2 = page.getByText("Genz", { exact: true }).first();
        this.giftCards = page.getByText("Gift Cards", { exact: true }).first();
        this.myntraInsider = page.getByText("Myntra Insider", { exact: true }).first();
        this.blog = page.getByText("Blog", { exact: true }).first();
        this.careers = page.getByText("Careers", { exact: true }).first();
        this.siteMap = page.getByText("Site Map", { exact: true }).first();
        this.corporateInformation = page.getByText("Corporate Information", { exact: true }).first();
        this.whitehat = page.getByText("Whitehat", { exact: true }).first();
        this.cleartrip = page.getByText("Cleartrip", { exact: true }).first();
        this.myntraGlobal = page.getByText("Myntra Global", { exact: true }).first();
        this.contactUs = page.getByText("Contact Us", { exact: true }).first();
        this.faq = page.getByText("FAQ", { exact: true }).first();
        this.tC = page.getByText("T&C", { exact: true }).first();
        this.termsOfUse = page.getByText("Terms Of Use", { exact: true }).first();
        this.trackOrders = page.getByText("Track Orders", { exact: true }).first();
        this.shipping = page.getByText("Shipping", { exact: true }).first();
        this.cancellation = page.getByText("Cancellation", { exact: true }).first();
        this.privacyPolicy = page.getByText("Privacy policy", { exact: true }).first();
        this.grievanceRedressal = page.getByText("Grievance Redressal", { exact: true }).first();
        this.fssaiFoodSafetyConnectApp = page.getByText("FSSAI Food Safety Connect app", { exact: true }).first();
        this.makeup = page.getByText("Makeup", { exact: true }).first();
        this.dressesForGirls = page.getByText("Dresses For Girls", { exact: true }).first();
        this.tShirts = page.getByText("T-Shirts", { exact: true }).first();
        this.sandals = page.getByText("Sandals", { exact: true }).first();
        this.headphones = page.getByText("Headphones", { exact: true }).first();
        this.babydolls = page.getByText("Babydolls", { exact: true }).first();
        this.blazersForMen = page.getByText("Blazers For Men", { exact: true }).first();
        this.handbags = page.getByText("Handbags", { exact: true }).first();
        this.ladiesWatches = page.getByText("Ladies Watches", { exact: true }).first();
        this.bags = page.getByText("Bags", { exact: true }).first();
        this.sportShoes = page.getByText("Sport Shoes", { exact: true }).first();
        this.reebokShoes = page.getByText("Reebok Shoes", { exact: true }).first();
        this.pumaShoes = page.getByText("Puma Shoes", { exact: true }).first();
        this.boxers = page.getByText("Boxers", { exact: true }).first();
        this.wallets = page.getByText("Wallets", { exact: true }).first();
        this.tops = page.getByText("Tops", { exact: true }).first();
        this.earrings = page.getByText("Earrings", { exact: true }).first();
        this.fastrackWatches = page.getByText("Fastrack Watches", { exact: true }).first();
        this.kurtis = page.getByText("Kurtis", { exact: true }).first();
        this.nike = page.getByText("Nike", { exact: true }).first();
        this.smartWatches = page.getByText("Smart Watches", { exact: true }).first();
        this.titanWatches = page.getByText("Titan Watches", { exact: true }).first();
        this.designerBlouse = page.getByText("Designer Blouse", { exact: true }).first();
        this.gowns = page.getByText("Gowns", { exact: true }).first();
        this.rings = page.getByText("Rings", { exact: true }).first();
        this.cricketShoes = page.getByText("Cricket Shoes", { exact: true }).first();
        this.forever21 = page.getByText("Forever 21", { exact: true }).first();
        this.eyeMakeup = page.getByText("Eye Makeup", { exact: true }).first();
        this.photoFrames = page.getByText("Photo Frames", { exact: true }).first();
        this.punjabiSuits = page.getByText("Punjabi Suits", { exact: true }).first();
        this.bikini = page.getByText("Bikini", { exact: true }).first();
        this.myntraFashionShow = page.getByText("Myntra Fashion Show", { exact: true }).first();
        this.lipstick = page.getByText("Lipstick", { exact: true }).first();
        this.saree = page.getByText("Saree", { exact: true }).first();
        this.watches = page.getByText("Watches", { exact: true }).first();
        this.dresses = page.getByText("Dresses", { exact: true }).first();
        this.lehenga = page.getByText("Lehenga", { exact: true }).first();
        this.nikeShoes = page.getByText("Nike Shoes", { exact: true }).first();
        this.goggles = page.getByText("Goggles", { exact: true }).first();
        this.bras = page.getByText("Bras", { exact: true }).first();
        this.suit = page.getByText("Suit", { exact: true }).first();
        this.chinos = page.getByText("Chinos", { exact: true }).first();
        this.shoes = page.getByText("Shoes", { exact: true }).first();
        this.adidasShoes = page.getByText("Adidas Shoes", { exact: true }).first();
        this.woodlandShoes = page.getByText("Woodland Shoes", { exact: true }).first();
        this.jewellery = page.getByText("Jewellery", { exact: true }).first();
        this.designersSarees = page.getByText("Designers Sarees", { exact: true }).first();
        this.aFlipkartCompany = page.getByText("A Flipkart company", { exact: true }).first();
        this.item08040011450 = page.getByText("080‑40011450", { exact: true }).first();
        this.clothing = page.getByText("clothing", { exact: true }).first();
        this.onlineShoppingForWomen = page.getByText("Online shopping for women", { exact: true }).first();
        this.sarees = page.getByText("sarees", { exact: true }).first();
        this.photoFrames2 = page.getByText("photo frames", { exact: true }).first();
        this.myntraStudio = page.getByText("Myntra Studio", { exact: true }).first();
        this.android = page.getByText("Android", { exact: true }).first();
        this.ios = page.getByText("IOS", { exact: true }).first();
        this.gifts = page.getByText("gifts", { exact: true }).first();
        this.blackShirtsForMen = page.getByText("Black Shirts For Men", { exact: true }).first();
        this.arrow = page.getByText("Arrow", { exact: true }).first();
        this.raymond = page.getByText("Raymond", { exact: true }).first();
        this.highlander = page.getByText("HIGHLANDER", { exact: true }).first();
        this.roadster = page.getByText("Roadster", { exact: true }).first();
        this.rareRABBIT = page.getByText("RARE RABBIT", { exact: true }).first();
        this.biograph = page.getByText("BIOGRAPH", { exact: true }).first();
        this.nautica = page.getByText("Nautica", { exact: true }).first();
        this.hereNOW = page.getByText("HERE&NOW", { exact: true }).first();
        this.tushreeBOUTIQUE = page.getByText("TUSHREE BOUTIQUE", { exact: true }).first();
        this.arrowSport = page.getByText("Arrow Sport", { exact: true }).first();
        this.mischiefMONKEY = page.getByText("MISCHIEF MONKEY", { exact: true }).first();
        this.whiteHUSK = page.getByText("WHITE HUSK", { exact: true }).first();
        this.powerlook = page.getByText("Powerlook", { exact: true }).first();
        this.louisPhilippeJeans = page.getByText("Louis Philippe Jeans", { exact: true }).first();
        this.mydesignation = page.getByText("MyDesignation", { exact: true }).first();
        this.jackJones = page.getByText("Jack & Jones", { exact: true }).first();
        this.bsBLUESQUAD = page.getByText("BS BLUE SQUAD", { exact: true }).first();
        this.donVINO = page.getByText("DON VINO", { exact: true }).first();
        this.flyingMachine = page.getByText("Flying Machine", { exact: true }).first();
        this.cahoot = page.getByText("CAHOOT", { exact: true }).first();
        this.theBEARHOUSE = page.getByText("THE BEAR HOUSE", { exact: true }).first();
        this.gangsta = page.getByText("GANGSTA", { exact: true }).first();
        this.theIndianGarageCo = page.getByText("The Indian Garage Co", { exact: true }).first();
        this.mastHarbour = page.getByText("Mast & Harbour", { exact: true }).first();
        this.rCodeByTheRoadsterLifeCo = page.getByText("R.Code by The Roadster Life Co.", { exact: true }).first();
        this.theHouseOfPolo = page.getByText("The House of Polo", { exact: true }).first();
        this.addOns = page.getByText("Add-Ons", { exact: true }).first();
        this.bundles = page.getByText("Bundles", { exact: true }).first();
        this.collar = page.getByText("Collar", { exact: true }).first();
        this.countryOfOrigin = page.getByText("Country of Origin", { exact: true }).first();
        this.craft = page.getByText("Craft", { exact: true }).first();
        this.fabrics = page.getByText("Fabrics", { exact: true }).first();
        this.fashionTrends = page.getByText("Fashion Trends", { exact: true }).first();
        this.slimFitOpaqueFormalShirt = page.getByText("Slim Fit Opaque Formal Shirt", { exact: true }).first();
        this.pureCottonFormalShirt = page.getByText("Pure Cotton Formal Shirt", { exact: true }).first();
        this.slimFitOpaqueCasualShirt = page.getByText("Slim Fit Opaque Casual Shirt", { exact: true }).first();
        this.pureCottonCasualShirts = page.getByText("Pure Cotton Casual Shirts", { exact: true }).first();
        this.menVynillShirt = page.getByText("Men Vynill Shirt", { exact: true }).first();
        this.pureCottonCasualShirt = page.getByText("Pure Cotton Casual Shirt", { exact: true }).first();
        this.menSEmbroideredResortShirt = page.getByText("Men's Embroidered Resort Shirt", { exact: true }).first();
        this.solidSlimFitShirt = page.getByText("Solid Slim Fit Shirt", { exact: true }).first();
        this.regularFitCheckedShirt = page.getByText("Regular Fit Checked Shirt", { exact: true }).first();
        this.menRegularFitCasualShirt = page.getByText("Men Regular Fit Casual Shirt", { exact: true }).first();
        this.slimPureCottonFormalShirt = page.getByText("Slim Pure Cotton Formal Shirt", { exact: true }).first();
        this.slimFitCasualShirt = page.getByText("Slim Fit Casual Shirt", { exact: true }).first();
        this.menBlackWhiteCheckShirt = page.getByText("Men Black White Check Shirt", { exact: true }).first();
        this.regularCheckedCasualShirt = page.getByText("Regular Checked Casual Shirt", { exact: true }).first();
        this.menOpaqueCasualShirt = page.getByText("Men Opaque Casual Shirt", { exact: true }).first();
        this.formalPureCottonShirt = page.getByText("Formal Pure Cotton Shirt", { exact: true }).first();
        this.cottonCasualShirt = page.getByText("Cotton Casual Shirt", { exact: true }).first();
        this.gear5BoxyFitShirt = page.getByText("Gear 5 Boxy Fit Shirt", { exact: true }).first();
        this.doublePocketCottonLongSleevesShirt = page.getByText("Double Pocket Cotton Long Sleeves Shirt", { exact: true }).first();
        this.relaxedFitCottonShirt = page.getByText("Relaxed Fit Cotton Shirt", { exact: true }).first();
        this.casualShirt = page.getByText("Casual Shirt", { exact: true }).first();
        this.cottonLinenCasualShirt = page.getByText("Cotton Linen Casual Shirt", { exact: true }).first();
        this.opaqueCasualShirt = page.getByText("Opaque Casual Shirt", { exact: true }).first();
        this.solidCasualCottonShirt = page.getByText("Solid CasualCotton Shirt", { exact: true }).first();
        this.menCottonCasualShirt = page.getByText("Men Cotton Casual Shirt", { exact: true }).first();
        this.menCheckedCottonShirt = page.getByText("Men Checked Cotton Shirt", { exact: true }).first();
        this.classicPrintedCasualShirt = page.getByText("Classic Printed Casual Shirt", { exact: true }).first();
        this.slimFitCheckedFlannelShirt = page.getByText("Slim Fit Checked Flannel Shirt", { exact: true }).first();
        this.menSSmartCasualShirts = page.getByText("Men's Smart Casual Shirts", { exact: true }).first();
        this.menSCrinkleTexturedShirt = page.getByText("Men's Crinkle Textured Shirt", { exact: true }).first();
        this.menPackOf2Shirts = page.getByText("Men Pack Of 2 Shirts", { exact: true }).first();
        this.classicCheckedShirt = page.getByText("Classic Checked Shirt", { exact: true }).first();
        this.menOversizedCottonShirt = page.getByText("Men Oversized Cotton Shirt", { exact: true }).first();
        this.regularFitSolidCasualCottonLinenShirt = page.getByText("Regular Fit Solid Casual Cotton Linen Shirt", { exact: true }).first();
        this.structuredStripeGeometricShirt = page.getByText("Structured Stripe Geometric Shirt", { exact: true }).first();
        this.menStripedCottonShirt = page.getByText("Men Striped Cotton Shirt", { exact: true }).first();
        this.cottonCasualShirts = page.getByText("Cotton Casual Shirts", { exact: true }).first();
        this.arrowOriginalSlimFitOpaqueFormalShirt = page.getByAltText("Arrow Original Slim Fit Opaque Formal Shirt", { exact: true });
        this.raymondPureCottonOpaqueFormalShirt = page.getByAltText("Raymond Pure Cotton Opaque Formal Shirt", { exact: true });
        this.highlanderMenSlimFitShirt = page.getByAltText("HIGHLANDER Men Slim Fit Shirt", { exact: true });
        this.roadsterTheLifestyleCoPureTwillCottonCasualShirt = page.getByAltText("Roadster The Lifestyle co pure twill cotton casual shirt", { exact: true });
        this.rareRABBITMenFloralPrintedCasualRegularFitShirt = page.getByAltText("RARE RABBIT Men Floral Printed Casual Regular Fit Shirt", { exact: true });
        this.roadsterMenBlackPureCottonCasualShirt = page.getByAltText("Roadster Men Black Pure Cotton Casual Shirt", { exact: true });
        this.biographMenPrintedCasualShirt = page.getByAltText("BIOGRAPH Men Printed Casual Shirt", { exact: true });
        this.nauticaSolidSlimFitShirt = page.getByAltText("Nautica Solid Slim Fit Shirt", { exact: true });
        this.roadsterMenBlackBlueRegularFitCheckedCasualShirt = page.getByAltText("Roadster Men Black & Blue Regular Fit Checked Casual Shirt", { exact: true });
        this.theRoadsterLifestyleCoMenBlackRegularFitPrintedCasualShirt = page.getByAltText("The Roadster Lifestyle Co Men Black Regular Fit Printed  Casual Shirt", { exact: true });
        this.arrowManhattanSlimFitSolidPureCottonFormalShirt = page.getByAltText("Arrow Manhattan Slim Fit Solid Pure Cotton Formal Shirt", { exact: true });
        this.clothing2 = page.getByText("Clothing", { exact: true }).first();
        this.shirts = page.getByText("Shirts", { exact: true }).first();
        this.arrowSlimFitOpaqueFormalShirtRs1280Rs209939OFF = page.getByText("Arrow Slim Fit Opaque Formal Shirt Rs. 1280Rs. 2099(39% OFF)", { exact: true }).first();
        this.raymondPureCottonFormalShirtRs1112Rs209947OFF = page.getByText("Raymond Pure Cotton Formal Shirt Rs. 1112Rs. 2099(47% OFF)", { exact: true }).first();
        this.highlanderSlimFitOpaqueCasualShirtRs463Rs159971OFF = page.getByText("HIGHLANDER Slim Fit Opaque Casual Shirt Rs. 463Rs. 1599(71% OFF)", { exact: true }).first();
        this.roadsterPureCottonCasualShirtsRs492Rs199975OFF = page.getByText("Roadster Pure Cotton Casual Shirts Rs. 492Rs. 1999(75% OFF)", { exact: true }).first();
        this.rareRABBITMenVynillShirtRs1719Rs399957OFF = page.getByText("RARE RABBIT Men Vynill Shirt Rs. 1719Rs. 3999(57% OFF)", { exact: true }).first();
        this.roadsterPureCottonCasualShirtRs489Rs139965OFF = page.getByText("Roadster Pure Cotton Casual Shirt Rs. 489Rs. 1399(65% OFF)", { exact: true }).first();
        this.biographMenSEmbroideredResortShirtRs615Rs269977OFF = page.getByText("BIOGRAPH Men's Embroidered Resort Shirt Rs. 615Rs. 2699(77% OFF)", { exact: true }).first();
        this.nauticaSolidSlimFitShirtRs1217Rs209942OFF = page.getByText("Nautica Solid Slim Fit Shirt Rs. 1217Rs. 2099(42% OFF)", { exact: true }).first();
        this.roadsterRegularFitCheckedShirtRs588Rs1499Rs911OFF = page.getByText("Roadster Regular Fit Checked Shirt Rs. 588Rs. 1499(Rs. 911 OFF)", { exact: true }).first();
        this.roadsterMenRegularFitCasualShirtRs509Rs149966OFF = page.getByText("Roadster Men Regular Fit Casual Shirt Rs. 509Rs. 1499(66% OFF)", { exact: true }).first();
        this.arrowSlimPureCottonFormalShirtRs1159Rs199942OFF = page.getByText("Arrow Slim Pure Cotton Formal Shirt Rs. 1159Rs. 1999(42% OFF)", { exact: true }).first();
        this.hereNOWSlimFitCasualShirtRs491Rs159969OFF = page.getByText("HERE&NOW Slim Fit Casual Shirt Rs. 491Rs. 1599(69% OFF)", { exact: true }).first();
        this.newTUSHREEBOUTIQUEMenBlackWhiteCheckShirtRs853Rs199957OFF = page.getByText("NEW TUSHREE BOUTIQUE Men Black White Check Shirt Rs. 853Rs. 1999(57% OFF)", { exact: true }).first();
        this.arrowSportSlimFitCasualShirtRs1172Rs229949OFF = page.getByText("Arrow Sport Slim Fit Casual Shirt Rs. 1172Rs. 2299(49% OFF)", { exact: true }).first();
        this.roadsterRegularCheckedCasualShirtRs779Rs119935OFF = page.getByText("Roadster Regular Checked Casual Shirt Rs. 779Rs. 1199(35% OFF)", { exact: true }).first();
        this.mischiefMONKEYMenOpaqueCasualShirtRs709Rs208866OFF = page.getByText("MISCHIEF MONKEY Men Opaque Casual Shirt Rs. 709Rs. 2088(66% OFF)", { exact: true }).first();
        this.arrowFormalPureCottonShirtRs1231Rs219944OFF = page.getByText("Arrow Formal Pure Cotton Shirt Rs. 1231Rs. 2199(44% OFF)", { exact: true }).first();
        this.roadsterCottonCasualShirtRs593Rs109946OFF = page.getByText("Roadster Cotton Casual Shirt Rs. 593Rs. 1099(46% OFF)", { exact: true }).first();
        this.newWHITEHUSKGear5BoxyFitShirtRs1176Rs287959OFF = page.getByText("NEW WHITE HUSK Gear 5 Boxy Fit Shirt Rs. 1176Rs. 2879(59% OFF)", { exact: true }).first();
        this.powerlookDoublePocketCottonLongSleevesShirtRs1203Rs279957OFF = page.getByText("Powerlook Double Pocket Cotton Long Sleeves Shirt Rs. 1203Rs. 2799(57% OFF)", { exact: true }).first();
        this.louisPhilippeJeansSlimFitCasualShirtRs1179Rs199941OFF = page.getByText("Louis Philippe Jeans Slim Fit Casual Shirt Rs. 1179Rs. 1999(41% OFF)", { exact: true }).first();
        this.mydesignationRelaxedFitCottonShirtRs399Rs159975OFF = page.getByText("MyDesignation Relaxed Fit Cotton Shirt Rs. 399Rs. 1599(75% OFF)", { exact: true }).first();
        this.jackJonesCasualShirtRs1149Rs249954OFF = page.getByText("Jack & Jones Casual Shirt Rs. 1149Rs. 2499(54% OFF)", { exact: true }).first();
        this.bsBLUESQUADCottonLinenCasualShirtRs537Rs199973OFF = page.getByText("BS BLUE SQUAD Cotton Linen Casual Shirt Rs. 537Rs. 1999(73% OFF)", { exact: true }).first();
        this.donVINOOpaqueCasualShirtRs890Rs199955OFF = page.getByText("DON VINO Opaque Casual Shirt Rs. 890Rs. 1999(55% OFF)", { exact: true }).first();
        this.roadsterSolidCasualCottonShirtRs643Rs139954OFF = page.getByText("Roadster Solid CasualCotton Shirt Rs. 643Rs. 1399(54% OFF)", { exact: true }).first();
        this.roadsterMenCottonCasualShirtRs588Rs1499Rs911OFF = page.getByText("Roadster Men Cotton Casual Shirt Rs. 588Rs. 1499(Rs. 911 OFF)", { exact: true }).first();
        this.flyingMachineMenCheckedCottonShirtRs1172Rs229949OFF = page.getByText("Flying Machine Men Checked Cotton Shirt Rs. 1172Rs. 2299(49% OFF)", { exact: true }).first();
        this.cahootClassicPrintedCasualShirtRs797Rs189958OFF = page.getByText("CAHOOT Classic Printed Casual Shirt Rs. 797Rs. 1899(58% OFF)", { exact: true }).first();
        this.flyingMachineCasualShirtRs1000Rs249960OFF = page.getByText("Flying Machine Casual Shirt Rs. 1000Rs. 2499(60% OFF)", { exact: true }).first();
        this.roadsterPureCottonCasualShirtRs476Rs139966OFF = page.getByText("Roadster Pure Cotton Casual Shirt Rs. 476Rs. 1399(66% OFF)", { exact: true }).first();
        this.theBEARHOUSESlimFitCheckedFlannelShirtRs873Rs249565OFF = page.getByText("THE BEAR HOUSE Slim Fit Checked Flannel Shirt Rs. 873Rs. 2495(65% OFF)", { exact: true }).first();
        this.newGANGSTAMenSSmartCasualShirtsRs1299 = page.getByText("NEW GANGSTA Men's Smart Casual Shirts Rs. 1299", { exact: true }).first();
        this.theIndianGarageCoMenCheckedCottonShirtRs495Rs174972OFF = page.getByText("The Indian Garage Co Men Checked Cotton Shirt Rs. 495Rs. 1749(72% OFF)", { exact: true }).first();
        this.biographMenSCrinkleTexturedShirtRs615Rs269977OFF = page.getByText("BIOGRAPH Men's Crinkle Textured Shirt Rs. 615Rs. 2699(77% OFF)", { exact: true }).first();
        this.powerlookCasualShirtRs1349Rs299955OFF = page.getByText("Powerlook Casual Shirt Rs. 1349Rs. 2999(55% OFF)", { exact: true }).first();
        this.roadsterMenPackOf2ShirtsRs818Rs2999Rs2181OFF = page.getByText("Roadster Men Pack Of 2 Shirts Rs. 818Rs. 2999(Rs. 2181 OFF)", { exact: true }).first();
        this.cahootClassicCheckedShirtRs797Rs189958OFF = page.getByText("CAHOOT Classic Checked Shirt Rs. 797Rs. 1899(58% OFF)", { exact: true }).first();
        this.cahootMenOversizedCottonShirtRs1139Rs199943OFF = page.getByText("CAHOOT Men Oversized Cotton Shirt Rs. 1139Rs. 1999(43% OFF)", { exact: true }).first();
        this.mastHarbourRegularFitSolidCasualCottonLinenShirtRs825Rs249967OFF = page.getByText("Mast & Harbour Regular Fit Solid Casual Cotton Linen Shirt Rs. 825Rs. 2499(67% OFF)", { exact: true }).first();
        this.newRCodeByTheRoadsterLifeCoCasualShirtRs719Rs117939OFF = page.getByText("NEW R.Code by The Roadster Life Co. Casual Shirt Rs. 719Rs. 1179(39% OFF)", { exact: true }).first();
        this.powerlookStructuredStripeGeometricShirtRs1065Rs259959OFF = page.getByText("Powerlook Structured Stripe Geometric Shirt Rs. 1065Rs. 2599(59% OFF)", { exact: true }).first();
        this.hereNOWMenStripedCottonShirtRs630Rs199968OFF = page.getByText("HERE&NOW Men Striped Cotton Shirt Rs. 630Rs. 1999(68% OFF)", { exact: true }).first();
        this.roadsterRegularFitCheckedShirtRs629Rs149958OFF = page.getByText("Roadster Regular Fit Checked Shirt Rs. 629Rs. 1499(58% OFF)", { exact: true }).first();
        this.powerlookCasualShirtRs1410Rs299953OFF = page.getByText("Powerlook Casual Shirt Rs. 1410Rs. 2999(53% OFF)", { exact: true }).first();
        this.roadsterCottonCasualShirtsRs499Rs199975OFF = page.getByText("Roadster Cotton Casual Shirts Rs. 499Rs. 1999(75% OFF)", { exact: true }).first();
        this.theHouseOfPoloPureCottonCasualShirtRs1109Rs299963OFF = page.getByText("The House of Polo Pure Cotton Casual Shirt Rs. 1109Rs. 2999(63% OFF)", { exact: true }).first();
        this.arrowPureCottonFormalShirtRs1209Rs219945OFF = page.getByText("Arrow Pure Cotton Formal Shirt Rs. 1209Rs. 2199(45% OFF)", { exact: true }).first();
        this.adidas = page.getByText("Adidas", { exact: true }).first();
        this.fila = page.getByText("Fila", { exact: true }).first();
        this.onlineShopping = page.getByText("Online Shopping", { exact: true }).first();
        this.pepeJeans = page.getByText("Pepe Jeans", { exact: true }).first();
        this.puma = page.getByText("Puma", { exact: true }).first();
        this.unitedColorsOfBenetton = page.getByText("United Colors of Benetton", { exact: true }).first();
        this.fastrack = page.getByText("Fastrack", { exact: true }).first();
        this.shorts = page.getByText("Shorts", { exact: true }).first();
        this.beingHuman = page.getByText("Being Human", { exact: true }).first();
        this.skirts = page.getByText("Skirts", { exact: true }).first();
        this.woodland = page.getByText("Woodland", { exact: true }).first();
        this.supra = page.getByText("Supra", { exact: true }).first();
        this.tShirts2 = page.getByText("T-shirts", { exact: true }).first();
        this.caps = page.getByText("Caps", { exact: true }).first();
        this.backpacks = page.getByText("Backpacks", { exact: true }).first();
        this.flipFlops = page.getByText("Flip Flops", { exact: true }).first();
        this.sunglasses = page.getByText("Sunglasses", { exact: true }).first();
        this.kurtas = page.getByText("Kurtas", { exact: true }).first();
        this.lingerie = page.getByText("Lingerie", { exact: true }).first();
        this.jackets = page.getByText("Jackets", { exact: true }).first();
        this.skechers = page.getByText("Skechers", { exact: true }).first();
        this.pumaTshirts = page.getByText("Puma Tshirts", { exact: true }).first();
        this.wranglerShirts = page.getByText("Wrangler Shirts", { exact: true }).first();
        this.adidasTshirts = page.getByText("Adidas Tshirts", { exact: true }).first();
        this.roadsterShirts = page.getByText("Roadster Shirts", { exact: true }).first();
        this.casualShoes = page.getByText("Casual Shoes", { exact: true }).first();
        this.runningShoes = page.getByText("Running Shoes", { exact: true }).first();
        this.nikeSportsShoes = page.getByText("Nike Sports Shoes", { exact: true }).first();
        this.jeans = page.getByText("Jeans", { exact: true }).first();
        this.beingHumanTshirts = page.getByText("Being Human Tshirts", { exact: true }).first();
        this.converseShoes = page.getByText("Converse Shoes", { exact: true }).first();
        this.rootrailthumbleftButton = page.locator("#rootRailThumbLeft");
        this.rootrailthumbrightButton = page.locator("#rootRailThumbRight");

    }


    async waitForPageReady(
        timeout = this.navigationTimeout
    ) {

        await this.page.waitForLoadState(
            'domcontentloaded',
            {
                timeout
            }
        );

        try {

            await this.page.waitForLoadState(
                'load',
                {
                    timeout
                }
            );

        } catch (error) {

            // Some applications continuously load
            // analytics or background resources.
        }
    }


    async navigate(
        url,
        timeout = this.navigationTimeout
    ) {

        await this.page.goto(
            url,
            {
                waitUntil: 'domcontentloaded',
                timeout
            }
        );

        await this.waitForPageReady(
            timeout
        );
    }


    async waitForElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        const target =
            locator.first();

        await target.waitFor({
            state: 'visible',
            timeout
        });

        return target;
    }


    async waitForElementAttached(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        const target =
            locator.first();

        await target.waitFor({
            state: 'attached',
            timeout
        });

        return target;
    }


    async waitForElementHidden(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        await locator
            .first()
            .waitFor({
                state: 'hidden',
                timeout
            });

        return true;
    }


    async waitForUrl(
        urlPattern,
        timeout = this.navigationTimeout
    ) {

        await this.page.waitForURL(
            urlPattern,
            {
                timeout
            }
        );

        await this.waitForPageReady(
            timeout
        );

        return true;
    }


    async clickElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.click({
            timeout
        });
    }


    async fillField(
        locatorName,
        value,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.fill(
            String(value),
            {
                timeout
            }
        );
    }


    async typeText(
        locatorName,
        value,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.fill(
            String(value),
            {
                timeout
            }
        );
    }


    async selectOption(
        locatorName,
        value,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        return await target.selectOption(
            value,
            {
                timeout
            }
        );
    }


    async checkElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.check({
            timeout
        });
    }


    async uncheckElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.uncheck({
            timeout
        });
    }


    async isChecked(
        locatorName,
        timeout = this.assertionTimeout
    ) {

        try {

            const target =
                await this.waitForElement(
                    locatorName,
                    timeout
                );

            const startTime =
                Date.now();

            while (
                Date.now() - startTime
                < timeout
            ) {

                if (
                    await target.isChecked()
                ) {
                    return true;
                }

                await this.page.waitForTimeout(
                    250
                );
            }

            return false;

        } catch (error) {

            return false;
        }
    }


    async getText(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        const text =
            await target.textContent();

        return String(
            text || ''
        ).trim();
    }


    async isVisible(
        locatorName,
        timeout = this.assertionTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        try {

            await locator
                .first()
                .waitFor({
                    state: 'visible',
                    timeout
                });

            return true;

        } catch (error) {

            return false;
        }
    }


    async hasText(
        locatorName,
        expectedText,
        timeout = this.assertionTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        const target =
            locator.first();

        try {

            await target.waitFor({
                state: 'visible',
                timeout
            });

            const expected =
                String(expectedText);

            const startTime =
                Date.now();

            while (
                Date.now() - startTime
                < timeout
            ) {

                const actualText =
                    String(
                        await target.textContent()
                        || ''
                    );

                if (
                    actualText.includes(
                        expected
                    )
                ) {
                    return true;
                }

                await this.page.waitForTimeout(
                    300
                );
            }

            return false;

        } catch (error) {

            return false;
        }
    }


    async hasExactText(
        locatorName,
        expectedText,
        timeout = this.assertionTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        const target =
            locator.first();

        try {

            await target.waitFor({
                state: 'visible',
                timeout
            });

            const expected =
                String(expectedText).trim();

            const startTime =
                Date.now();

            while (
                Date.now() - startTime
                < timeout
            ) {

                const actualText =
                    String(
                        await target.textContent()
                        || ''
                    ).trim();

                if (
                    actualText === expected
                ) {
                    return true;
                }

                await this.page.waitForTimeout(
                    300
                );
            }

            return false;

        } catch (error) {

            return false;
        }
    }


    async waitForText(
        locatorName,
        expectedText,
        timeout = this.assertionTimeout
    ) {

        const hasExpectedText =
            await this.hasText(
                locatorName,
                expectedText,
                timeout
            );

        if (!hasExpectedText) {

            throw new Error(
                `Expected text "${expectedText}" `
                + `was not found in locator: `
                + `${locatorName}`
            );
        }

        return true;
    }


    async scrollToElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElementAttached(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();
    }


    async scrollToTop() {

        await this.page.evaluate(
            () => {
                window.scrollTo(
                    0,
                    0
                );
            }
        );
    }


    async scrollToBottom() {

        await this.page.evaluate(
            () => {
                window.scrollTo(
                    0,
                    document.body.scrollHeight
                );
            }
        );
    }


    async scrollByPixels(
        pixels
    ) {

        await this.page.evaluate(
            (value) => {
                window.scrollBy(
                    0,
                    value
                );
            },
            pixels
        );
    }


    async hoverElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.hover({
            timeout
        });
    }


    async pressKey(
        locatorName,
        key,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.press(
            key,
            {
                timeout
            }
        );
    }
    async clickAndSwitchToNewTab(
    locatorName,
    timeout = this.navigationTimeout
) {
    const target =
        await this.waitForElement(
            locatorName,
            timeout
        );

    const [
        newPage
    ] = await Promise.all([
        this.page.context().waitForEvent(
            'page',
            {
                timeout
            }
        ),

        target.click({
            timeout
        })
    ]);

    await newPage.waitForLoadState(
        'domcontentloaded',
        {
            timeout
        }
    );

    this.parentPage =
        this.page;

    this.page =
        newPage;

    return newPage;
}


async switchToTabByUrl(
    expectedUrl,
    timeout = this.navigationTimeout
) {
    const expected =
        String(expectedUrl);

    const startTime =
        Date.now();

    while (
        Date.now() - startTime
        < timeout
    ) {
        const pages =
            this.page.context().pages();

        for (
            const openPage
            of pages
        ) {
            if (
                openPage.url().includes(
                    expected
                )
            ) {
                this.page =
                    openPage;

                await this.page.bringToFront();

                return true;
            }
        }

        await this.page.waitForTimeout(
            250
        );
    }

    return false;
}


async switchToTabByTitle(
    expectedTitle,
    timeout = this.navigationTimeout
) {
    const expected =
        String(expectedTitle);

    const startTime =
        Date.now();

    while (
        Date.now() - startTime
        < timeout
    ) {
        const pages =
            this.page.context().pages();

        for (
            const openPage
            of pages
        ) {
            const title =
                await openPage.title();

            if (
                title.includes(
                    expected
                )
            ) {
                this.page =
                    openPage;

                await this.page.bringToFront();

                return true;
            }
        }

        await this.page.waitForTimeout(
            250
        );
    }

    return false;
}


async switchToParentTab() {
    if (
        !this.parentPage
        || this.parentPage.isClosed()
    ) {
        throw new Error(
            'Parent browser tab is not available.'
        );
    }

    this.page =
        this.parentPage;

    await this.page.bringToFront();

    return true;
}


async closeCurrentTab() {
    if (
        this.page.isClosed()
    ) {
        return true;
    }

    await this.page.close();

    if (
        this.parentPage
        && !this.parentPage.isClosed()
    ) {
        this.page =
            this.parentPage;

        await this.page.bringToFront();
    }

    return true;
}


async getOpenTabCount() {
    return this.page
        .context()
        .pages()
        .filter(
            openPage =>
                !openPage.isClosed()
        )
        .length;
}


    async getCurrentUrl() {

        return this.page.url();
    }


    async urlContains(
        expectedValue,
        timeout = this.assertionTimeout
    ) {

        const expected =
            String(expectedValue);

        const startTime =
            Date.now();

        while (
            Date.now() - startTime
            < timeout
        ) {

            const currentUrl =
                this.page.url();

            if (
                currentUrl.includes(
                    expected
                )
            ) {
                return true;
            }

            await this.page.waitForTimeout(
                300
            );
        }

        return false;
    }


}

module.exports = PageObject;
