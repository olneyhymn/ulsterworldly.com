(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    geojsonUrl: '/data/hopper-locations.geojson',
    initialCenter: [37.6, -84.8], // Central Kentucky
    initialZoom: 8,
    maxZoom: 18,
    tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  };

  // Color scheme for location types
  const COLORS = {
    church: '#dc3545',
    educational: '#007bff',
    burial: '#6c757d',
    residence: '#28a745',
    event: '#ffc107',
    default: '#6c757d'
  };

  // Global state
  let map;
  let markersLayer;
  let geojsonData;
  let currentFilter = 'all';

  // Initialize map on page load
  // Since this script is loaded dynamically after page load,
  // check if DOM is ready or run immediately
  function init() {
    if (document.getElementById('hopper-map')) {
      initMap();
      loadGeoJSON();
      setupFilterButtons();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // DOM already loaded, run immediately
    init();
  }

  function initMap() {
    map = L.map('hopper-map').setView(CONFIG.initialCenter, CONFIG.initialZoom);

    L.tileLayer(CONFIG.tileLayer, {
      maxZoom: CONFIG.maxZoom,
      attribution: CONFIG.attribution
    }).addTo(map);

    markersLayer = L.layerGroup().addTo(map);
  }

  function loadGeoJSON() {
    fetch(CONFIG.geojsonUrl)
      .then(response => response.json())
      .then(data => {
        geojsonData = data;
        displayMarkers(data.features);
      })
      .catch(error => {
        console.error('Error loading GeoJSON:', error);
        showError('Failed to load location data. Please try refreshing the page.');
      });
  }

  function displayMarkers(features) {
    markersLayer.clearLayers();

    features.forEach(feature => {
      if (shouldShowFeature(feature)) {
        createMarker(feature);
      }
    });

    // Fit map to markers if any are displayed
    if (markersLayer.getLayers().length > 0) {
      const group = new L.featureGroup(markersLayer.getLayers());
      map.fitBounds(group.getBounds().pad(0.1));
    }
  }

  function shouldShowFeature(feature) {
    if (currentFilter === 'all') return true;
    return feature.properties.type === currentFilter;
  }

  function createMarker(feature) {
    const coords = feature.geometry.coordinates;
    const props = feature.properties;

    // Create custom icon
    const icon = L.divIcon({
      className: 'custom-marker',
      html: `<div style="background-color: ${COLORS[props.type] || COLORS.default}; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    const marker = L.marker([coords[1], coords[0]], { icon: icon });

    // Create popup content
    const popupContent = createPopupContent(props);
    marker.bindPopup(popupContent, { maxWidth: 300 });

    marker.addTo(markersLayer);
  }

  function createPopupContent(props) {
    let html = `<div class="map-popup">`;
    html += `<h6 class="mb-2"><strong>${escapeHtml(props.name)}</strong></h6>`;
    html += `<p class="small mb-1">${escapeHtml(props.description)}</p>`;

    if (props.family_members && props.family_members.length > 0) {
      html += `<p class="small mb-1"><strong>Family:</strong> ${escapeHtml(props.family_members.slice(0, 2).join(', '))}`;
      if (props.family_members.length > 2) {
        html += ` and ${props.family_members.length - 2} more`;
      }
      html += `</p>`;
    }

    html += `<button class="btn btn-sm btn-primary mt-2" onclick="window.showLocationDetailsGlobal('${escapeHtml(props.name).replace(/'/g, "\\'")}')">More Details</button>`;
    html += `</div>`;

    return html;
  }

  function showLocationDetails(props) {
    // Set modal title
    document.getElementById('locationModalTitle').textContent = props.name;

    // Build modal body
    let html = `<div class="location-details">`;

    // Type badge
    html += `<span class="badge badge-secondary mb-3">${capitalize(props.type)}</span>`;

    // Description
    html += `<p>${escapeHtml(props.description)}</p>`;

    // Date range
    if (props.date_range) {
      html += `<p><strong>Period:</strong> ${escapeHtml(props.date_range)}</p>`;
    }

    // Family members
    if (props.family_members && props.family_members.length > 0) {
      html += `<p><strong>Hopper Family Members:</strong><br>`;
      html += props.family_members.map(m => `<span class="badge badge-info mr-1 mb-1">${escapeHtml(m)}</span>`).join('');
      html += `</p>`;
    }

    // Events
    if (props.events && props.events.length > 0) {
      html += `<p><strong>Notable Events:</strong></p><ul>`;
      props.events.forEach(event => {
        html += `<li>${escapeHtml(event)}</li>`;
      });
      html += `</ul>`;
    }

    // Blog posts
    if (props.blog_posts && props.blog_posts.length > 0) {
      html += `<p><strong>Related Blog Posts:</strong></p><ul>`;
      props.blog_posts.forEach(post => {
        const postTitle = post.split('/').filter(p => p).pop().replace(/-/g, ' ');
        html += `<li><a href="${escapeHtml(post)}" target="_blank">${capitalize(postTitle)}</a></li>`;
      });
      html += `</ul>`;
    }

    html += `</div>`;

    document.getElementById('locationModalBody').innerHTML = html;
    $('#locationModal').modal('show');
  }

  function setupFilterButtons() {
    const buttons = document.querySelectorAll('[data-filter]');
    buttons.forEach(button => {
      button.addEventListener('click', function() {
        // Update active state
        buttons.forEach(b => b.classList.remove('active'));
        this.classList.add('active');

        // Apply filter
        currentFilter = this.dataset.filter;
        if (geojsonData) {
          displayMarkers(geojsonData.features);
        }
      });
    });
  }

  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
  }

  function showError(message) {
    const mapDiv = document.getElementById('hopper-map');
    mapDiv.innerHTML = `<div class="alert alert-danger m-3">${escapeHtml(message)}</div>`;
  }

  // Make showLocationDetails globally accessible for popup buttons
  window.showLocationDetailsGlobal = function(name) {
    if (geojsonData) {
      const feature = geojsonData.features.find(f => f.properties.name === name);
      if (feature) {
        showLocationDetails(feature.properties);
      }
    }
  };

})();
