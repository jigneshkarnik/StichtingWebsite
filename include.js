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
                        { text: 'Contact Us', href: 'contact.html' },
                        { text: 'Admin', href: 'admin.html' } // New Admin link
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