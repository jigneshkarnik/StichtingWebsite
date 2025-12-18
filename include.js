/**
 * Loads and injects common HTML components (header and footer) into the current page.
 * @param {string} pageTitle - The title specific to the page being loaded.
 * @param {string} activePage - The filename of the current page to set the active navigation link.
 */
function loadComponents(pageTitle, activePage) {
    const headerPath = 'header.html';
    const footerPath = 'footer.html';

    // Set the page title
    document.title = pageTitle;

    // 1. Load Header Content and Inject
    fetch(headerPath)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.text();
        })
        .then(headerContent => {
            const headerPlaceholder = document.getElementById('header-placeholder');
            if (headerPlaceholder) {
                // Use outerHTML to replace the placeholder div with the actual header content
                headerPlaceholder.outerHTML = headerContent; 
                
                // Build and insert navigation links (needed after header is injected)
                const navLinksContainer = document.getElementById('main-nav-links');
                if (navLinksContainer) {
                    // Ordered links per requested sequence (Donations removed from nav)
                    const links = [
                        { text: 'Home', href: 'index.html' },
                        { text: 'Event Archives', href: 'events.html' },
                        { text: 'Upcoming Events', href: 'upcoming-events.html' },
                        { text: 'News', href: 'news.html' },
                        { text: 'Sponsors', href: 'sponsors.html' },
                        { text: 'The Tulips Lounge', href: 'tulip-lounge.html' },
                        { text: 'Bhartiya First Conclave', href: 'bhartiyafirst.html' },
                        { text: 'About Us', href: 'about.html' },
                        { text: 'Contact Us', href: 'contact.html' }
                    ];

                    // Build list items for the nav
                    links.forEach(link => {
                        const li = document.createElement('li');
                        const a = document.createElement('a');
                        a.href = link.href;
                        a.textContent = link.text;
                        // active state
                        if (link.href === activePage || (link.href === 'bhartiyafirst.html' && activePage === 'bhartiyafirst.html')) {
                            a.classList.add('active');
                        }
                        li.appendChild(a);
                        navLinksContainer.appendChild(li);
                    });

                    // Add a 'more' dropdown container for overflow items (inserted before donate so donate stays visible)
                    const moreLi = document.createElement('li');
                    moreLi.className = 'more';
                    moreLi.innerHTML = '<button class="more-toggle" aria-expanded="false"><i class="fa fa-ellipsis-h"></i> <span class="more-count" aria-hidden="true"></span></button><ul class="more-list" aria-hidden="true"></ul>';
                    navLinksContainer.appendChild(moreLi);

                    // Add Donate Button as a nav item (always visible, will not be moved into More)
                    const donateLi = document.createElement('li');
                    donateLi.className = 'donate-li';
                    donateLi.innerHTML = '<a href="donations.html" class="btn-donate" aria-label="Donate">Donate</a>';
                    navLinksContainer.appendChild(donateLi);

                    // Function to redistribute items into the more-list when space is limited
                    function redistributeMenu() {
                        // Skip redistribution on mobile (max-width 900px) since menu is dropdown
                        if (window.innerWidth <= 900) return;
                        const nav = navLinksContainer;
                        const more = nav.querySelector('.more');
                        const moreList = more.querySelector('.more-list');
                        // donate is a nav item (.donate-li)
                        const donate = nav.querySelector('.donate-li') || document.querySelector('.donate-li');
                        const navbar = document.querySelector('.navbar');
                        const logo = document.querySelector('.logo');
                        if (!nav || !more || !navbar) return;

                        // Move all items out of more-list back into nav before measuring
                        while (moreList.firstChild) {
                            nav.insertBefore(moreList.firstChild, more);
                        }

                        // Measure available space (navbar width minus logo and donate widths)
                        const navbarWidth = navbar.clientWidth;
                        const logoWidth = logo ? logo.offsetWidth : 0;
                        const donateWidth = donate ? donate.offsetWidth : 0;
                        const buffer = 86; // breathing room to avoid edge-case wrapping

                        // Ensure the centered nav reserves visible space for the donate button by
                        // limiting the nav's max-width on wide screens. This prevents the centered
                        // `.nav-links` from extending beneath the donate item and getting clipped.
                        try {
                            if (window.innerWidth >= 992 && donateWidth > 0) {
                                // leave some extra breathing room (40px) beyond donate width
                                const reserve = donateWidth + 40;
                                // nav max width should be navbarWidth minus reserve (and account for logo)
                                nav.style.maxWidth = (navbarWidth - reserve - logoWidth) + 'px';
                            } else {
                                nav.style.maxWidth = '';
                            }
                        } catch (e) {}

                        const available = navbarWidth - (logoWidth + donateWidth + buffer);

                        // Compute gap between items (CSS gap)
                        let gap = 18; // default
                        try {
                            const cs = window.getComputedStyle(nav);
                            const g = cs.getPropertyValue('gap') || cs.getPropertyValue('column-gap');
                            if (g) gap = parseFloat(g);
                        } catch (e) {}

                        // Collect candidate items (exclude .more and .donate-li)
                        let items = Array.from(nav.children).filter(ch => !ch.classList.contains('more') && !ch.classList.contains('donate-li'));

                        // Calculate used width (sum of item widths + gaps)
                        let used = items.reduce((sum, el) => sum + el.offsetWidth, 0);
                        if (items.length > 1) used += gap * (items.length - 1);

                        // If used space exceeds available, move items from right to left into moreList
                        while (used > available && items.length > 0) {
                            const last = items.pop();
                            used -= last.offsetWidth;
                            if (items.length >= 1) used -= gap; // removed one gap
                            moreList.insertBefore(last, moreList.firstChild);
                        }

                        // If still not fitting (edge cases), ensure at least one visible item remains in nav (home)
                        items = Array.from(nav.children).filter(ch => !ch.classList.contains('more') && !ch.classList.contains('donate-li'));
                        if (items.length === 0 && moreList.children.length > 0) {
                            // move the last item back out so nav isn't empty
                            const firstFromMore = moreList.removeChild(moreList.firstChild);
                            nav.insertBefore(firstFromMore, more);
                        }

                        // Update the more button count and visibility
                        const moreToggle = more.querySelector('.more-toggle');
                        const moreCount = moreToggle ? moreToggle.querySelector('.more-count') : null;
                        const count = moreList.children.length;
                        if (moreCount) moreCount.textContent = count > 0 ? `(${count})` : '';
                        if (count === 0) {
                            more.style.display = 'none';
                            if (moreList.classList.contains('open')) {
                                moreList.classList.remove('open');
                                moreToggle && moreToggle.setAttribute('aria-expanded', 'false');
                                moreList.setAttribute('aria-hidden', 'true');
                            }
                        } else {
                            more.style.display = 'block';
                        }
                    }

                    // Toggle more-list on click (desktop)
                    // Toggle more-list on click (desktop) and support closing on outside click / Esc
                    const moreToggleBtn = navLinksContainer.querySelector('.more-toggle');
                    const moreContainer = navLinksContainer.querySelector('.more');
                    const moreListEl = moreContainer ? moreContainer.querySelector('.more-list') : null;

                    if (moreToggleBtn && moreListEl) {
                        moreToggleBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            const isOpen = moreListEl.classList.toggle('open');
                            moreToggleBtn.setAttribute('aria-expanded', isOpen);
                            moreListEl.setAttribute('aria-hidden', !isOpen);
                        });

                        // Close when clicking outside
                        document.addEventListener('click', (ev) => {
                            if (!moreContainer.contains(ev.target) && moreListEl.classList.contains('open')) {
                                moreListEl.classList.remove('open');
                                moreToggleBtn.setAttribute('aria-expanded', 'false');
                                moreListEl.setAttribute('aria-hidden', 'true');
                            }
                        });

                        // Close with Escape key
                        document.addEventListener('keydown', (ev) => {
                            if (ev.key === 'Escape' && moreListEl.classList.contains('open')) {
                                moreListEl.classList.remove('open');
                                moreToggleBtn.setAttribute('aria-expanded', 'false');
                                moreListEl.setAttribute('aria-hidden', 'true');
                            }
                        });
                    }

                    // Debounced resize to redistribute
                    let _redistributeTimer = null;
                    window.addEventListener('resize', () => {
                        clearTimeout(_redistributeTimer);
                        _redistributeTimer = setTimeout(redistributeMenu, 120);
                    });

                    // Initial run after short delay
                    setTimeout(redistributeMenu, 250);
                    // After inserting links, check if the menu is too long for the header space
                    function checkLongMenu() {
                        const nav = document.getElementById('main-nav-links');
                        const navbar = document.querySelector('.navbar');
                        const logo = document.querySelector('.logo');
                        const donate = document.querySelector('.btn-donate');
                        if (!nav || !navbar) return;

                        // Available space for nav = navbar width minus logo and donate widths (with buffer)
                        const navbarWidth = navbar.clientWidth;
                        const logoWidth = logo ? logo.offsetWidth : 0;
                        const donateWidth = donate ? donate.offsetWidth : 0;
                        const buffer = 80; // breathing room for gaps/padding
                        const available = navbarWidth - (logoWidth + donateWidth + buffer);

                        // Total width of nav items
                        let linksWidth = 0;
                        Array.from(nav.children).forEach(li => {
                            linksWidth += li.offsetWidth;
                        });

                        if (linksWidth > available) {
                            nav.classList.add('long-menu');
                        } else {
                            nav.classList.remove('long-menu');
                        }
                    }

                    // Debounced resize listener
                    let _menuResizeTimer = null;
                    window.addEventListener('resize', () => {
                        clearTimeout(_menuResizeTimer);
                        _menuResizeTimer = setTimeout(checkLongMenu, 120);
                    });

                    // Run check after a short delay to allow fonts/images to settle
                    setTimeout(checkLongMenu, 200);
                }
                
                // CRITICAL FIX: Initialize mobile menu logic immediately after header injection
                const toggleButton = document.querySelector('.menu-toggle');
                const navLinks = document.getElementById('main-nav-links');

                if (toggleButton && navLinks) {
                    toggleButton.addEventListener('click', () => {
                        navLinks.classList.toggle('open');
                        
                        const isExpanded = navLinks.classList.contains('open');
                        toggleButton.setAttribute('aria-expanded', isExpanded);

                        const icon = toggleButton.querySelector('i');
                        icon.classList.toggle('fa-bars');
                        icon.classList.toggle('fa-times');
                    });
                }
            }
        })
        .catch(error => console.error('Error loading header. Please check the file path and local server setup:', error));

    // 2. Load Footer Content and Inject
    fetch(footerPath)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.text();
        })
        .then(footerContent => {
            const footerPlaceholder = document.getElementById('footer-placeholder');
            if (footerPlaceholder) {
                // Use outerHTML to replace the placeholder div with the actual footer content
                footerPlaceholder.outerHTML = footerContent; 
            }
        })
        .catch(error => console.error('Error loading footer. Please check the file path and local server setup:', error));
}