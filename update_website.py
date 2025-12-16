import json
import shutil
from pathlib import Path

# Paths
MAPPING_FILE = "cloudinary_event_mapping.json"
EVENTS_HTML = "events.html"
EVENTS_BACKUP = "events-backup.html"
GALLERY_HTML = "gallery.html"
GALLERY_CSS = "gallery.css"
GALLERY_JS = "gallery.js"

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
    <title>Events Gallery - Sanskriti & Sanskar</title>
    <style>
        * {
            margin:  0;
            padding: 0;
            box-sizing:  border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background:  #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size:  2.5em;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size:  1.1em;
        }
        
        .events-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .event-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        
        .event-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        
        .event-thumbnail {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #e0e0e0;
        }
        
        .event-info {
            padding: 20px;
        }
        
        .event-title {
            font-size:  1.2em;
            font-weight:  600;
            color: #333;
            margin-bottom: 8px;
            line-height: 1.3;
        }
        
        . event-meta {
            display: flex;
            justify-content: space-between;
            color: #666;
            font-size: 0.9em;
            margin-top: 12px;
        }
        
        .event-date {
            color: #ff6b6b;
            font-weight: 500;
        }
        
        .photo-count {
            background: #4ecdc4;
            color: white;
            padding: 4px 12px;
            border-radius:  20px;
            font-size:  0.85em;
        }
        
        @media (max-width: 768px) {
            .events-grid {
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 15px;
            }
            
            h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Events Gallery</h1>
        <p class="subtitle">Sanskriti & Sanskar - Celebrating Indian Culture in the Netherlands</p>
        
        <div class="events-grid">
"""

# Sort events by date (newest first)
sorted_events = sorted(events, key=lambda x: x['event_date'], reverse=True)

for event in sorted_events:
    if event['photo_count'] > 0:
        # Get first image URL and create thumbnail version
        first_image = event['cloudinary_urls'][0]
        
        # Cloudinary transformation for thumbnail:  width=400, height=300, crop=fill, quality=auto
        thumbnail_url = first_image. replace(
            '/upload/',
            '/upload/w_400,h_300,c_fill,q_auto,f_auto/'
        )
        
        # Create gallery link with URL parameters
        gallery_link = f"gallery.html?folder={event['cloudinary_folder']}&name={event['event_name']}&date={event['event_date']}"
        
        events_html += f"""
            <a href="{gallery_link}" class="event-card">
                <img 
                    src="{thumbnail_url}" 
                    alt="{event['event_name']}"
                    class="event-thumbnail"
                    loading="lazy"
                >
                <div class="event-info">
                    <div class="event-title">{event['event_name']}</div>
                    <div class="event-meta">
                        <span class="event-date">📅 {event['event_date']}</span>
                        <span class="photo-count">📷 {event['photo_count']} photos</span>
                    </div>
                </div>
            </a>
"""

events_html += """
        </div>
    </div>
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
    border-radius:  12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.back-button {
    display: inline-block;
    background: #4ecdc4;
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    text-decoration:  none;
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
    margin-bottom:  5px;
}

#photo-count {
    color: #666;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

.gallery-item {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: transform 0.3s ease;
    background: white;
}

.gallery-item:hover {
    transform: scale(1.05);
}

.gallery-item img {
    width: 100%;
    height: 250px;
    object-fit:  cover;
    display: block;
}

.loading {
    text-align: center;
    padding:  40px;
    color: #666;
    font-size: 1.2em;
}

/* Lightbox */
.lightbox {
    display: none;
    position: fixed;
    z-index: 1000;
    top: 0;
    left:  0;
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
    object-fit:  contain;
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
    transform:  translateY(-50%);
    color: white;
    font-size: 60px;
    font-weight:  bold;
    cursor: pointer;
    padding: 20px;
    user-select: none;
    z-index: 1001;
}

.lightbox-prev: hover,
.lightbox-next:hover {
    color: #4ecdc4;
}

. lightbox-prev {
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
    
    .gallery-item img {
        height: 150px;
    }
    
    #event-title {
        font-size: 1.5em;
    }
    
    . lightbox-prev,
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

// Event mapping data
const EVENT_MAPPING = """ + json.dumps(events, indent=2) + """;

// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const folderName = urlParams.get('folder');
const eventName = urlParams.get('name');
const eventDate = urlParams.get('date');

// Find event in mapping
const eventData = EVENT_MAPPING.find(e => e. cloudinary_folder === folderName);

if (! eventData) {
    document.getElementById('gallery-grid').innerHTML = '<div class="loading">Event not found</div>';
} else {
    // Update header
    document.getElementById('event-title').textContent = eventData.event_name;
    document.getElementById('event-date').textContent = `📅 ${eventData.event_date}`;
    document.getElementById('photo-count').textContent = `📷 ${eventData.photo_count} photos`;
    
    // Set page title
    document.title = `${eventData.event_name} - Gallery`;
    
    // Generate gallery
    const galleryGrid = document.getElementById('gallery-grid');
    galleryGrid.innerHTML = '';
    
    eventData.cloudinary_urls.forEach((url, index) => {
        // Create responsive thumbnail URL
        // Desktop: 400px wide, Mobile: 300px wide
        const thumbnailUrl = url.replace(
            '/upload/',
            '/upload/w_400,h_300,c_fill,q_auto,f_auto,dpr_auto/'
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
    document.body.style. overflow = 'auto';
}

function showImage(index) {
    if (! eventData || index < 0 || index >= eventData.cloudinary_urls.length) return;
    
    // Use high-quality version for lightbox
    const fullUrl = eventData.cloudinary_urls[index]. replace(
        '/upload/',
        '/upload/w_1920,q_auto,f_auto/'
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
