import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths
MAPPING_FILE = "cloudinary_event_mapping.json"
EVENTS_HTML = "events.html"
EVENTS_BACKUP = "events-backup.html"
GALLERY_HTML = "gallery.html"
GALLERY_CSS = "gallery.css"
GALLERY_JS = "gallery.js"

def format_date(date_str):
    """
    Convert date from YYYY-MM-DD to MMM'YY format
    Example: 2025-06-09 -> Jun'25
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime("%b'%y")
    except:
        return date_str

# Load mapping
with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    events = json.load(f)

print("🔄 Updating website files.. .\n")

# Step 1: Backup existing events.html
print("📋 Step 1: Backing up events.html...")
if Path(EVENTS_HTML).exists():
    shutil.copy2(EVENTS_HTML, EVENTS_BACKUP)
    print(f"   ✅ Backed up to: {EVENTS_BACKUP}\n")
else:
    print(f"   ⚠️  {EVENTS_HTML} not found - will create new file\n")

# Step 2: Generate updated events.html
print("📝 Step 2: Generating updated events.html...")

events_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Events Archive - Sanskriti & Sanskar</title>
    <!-- Font Awesome is linked here for icons (if any) in the main content -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Link the external CSS file for common styles -->
    <link rel="stylesheet" href="style.css"> 

    <style>
        /* --- PAGE SPECIFIC STYLES (EVENTS) --- */
        
        /* PAGE HEADER */
        .page-header {
            background-color: var(--secondary-color);
            color: var(--white);
            padding: 60px 5%;
            text-align: center;
        }
        .page-header h1 { font-size: 2.5rem; margin-bottom: 10px; }

        /* --- EVENTS GRID --- */
        .events-container { padding: 60px 5%; max-width: 1400px; margin: 0 auto; }
        
        .events-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
        }

        .event-card {
            background: var(--white);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            text-decoration: none;
            color: inherit;
        }

        .event-card:hover { 
            transform: translateY(-5px); 
            box-shadow: 0 10px 25px rgba(0,0,0,0.15); 
        }

        .card-image {
            height: 220px;
            overflow: hidden;
            position: relative;
        }

        .card-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: top;
            transition: transform 0.5s ease;
        }

        .event-card:hover .card-image img { transform: scale(1.05); }

        .date-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: var(--white);
            color: var(--secondary-color);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        .card-content { padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }
        .card-content h3 { 
            color: var(--secondary-color); 
            margin-bottom: 10px; 
            font-size: 1.1rem; 
            line-height: 1.4; 
            min-height: 3em; 
        }
        .event-meta { margin-top: auto; color: var(--text-light); font-size: 0.9rem; border-top: 1px solid #eee; padding-top: 10px; }
        .event-meta div { display: flex; align-items: center; gap: 8px; margin-top: 5px; }

        @media (max-width: 768px) {
            .card-content h3 { min-height: unset; }
        }
    </style>
</head>
<body>

<!-- 1. HEADER PLACEHOLDER -->
<div id="header-placeholder"></div>

<main>
    <div class="page-header">
        <h1>Events Archive</h1>
        <p>A Visual Journey of Our Community Moments</p>
    </div>

    <section class="events-container">
        <div class="events-grid">
"""

# Sort events by date (newest first)
sorted_events = sorted(events, key=lambda x: x['event_date'], reverse=True)

for event in sorted_events:
    if event['photo_count'] > 0:
        # Get first image URL and create thumbnail version
        first_image = event['cloudinary_urls'][0]
        
        # Cloudinary transformation for thumbnail: width=400, height=300, crop=fit with white background to avoid cropping
        thumbnail_url = first_image.replace(
            '/upload/',
            '/upload/w_400,h_300,c_fit,q_auto,f_auto,b_white/'
        )
        
        # Format date to MMM'YY style
        formatted_date = format_date(event['event_date'])
        
        # Create gallery link with URL parameters
        gallery_link = f"gallery.html?folder={event['cloudinary_folder']}&name={event['event_name']}&date={event['event_date']}"
        
        events_html += f"""
            <a href="{gallery_link}" class="event-card">
                <div class="card-image">
                    <span class="date-badge">{formatted_date}</span>
                    <img 
                        src="{thumbnail_url}" 
                        alt="{event['event_name']}"
                        loading="lazy"
                    >
                </div>
                <div class="card-content">
                    <h3>{event['event_name']}</h3>
                    <div class="event-meta">
                        <div><i class="fas fa-calendar-alt"></i> {event['photo_count']} photos</div>
                    </div>
                </div>
            </a>
"""

