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
                    const links = [
                        { text: 'Home', href: 'index.html' },
                        { text: 'About', href: 'about.html' },
                        { text: 'Events', href: 'events.html' },
                        { text: 'Donations', href: 'donations.html' },
                        { text: 'News', href: 'news.html' },
                        { text: 'Sponsors', href: 'sponsors.html' },
                        { text: 'The Tulips Lounge', href: 'tulip-lounge.html' },
                        { text: 'Bhartiya First Conclave', href: 'bhartiyafirst.html' },
                        { text: 'Contact Us', href: 'contact.html' },
                    ];

                    let navHtml = links.map(link => {
                        // Check if the link matches the current page, or if the current page is the specific Bhartiya First page
                        const isActive = (link.href === activePage) || (link.href === 'bhartiyafirst.html' && activePage === 'bhartiyafirst.html');
                        const className = isActive ? 'active' : '';
                        return `<li><a href="${link.href}" class="${className}">${link.text}</a></li>`;
                    }).join('');

                    // Add Donate Button
                    navHtml += '<li><a href="donations.html" class="btn-donate">Donate Now</a></li>';
                    
                    navLinksContainer.innerHTML = navHtml;
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