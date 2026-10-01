export interface Translations {
    common: {
        loading: string;
    };
    nav: {
        home: string;
        category: string;
        categories: string;
        noCategories: string;
        loadError: string;
        contact: string;
        searchPlaceholder: string;
        search: string;
        toggleNav: string;
        login: string;
        cart: string;
        logout: string;
        language: string;
    };
    footer: {
        address: string;
        contact: string;
        whatsapp: string;
    };
    home: {
        title: string;
        heroTitle: string;
        heroSubtitle: string;
        heroCta: string;
        categoriesTitle: string;
        loadingCategories: string;
        noCategories: string;
        newProductsTitle: string;
        loadingProducts: string;
        pageNotFound: string;
        loadProductsError: string;
        featureFastDeliveryTitle: string;
        featureFastDeliveryText: string;
        featureSecurePurchaseTitle: string;
        featureSecurePurchaseText: string;
        featureSupportTitle: string;
        featureSupportText: string;
    };
    product: {
        noImage: string;
        viewDetails: string;
        addToCart: (name: string) => string;
        empty: string;
        allProductsTitle: string;
        notFound: string;
        searchingFor: (term: string) => string;
        sortLabel: string;
        sortRecent: string;
        sortNameAsc: string;
        sortNameDesc: string;
        sortPriceAsc: string;
        sortPriceDesc: string;
        loadError: string;
        breadcrumbLabel: string;
        descriptionTitle: string;
        noProductImage: string;
        addToCartLabel: string;
        addToWishlist: string;
        slideLabel: (position: number) => string;
        imageAlt: (name: string, position: number) => string;
    };
    pagination: {
        navigation: string;
        first: string;
        previous: string;
        next: string;
        last: string;
    };
    contact: {
        title: string;
        heading: string;
        success: string;
        genericError: string;
        rateLimitError: string;
        nameLabel: string;
        nameError: string;
        emailLabel: string;
        emailError: string;
        phoneLabel: string;
        phonePlaceholder: string;
        phoneError: string;
        messageLabel: string;
        messageError: string;
        send: string;
        sending: string;
        otherContacts: string;
    };
    notFound: {
        title: string;
        heading: string;
        description: string;
        backHome: string;
    };
    auth: {
        emailLabel: string;
        passwordLabel: string;
        nameLabel: string;
        dateBirthLabel: string;
        phoneLabel: string;
        phonePlaceholder: string;
        password1Label: string;
        password2Label: string;
        newPasswordLabel: string;
        confirmNewPasswordLabel: string;
        login: {
            title: string;
            heading: string;
            submit: string;
            submitting: string;
            createAccount: string;
            forgotPassword: string;
            resendConfirmation: string;
            resending: string;
            confirmationResent: string;
        };
        signup: {
            title: string;
            heading: string;
            submit: string;
            submitting: string;
            haveAccount: string;
            successTitle: string;
            successText: (email: string) => string;
            goToLogin: string;
        };
        passwordReset: {
            title: string;
            heading: string;
            intro: string;
            submit: string;
            submitting: string;
            backToLogin: string;
            doneTitle: string;
            doneText: string;
        };
        passwordResetConfirm: {
            title: string;
            heading: string;
            submit: string;
            submitting: string;
            checking: string;
            invalidTitle: string;
            invalidText: string;
            requestNew: string;
            completeTitle: string;
            completeText: string;
            goToLogin: string;
        };
        emailVerification: {
            title: string;
            checking: string;
            successTitle: string;
            successText: string;
            invalidTitle: string;
            invalidText: string;
            login: string;
            backToLogin: string;
        };
        loggedOut: {
            title: string;
            heading: string;
            text: string;
            loginAgain: string;
        };
        errors: {
            invalidLogin: string;
            inactive: string;
            emailNotVerified: string;
            generic: string;
            network: string;
            tooManyRequests: string;
        };
    };
    userMenu: {
        hello: (name: string) => string;
        profile: string;
        editProfile: string;
        changePassword: string;
        orders: string;
        addresses: string;
        wishlist: string;
        admin: string;
    };
}