events_html += """
        </div>
    </section>
</main>

<!-- 2. FOOTER PLACEHOLDER -->
<div id="footer-placeholder"></div>

<!-- 3. INCLUDE JAVASCRIPT -->
<script src="include.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', () => {
        loadComponents('Events Archive - Sanskriti & Sanskar', 'events.html');
    });
</script>
</body>
</html>
"""

# Save events.html
with open(EVENTS_HTML, 'w', encoding='utf-8') as f:
    f.write(events_html)

print(f"   ✅ Created {EVENTS_HTML} with {len([e for e in events if e['photo_count'] > 0])} events\n")

# Step 3: Generate gallery.html
print("📝 Step 3: Generating gallery.html...")

gallery_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Event Gallery</title>
    <link rel="stylesheet" href="gallery. css">
</head>
<body>
    <div class="gallery-container">
        <header class="gallery-header">
            <a href="events.html" class="back-button">← Back to Events</a>
            <h1 id="event-title">Loading...</h1>
            <p id="event-date"></p>
            <p id="photo-count"></p>
        </header>
        
        <div id="gallery-grid" class="gallery-grid">
            <div class="loading">Loading photos...</div>
        </div>
    </div>
    
    <!-- Lightbox -->
    <div id="lightbox" class="lightbox">
        <span class="lightbox-close">&times;</span>
        <span class="lightbox-prev">&#10094;</span>
        <span class="lightbox-next">&#10095;</span>
        <img id="lightbox-img" src="" alt="">
        <div class="lightbox-caption"></div>
    </div>
    
    <script src="gallery.js"></script>
</body>
</html>
"""

with open(GALLERY_HTML, 'w', encoding='utf-8') as f:
    f.write(gallery_html)

print(f"   ✅ Created {GALLERY_HTML}\n")

# Step 4: Generate gallery.css
print("📝 Step 4: Generating gallery.css...")

gallery_css = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f5f5;
}

.gallery-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

.gallery-header {
    text-align: center;
    margin-bottom: 30px;
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.back-button {
    display: inline-block;
    background: #4ecdc4;
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    text-decoration: none;
    margin-bottom: 20px;
    transition: background 0.3s ease;
}

.back-button:hover {
    background: #45b8b0;
}

#event-title {
    font-size: 2em;
    color: #333;
    margin-bottom: 10px;
}

#event-date {
    color: #ff6b6b;
    font-size: 1.1em;
    margin-bottom: 5px;
}

#photo-count {
    color: #666;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
}

.gallery-item {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: transform 0.3s ease;
    background: white;
    aspect-ratio: 4/3;
}

.gallery-item:hover {
    transform: scale(1.05);
}

.gallery-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.loading {
    text-align: center;
    padding: 40px;
    color: #666;
    font-size: 1.2em;
}

/* Lightbox */
.lightbox {
    display: none;
    position: fixed;
    z-index: 1000;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.95);
}

.lightbox.active {
    display: flex;
    align-items: center;
    justify-content: center;
}

.lightbox img {
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
}

.lightbox-close {
    position: absolute;
    top: 20px;
    right: 40px;
    color: white;
    font-size: 40px;
    font-weight: bold;
    cursor: pointer;
    z-index: 1001;
}

.lightbox-close:hover {
    color: #ff6b6b;
}

.lightbox-prev,
.lightbox-next {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    color: white;
    font-size: 60px;
    font-weight: bold;
    cursor: pointer;
    padding: 20px;
    user-select: none;
    z-index: 1001;
}

.lightbox-prev:hover,
.lightbox-next:hover {
    color: #4ecdc4;
}

.lightbox-prev {
    left: 20px;
}

.lightbox-next {
    right: 20px;
}

.lightbox-caption {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    color: white;
    font-size: 1.1em;
    background: rgba(0, 0, 0, 0.7);
    padding: 10px 20px;
    border-radius: 6px;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .gallery-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 10px;
    }
    
    #event-title {
        font-size: 1.5em;
    }
    
    .lightbox-prev,
    .lightbox-next {
        font-size: 40px;
        padding: 10px;
    }
}
"""

with open(GALLERY_CSS, 'w', encoding='utf-8') as f:
    f.write(gallery_css)

print(f"   ✅ Created {GALLERY_CSS}\n")

# Step 5: Generate gallery.js
print("📝 Step 5: Generating gallery.js...")

