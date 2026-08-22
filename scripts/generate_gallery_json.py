#!/usr/bin/env python3
"""
Generate gallery.html and gallery.js from cloudinary_event_mapping_enhanced.json
Embeds all event data and images for dynamic gallery rendering
"""

import json

# Load the enhanced event mapping
with open('cloudinary_event_mapping_enhanced.json', 'r') as f:
    events_data = json.load(f)

# Create gallery.js with embedded data
gallery_js_content = f'''// Cloudinary configuration
const CLOUDINARY_CLOUD_NAME = 'du0lumtob';
const CLOUDINARY_BASE_URL = `https://res.cloudinary.com/${{CLOUDINARY_CLOUD_NAME}}/image/upload`;

// EMBEDDED EVENT DATA FROM cloudinary_event_mapping_enhanced.json
// Auto-generated - do not edit manually
// To update: Re-run scripts/generate_gallery_json.py
const EVENT_MAPPING_DATA = {json.dumps(events_data, indent=2)};

/**
 * Format date from various formats
 * Handles timestamps, date strings, and year numbers
 */
function formatDate(dateValue) {{
    if (!dateValue) return "?";
    
    // Handle timestamp (milliseconds)
    if (typeof dateValue === 'number' && dateValue > 10000000000) {{
        const date = new Date(dateValue);
        return date.toLocaleDateString('en-US', {{ month: 'short', year: '2-digit' }});
    }}
    
    // Handle date string like "Jul-2023"
    if (typeof dateValue === 'string' && dateValue.includes('-')) {{
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const parts = dateValue.split('-');
        
        // Check if it's "Jul-2023" format
        const monthIndex = months.indexOf(parts[0]);
        if (monthIndex !== -1 && parts[1]) {{
            const year = parts[1].slice(-2);
            return `${{parts[0]}}'${{year}}`;
        }}
        
        // Check if it's "2025-01-23" format
        if (dateValue.match(/^\\d{{4}}-\\d{{2}}-\\d{{2}}/)) {{
            const date = new Date(dateValue);
            return date.toLocaleDateString('en-US', {{ month: 'short', year: '2-digit' }});
        }}
    }}
    
    return String(dateValue);
}}

/**
 * Get URL parameters and load event data
 */
function initializeGallery() {{
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const folderName = urlParams.get('folder');
    const eventName = urlParams.get('name');
    const eventDate = urlParams.get('date');
    
    if (!folderName) {{
        document.getElementById('gallery-grid').innerHTML = '<div class="loading">No folder specified</div>';
        return;
    }}
    
    // Find event in embedded data
    const eventData = EVENT_MAPPING_DATA.find(e => e.cloudinary_folder === folderName);
    
    if (!eventData) {{
        console.error(`Event not found: ${{folderName}}`);
        document.getElementById('gallery-grid').innerHTML = `
            <div class="loading">
                <p>Event data for "${{folderName}}" not found</p>
                <p><a href="events.html">← Back to Events</a></p>
            </div>
        `;
        return;
    }}
    
    // Display event information
    const details = eventData.event_details || {{}};
    const displayName = details.name || eventData.event_name;
    const photoCount = eventData.cloudinary_urls ? eventData.cloudinary_urls.length : eventData.image_count || 0;
    
    document.getElementById('event-title').textContent = displayName;
    document.getElementById('event-date').textContent = `📅 ${{formatDate(details.date || details.year)}}`;
    document.getElementById('photo-count').textContent = `📷 ${{photoCount}} photos`;
    
    if (details.venue) {{
        const venueEl = document.createElement('p');
        venueEl.style.marginTop = '10px';
        venueEl.innerHTML = `<i class="fas fa-map-marker-alt"></i> ${{details.venue}}`;
        document.querySelector('.gallery-header').appendChild(venueEl);
    }}
    
    // Set page title
    document.title = `${{displayName}} - Gallery`;
    
    // Generate gallery
    const galleryGrid = document.getElementById('gallery-grid');
    galleryGrid.innerHTML = '';
    
    const images = eventData.cloudinary_urls || [];
    
    if (images.length === 0) {{
        galleryGrid.innerHTML = '<div class="loading">No images found for this event</div>';
        return;
    }}
    
    images.forEach((url, index) => {{
        // Create responsive thumbnail URL with smart cropping
        const thumbnailUrl = url.replace(
            '/upload/',
            '/upload/w_350,h_260,c_fill,g_auto,q_auto,f_auto/'
        );
        
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.innerHTML = `<img src="${{thumbnailUrl}}" alt="Photo ${{index + 1}}" loading="lazy" data-full="${{url}}" data-index="${{index}}">`;
        
        item.addEventListener('click', () => openLightbox(index, images));
        
        galleryGrid.appendChild(item);
    }});
}}

// Lightbox functionality
let currentIndex = 0;
let currentImages = [];
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');

function openLightbox(index, images) {{
    currentIndex = index;
    currentImages = images;
    showImage(index);
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}}

function closeLightbox() {{
    lightbox.classList.remove('active');
    document.body.style.overflow = 'auto';
}}

function showImage(index) {{
    if (!currentImages || index < 0 || index >= currentImages.length) return;
    
    // Use high-quality version for lightbox without any cropping
    const fullUrl = currentImages[index].replace(
        '/upload/',
        '/upload/w_1920,q_auto:good,f_auto/'
    );
    
    lightboxImg.src = fullUrl;
    document.querySelector('.lightbox-caption').textContent = `${{index + 1}} / ${{currentImages.length}}`;
}}

function nextImage() {{
    currentIndex = (currentIndex + 1) % currentImages.length;
    showImage(currentIndex);
}}

function prevImage() {{
    currentIndex = (currentIndex - 1 + currentImages.length) % currentImages.length;
    showImage(currentIndex);
}}

// Initialize gallery when DOM is ready
document.addEventListener('DOMContentLoaded', initializeGallery);

// Event listeners
document.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
document.querySelector('.lightbox-next').addEventListener('click', nextImage);
document.querySelector('.lightbox-prev').addEventListener('click', prevImage);

// Keyboard navigation
document.addEventListener('keydown', (e) => {{
    if (!lightbox.classList.contains('active')) return;
    
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowRight') nextImage();
    if (e.key === 'ArrowLeft') prevImage();
}});

// Close on background click
lightbox.addEventListener('click', (e) => {{
    if (e.target === lightbox) closeLightbox();
}});
'''

# Write gallery.js
with open('gallery.js', 'w', encoding='utf-8') as f:
    f.write(gallery_js_content)

print("✅ Generated gallery.js")
print(f"📊 Embedded {len(events_data)} events with all image URLs")
print(f"📋 Features:")
print(f"   • All {len(events_data)} events with full image galleries")
print(f"   • Dynamic gallery rendering from embedded JSON")
print(f"   • Gallery automatically displays event details")
print(f"   • Venue, date, and photo count displayed")
print(f"   • Responsive thumbnails with Cloudinary optimization")
print(f"   • Lightbox with keyboard navigation (Arrow keys, ESC)")
print(f"\n💡 To update after changing cloudinary_event_mapping_enhanced.json:")
print(f"   python3 scripts/generate_gallery_json.py")
