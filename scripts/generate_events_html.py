#!/usr/bin/env python3
"""
Generate dynamic events.html from cloudinary_event_mapping_enhanced.json
Embeds full event data in HTML for easy dynamic rendering
"""

import json

# Load the enhanced event mapping
with open('cloudinary_event_mapping_enhanced.json', 'r') as f:
    events_data = json.load(f)

# Create HTML with embedded JSON
html_content = f'''<!DOCTYPE html>
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
        .page-header {{
            background-color: var(--secondary-color);
            color: var(--white);
            padding: 60px 5%;
            text-align: center;
        }}
        .page-header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}

        /* --- EVENTS GRID --- */
        .events-container {{ padding: 60px 5%; max-width: 1400px; margin: 0 auto; }}
        
        .events-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
        }}

        .event-card {{
            background: var(--white);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            text-decoration: none;
            color: inherit;
        }}

        .event-card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 10px 25px rgba(0,0,0,0.15); 
        }}

        .card-image {{
            height: 220px;
            overflow: hidden;
            position: relative;
        }}

        .card-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: top;
            transition: transform 0.5s ease;
        }}

        .event-card:hover .card-image img {{ transform: scale(1.05); }}

        .date-badge {{
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
        }}

        .card-content {{ padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }}
        .card-content h3 {{ 
            color: var(--secondary-color); 
            margin-bottom: 10px; 
            font-size: 1.1rem; 
            line-height: 1.4; 
            min-height: 3em; 
        }}
        .event-meta {{ margin-top: auto; color: var(--text-light); font-size: 0.9rem; border-top: 1px solid #eee; padding-top: 10px; }}
        .event-meta div {{ display: flex; align-items: center; gap: 8px; margin-top: 5px; }}
        .event-venue {{ font-weight: 500; color: var(--secondary-color); }}

        @media (max-width: 768px) {{
            .card-content h3 {{ min-height: unset; }}
        }}
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
        <div class="events-grid" id="eventsGrid">
            <!-- Events will be generated dynamically here -->
        </div>
    </section>
</main>

<!-- EMBEDDED EVENT DATA - AUTO-GENERATED FROM cloudinary_event_mapping_enhanced.json -->
<!-- To update: Re-run generate_events_html.py script -->
<script type="application/json" id="eventsData">
{json.dumps(events_data, indent=2)}
</script>

<!-- SCRIPTS -->
<script>
/**
 * DYNAMIC EVENTS RENDERER
 * This script reads event data from the embedded JSON and generates event cards
 * 
 * HOW TO UPDATE:
 * 1. Update cloudinary_event_mapping_enhanced.json with new event data
 * 2. Run: python3 scripts/generate_events_html.py
 * 3. This will regenerate events.html with the latest data
 * 4. No manual HTML editing needed!
 */

function formatDateBadge(dateValue) {{
    /**
     * Convert date to badge format
     * Handles timestamps (milliseconds), date strings, and year numbers
     * Examples: 1709251200000 → "Mar'24", "Jul-2023" → "Jul", 2024 → current month of 2024
     */
    if (!dateValue) return "?";
    
    // Handle timestamp (milliseconds)
    if (typeof dateValue === 'number' && dateValue > 10000000000) {{
        const date = new Date(dateValue);
        const month = date.toLocaleDateString('en-US', {{ month: 'short' }});
        const year = date.getFullYear().toString().slice(-2);
        return `${{month}}'${{year}}`;
    }}
    
    // Handle date string like "Jul-2023"
    if (typeof dateValue === 'string' && dateValue.includes('-')) {{
        const parts = dateValue.split('-');
        return parts[0];
    }}
    
    // Handle date string like "2025-01-23"
    if (typeof dateValue === 'string' && dateValue.match(/^\d{{4}}-\d{{2}}-\d{{2}}/)) {{
        const date = new Date(dateValue);
        const month = date.toLocaleDateString('en-US', {{ month: 'short' }});
        const year = date.getFullYear().toString().slice(-2);
        return `${{month}}'${{year}}`;
    }}
    
    // Fallback: just return year
    return dateValue;
}}

function getFirstImageUrl(urls) {{
    /**
     * Get the first valid image URL from the cloudinary_urls array
     * Falls back to placeholder if no URLs available
     */
    if (Array.isArray(urls) && urls.length > 0) {{
        return urls[0];
    }}
    return "https://via.placeholder.com/400x300?text=Event+Photo";
}}

function createEventCard(event) {{
    /**
     * Create an event card element from event data
     * Structure matches the original events.html design
     */
    const details = event.event_details || {{}};
    const venue = details.venue ? ` @${{details.venue}}` : '';
    const displayName = details.name || event.event_name;
    const dateBadge = formatDateBadge(details.date || details.year);
    const imageUrl = getFirstImageUrl(event.cloudinary_urls);
    const photoCount = event.image_count || 0;
    
    // Create gallery link with query parameters
    const galleryLink = `gallery.html?folder=${{encodeURIComponent(event.cloudinary_folder)}}&name=${{encodeURIComponent(displayName)}}&date=${{details.date || ''}}`;
    
    // Create card HTML
    const card = document.createElement('a');
    card.href = galleryLink;
    card.className = 'event-card';
    card.innerHTML = `
        <div class="card-image">
            <span class="date-badge">${{dateBadge}}</span>
            <img 
                src="${{imageUrl}}" 
                alt="${{displayName}}"
                loading="lazy"
                onerror="this.src='https://via.placeholder.com/400x300?text=Event+Photo'"
            >
        </div>
        <div class="card-content">
            <h3>${{displayName}}</h3>
            <div class="event-meta">
                ${{details.venue ? `<div><i class="fas fa-map-marker-alt"></i><span class="event-venue">${{details.venue}}</span></div>` : ''}}
                <div><i class="fas fa-images"></i> ${{photoCount}} photos</div>
            </div>
        </div>
    `;
    
    return card;
}}

function renderEvents() {{
    /**
     * Main render function
     * Reads event JSON data and generates all event cards
     * Automatically called when page loads
     */
    try {{
        // Get embedded JSON data
        const jsonElement = document.getElementById('eventsData');
        const eventsData = JSON.parse(jsonElement.textContent);
        
        // Get grid container
        const grid = document.getElementById('eventsGrid');
        grid.innerHTML = ''; // Clear any existing content
        
        // Sort events by date (newest first)
        const sortedEvents = eventsData.sort((a, b) => {{
            const dateA = a.event_details?.date || a.event_details?.year || 0;
            const dateB = b.event_details?.date || b.event_details?.year || 0;
            return dateB - dateA;
        }});
        
        // Create and append cards for each event
        sortedEvents.forEach(event => {{
            if (event.event_name && event.cloudinary_urls && event.cloudinary_urls.length > 0) {{
                const card = createEventCard(event);
                grid.appendChild(card);
            }}
        }});
        
        console.log(`✅ Rendered ${{grid.children.length}} event cards from ${{eventsData.length}} events`);
        
    }} catch (error) {{
        console.error('❌ Error rendering events:', error);
        document.getElementById('eventsGrid').innerHTML = '<p style="color: red;">Error loading events. Please check the console.</p>';
    }}
}}

// Render events when page loads
document.addEventListener('DOMContentLoaded', renderEvents);
</script>

<!-- FOOTER PLACEHOLDER -->
<script>
    // Load header and footer from placeholders (keep existing pattern)
    document.addEventListener('DOMContentLoaded', function() {{
        const headerPlaceholder = document.getElementById('header-placeholder');
        if (headerPlaceholder) {{
            // Replace with actual header component if available
            headerPlaceholder.innerHTML = '<header><!-- Header goes here --></header>';
        }}
    }});
</script>

</body>
</html>
'''

# Write HTML file
with open('events.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Generated events.html")
print(f"📊 Embedded {len(events_data)} events")
print(f"📋 Features:")
print(f"   • Dynamic card generation from JSON")
print(f"   • Auto-sorted by date (newest first)")
print(f"   • Image lazy-loading with fallback")
print(f"   • Responsive grid layout")
print(f"   • Easy to update: just run this script again after updating JSON")