gallery_js = """// Cloudinary configuration
const CLOUDINARY_CLOUD_NAME = 'du0lumtob';
const CLOUDINARY_BASE_URL = `https://res.cloudinary.com/${CLOUDINARY_CLOUD_NAME}/image/upload`;

// Format date from YYYY-MM-DD to MMM'YY
function formatDate(dateStr) {
    try {
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const parts = dateStr.split('-');
        const year = parts[0].slice(2); // Get last 2 digits of year
        const monthIndex = parseInt(parts[1]) - 1;
        return `${months[monthIndex]}'${year}`;
    } catch {
        return dateStr;
    }
}

// Event mapping data
const EVENT_MAPPING = """ + json.dumps(events, indent=2) + """;

// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const folderName = urlParams.get('folder');
const eventName = urlParams.get('name');
const eventDate = urlParams.get('date');

// Find event in mapping
const eventData = EVENT_MAPPING.find(e => e.cloudinary_folder === folderName);

if (!eventData) {
    document.getElementById('gallery-grid').innerHTML = '<div class="loading">Event not found</div>';
} else {
    // Update header with formatted date
    document.getElementById('event-title').textContent = eventData.event_name;
    document.getElementById('event-date').textContent = `📅 ${formatDate(eventData.event_date)}`;
    document.getElementById('photo-count').textContent = `📷 ${eventData.photo_count} photos`;
    
    // Set page title
    document.title = `${eventData.event_name} - Gallery`;
    
    // Generate gallery
    const galleryGrid = document.getElementById('gallery-grid');
    galleryGrid.innerHTML = '';
    
    eventData.cloudinary_urls.forEach((url, index) => {
        // Create responsive thumbnail URL with smart cropping (c_fill,g_auto)
        const thumbnailUrl = url.replace(
            '/upload/',
            '/upload/w_350,h_260,c_fill,g_auto,q_auto,f_auto/'
        );
        
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.innerHTML = `<img src="${thumbnailUrl}" alt="Photo ${index + 1}" loading="lazy" data-full="${url}" data-index="${index}">`;
        
        item.addEventListener('click', () => openLightbox(index));
        
        galleryGrid.appendChild(item);
    });
}

// Lightbox functionality
let currentIndex = 0;
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');

function openLightbox(index) {
    currentIndex = index;
    showImage(index);
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    lightbox.classList.remove('active');
    document.body.style.overflow = 'auto';
}

function showImage(index) {
    if (!eventData || index < 0 || index >= eventData.cloudinary_urls.length) return;
    
    // Use high-quality version for lightbox without any cropping
    const fullUrl = eventData.cloudinary_urls[index].replace(
        '/upload/',
        '/upload/w_1920,q_auto:good,f_auto/'
    );
    
    lightboxImg.src = fullUrl;
    document.querySelector('.lightbox-caption').textContent = `${index + 1} / ${eventData.cloudinary_urls.length}`;
}

function nextImage() {
    currentIndex = (currentIndex + 1) % eventData.cloudinary_urls.length;
    showImage(currentIndex);
}

function prevImage() {
    currentIndex = (currentIndex - 1 + eventData.cloudinary_urls.length) % eventData.cloudinary_urls.length;
    showImage(currentIndex);
}

// Event listeners
document.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
document.querySelector('.lightbox-next').addEventListener('click', nextImage);
document.querySelector('.lightbox-prev').addEventListener('click', prevImage);

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('active')) return;
    
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowRight') nextImage();
    if (e.key === 'ArrowLeft') prevImage();
});

// Close on background click
lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
});
"""

with open(GALLERY_JS, 'w', encoding='utf-8') as f:
    f.write(gallery_js)

print(f"   ✅ Created {GALLERY_JS}\n")

print("="*70)
print("✅ Website update complete!")
print("\nFiles created/updated:")
print(f"   📋 {EVENTS_BACKUP} (backup)")
print(f"   📄 {EVENTS_HTML} (updated with thumbnails)")
print(f"   📄 {GALLERY_HTML} (dynamic gallery page)")
print(f"   🎨 {GALLERY_CSS} (gallery styles)")
print(f"   ⚡ {GALLERY_JS} (gallery functionality)")
print("="*70)
print("\n🚀 Next steps:")
print("   1. Test locally:  Open events.html in your browser")
print("   2. Push to GitHub:")
print("      git add events.html events-backup.html gallery.html gallery. css gallery.js")
print("      git commit -m 'Update events gallery with Cloudinary integration'")
print("      git push")
print("\n📱 Features:")
print("   ✅ Responsive thumbnails (optimized for mobile)")
print("   ✅ Lazy loading for better performance")
print("   ✅ Automatic image optimization via Cloudinary")
print("   ✅ Full-screen lightbox with keyboard navigation")
print("   ✅ Generic gallery. html works for all events")
