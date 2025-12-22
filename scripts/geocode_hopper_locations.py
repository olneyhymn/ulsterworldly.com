#!/usr/bin/env python3
"""
Geocode Hopper Family Kentucky Locations

This script geocodes Kentucky locations connected to the Hopper family
and generates a GeoJSON file for use with Leaflet maps.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


# Kentucky locations connected to the Hopper family
LOCATIONS = [
    {
        "name": "Stanford Presbyterian Church",
        "search_query": "Stanford Presbyterian Church, Stanford, Lincoln County, Kentucky",
        "type": "church",
        "family_members": ["Joseph Hopper", "George Dunlap Hopper", "William Higgins Hopper", "Margaret Higgins Hopper"],
        "events": ["Hopper Day celebration (August 2, 1936)", "Family worship location"],
        "date_range": "1800s-present",
        "description": "Primary Hopper family church in Stanford, Kentucky. George Dunlap Hopper served as deacon and ruling elder here for many years. Site of 'Hopper Day' celebration in 1936 honoring Joseph Hopper.",
        "blog_posts": ["/post/hopper-day-1936/", "/post/siblings-of-joseph-hopper/"],
        "fallback_coords": {"lat": 37.5312, "lon": -84.6619},  # Stanford, KY coordinates
    },
    {
        "name": "Perryville Presbyterian Church",
        "search_query": "Perryville Presbyterian Church, Perryville, Boyle County, Kentucky",
        "type": "church",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Uncle Joe's membership from 1851", "Uncle Joe served as ruling elder (1854)", "Uncle Joe served as clerk of session (1854-1875)"],
        "date_range": "1851-1915",
        "description": "Home church of 'Uncle Joe' Hopper, Kentucky evangelist. He was a member from 1851, ordained as ruling elder in 1854 at age 25, and served as clerk of session for over 20 years.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
        "fallback_coords": {"lat": 37.6504, "lon": -84.9516},  # Perryville, KY coordinates
    },
    {
        "name": "Buffalo Cemetery",
        "search_query": "Buffalo Cemetery, Stanford, Lincoln County, Kentucky",
        "type": "burial",
        "family_members": ["George Dunlap Hopper", "William M. Higgins"],
        "events": ["George Dunlap Hopper buried (1913)", "William M. Higgins buried"],
        "date_range": "1913-present",
        "description": "Cemetery near Stanford where George Dunlap Hopper (1848-1913) and William M. Higgins were buried.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Perryville Cemetery",
        "search_query": "Perryville Cemetery, Perryville, Kentucky",
        "type": "burial",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Uncle Joe Hopper buried (March 28, 1915)"],
        "date_range": "1915-present",
        "description": "Burial site of Joseph Hamilton 'Uncle Joe' Hopper (1829-1915), prominent Kentucky Presbyterian evangelist.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Centre College",
        "search_query": "Centre College, Danville, Kentucky",
        "type": "educational",
        "family_members": ["Joseph Hopper", "William Higgins Hopper", "George Dunlap Hopper Jr."],
        "events": ["Joseph Hopper graduated magna cum laude (1914)", "William Hopper graduated (1908)"],
        "date_range": "1900s-1910s",
        "description": "Presbyterian college in Danville where multiple Hopper family members studied. Joseph Hopper graduated magna cum laude in 1914, his brother William graduated in 1908.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Louisville Presbyterian Theological Seminary",
        "search_query": "Louisville Presbyterian Theological Seminary, Louisville, Kentucky",
        "type": "educational",
        "family_members": ["Joseph Hopper", "William Higgins Hopper", "Hershey Longenecker"],
        "events": ["Joseph Hopper graduated (1917)", "William Hopper graduated (1911)", "Hershey Longenecker attended (1913-1916)"],
        "date_range": "1911-1917",
        "description": "Presbyterian seminary in Louisville where Joseph Hopper graduated in 1917, his brother William graduated in 1911, and Joseph's father-in-law Hershey Longenecker attended 1913-1916.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Stanford, Kentucky",
        "search_query": "Stanford, Lincoln County, Kentucky",
        "type": "residence",
        "family_members": ["Joseph Hopper", "George Dunlap Hopper", "Margaret Higgins Hopper"],
        "events": ["Joseph Hopper born (June 1, 1892)", "George Dunlap Hopper moved here (1869)", "Hopper family home"],
        "date_range": "1869-1940s",
        "description": "Primary Hopper family town in Lincoln County. Joseph Hopper was born here in 1892. George Dunlap Hopper moved here in 1869 and farmed on the Danville pike at Hawkins' Branch.",
        "blog_posts": ["/post/hopper-day-1936/", "/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Lancaster, Kentucky",
        "search_query": "Lancaster, Garrard County, Kentucky",
        "type": "residence",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)", "George Dunlap Hopper"],
        "events": ["Uncle Joe Hopper born (July 22, 1829)", "George Dunlap Hopper born (October 29, 1848)"],
        "date_range": "1829-1869",
        "description": "Birthplace of both Uncle Joe Hopper (1829) and George Dunlap Hopper (1848).",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/", "/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Perryville, Kentucky",
        "search_query": "Perryville, Boyle County, Kentucky",
        "type": "residence",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Uncle Joe's home", "Base for evangelistic work"],
        "date_range": "1850s-1915",
        "description": "Home of Uncle Joe Hopper. He married Mary B. Mitchell, daughter of wealthy farmer from Boyle County, and lived in Perryville throughout his ministry.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Highland Church, Louisville",
        "search_query": "Highland Presbyterian Church, Louisville, Kentucky",
        "type": "church",
        "family_members": ["Joseph Hopper"],
        "events": ["Joseph Hopper served as stated supply (1919-1920)"],
        "date_range": "1919-1920",
        "description": "Louisville church where Joseph Hopper served as stated supply from 1919-1920 before departing for missionary work in Korea.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Maxwell Street Presbyterian Church, Lexington",
        "search_query": "Maxwell Street Presbyterian Church, Lexington, Kentucky",
        "type": "church",
        "family_members": ["Margaret Higgins Hopper"],
        "events": ["Margaret Hopper's membership"],
        "date_range": "1900s-1920s",
        "description": "Lexington church where Margaret Higgins Hopper was a member before becoming a missionary to Korea.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Woodland Presbyterian Church, Louisville",
        "search_query": "Woodland Presbyterian Church, Louisville, Kentucky",
        "type": "church",
        "family_members": ["William Higgins Hopper"],
        "events": ["William Hopper's pastorate"],
        "date_range": "1910s-1920s",
        "description": "Louisville church where William Higgins Hopper served as pastor.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
        "fallback_coords": {"lat": 38.2527, "lon": -85.7585},  # Louisville, KY coordinates
    },
    {
        "name": "Flora Heights Presbyterian Church, Louisville",
        "search_query": "Flora Heights Presbyterian Church, Louisville, Kentucky",
        "type": "church",
        "family_members": ["William Higgins Hopper"],
        "events": ["William Hopper's pastorate"],
        "date_range": "1920s-1930s",
        "description": "Louisville church where William Higgins Hopper served as pastor.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
        "fallback_coords": {"lat": 38.2527, "lon": -85.7585},  # Louisville, KY coordinates
    },
    {
        "name": "Twin Creek Church, Athol",
        "search_query": "Athol, Breathitt County, Kentucky",
        "type": "church",
        "family_members": ["Joseph Hopper"],
        "events": ["Joseph Hopper installed as pastor (1917)"],
        "date_range": "1917-1918",
        "description": "Mountain church in Breathitt County where Joseph Hopper was installed as pastor in 1917, part of his early ministry in eastern Kentucky.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Canyon Falls Church",
        "search_query": "Canyon Falls, Kentucky",
        "type": "church",
        "family_members": ["Joseph Hopper"],
        "events": ["Joseph Hopper installed as pastor (1917)"],
        "date_range": "1917-1918",
        "description": "Church where Joseph Hopper was installed as pastor in 1917, part of his early Kentucky ministry.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "St. Helens Church",
        "search_query": "St. Helens, Kentucky",
        "type": "church",
        "family_members": ["Joseph Hopper"],
        "events": ["Joseph Hopper installed as pastor (1917)"],
        "date_range": "1917-1918",
        "description": "Church where Joseph Hopper was installed as pastor in 1917, part of his early Kentucky ministry.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Berry Boulevard Church, Louisville",
        "search_query": "Berry Boulevard Presbyterian Church, Louisville, Kentucky",
        "type": "church",
        "family_members": ["Hershey Longenecker"],
        "events": ["Hershey Longenecker served as stated supply/pastor (1915-1917)"],
        "date_range": "1915-1917",
        "description": "Louisville church where Hershey Longenecker (Joseph Hopper's father-in-law) served as stated supply and pastor from 1915-1917.",
        "blog_posts": [],
        "fallback_coords": {"lat": 38.2527, "lon": -85.7585},  # Louisville, KY coordinates
    },
    {
        "name": "First Presbyterian Church, Louisville",
        "search_query": "First Presbyterian Church, Louisville, Kentucky",
        "type": "church",
        "family_members": ["Edward O. Guerrant"],
        "events": ["Edward O. Guerrant served before becoming evangelist"],
        "date_range": "1800s",
        "description": "Historic Louisville church where Edward O. Guerrant served before beginning his mountain mission work, which Uncle Joe Hopper later joined.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "First Presbyterian Church, Danville",
        "search_query": "First Presbyterian Church, Danville, Kentucky",
        "type": "church",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Uncle Joe briefly a member"],
        "date_range": "1850s",
        "description": "Danville church where Uncle Joe Hopper was briefly a member.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Burnside, Kentucky",
        "search_query": "Burnside, Pulaski County, Kentucky",
        "type": "church",
        "family_members": ["William Higgins Hopper"],
        "events": ["William Hopper's pastorate"],
        "date_range": "1910s-1920s",
        "description": "Town in Pulaski County where William Higgins Hopper served as pastor.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Stanford Female College",
        "search_query": "Stanford, Lincoln County, Kentucky",
        "type": "educational",
        "family_members": ["Margaret Higgins Hopper"],
        "events": ["Margaret Hopper attended (1900-1904)"],
        "date_range": "1900-1904",
        "description": "Women's college in Stanford where Margaret Higgins Hopper studied from 1900-1904.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
        "fallback_coords": {"lat": 37.5312, "lon": -84.6619},  # Stanford coordinates
    },
    {
        "name": "Sayre College, Lexington",
        "search_query": "Sayre School, Lexington, Kentucky",
        "type": "educational",
        "family_members": ["Margaret Higgins Hopper"],
        "events": ["Margaret Hopper attended"],
        "date_range": "1900s",
        "description": "Lexington educational institution where Margaret Higgins Hopper studied.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Stanford High School",
        "search_query": "Stanford High School, Stanford, Kentucky",
        "type": "educational",
        "family_members": ["Margaret Higgins Hopper"],
        "events": ["Margaret Hopper taught (1909-1941)"],
        "date_range": "1909-1941",
        "description": "High school in Stanford where Margaret Higgins Hopper taught for over 30 years, from 1909 to 1941.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
        "fallback_coords": {"lat": 37.5312, "lon": -84.6619},  # Stanford, KY coordinates
    },
    {
        "name": "Mt. Sterling, Kentucky",
        "search_query": "Mt. Sterling, Montgomery County, Kentucky",
        "type": "educational",
        "family_members": ["Walter Owsley Hopper"],
        "events": ["Walter Hopper served as high school superintendent"],
        "date_range": "1900s-1920s",
        "description": "Town in Montgomery County where Walter Owsley Hopper served as superintendent of the high school.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Harrodsburg, Kentucky",
        "search_query": "Harrodsburg, Mercer County, Kentucky",
        "type": "event",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Evangelistic meetings held by Uncle Joe"],
        "date_range": "1880s-1900s",
        "description": "Site of evangelistic meetings conducted by Uncle Joe Hopper during his ministry throughout Kentucky.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Salvisa, Kentucky",
        "search_query": "Salvisa, Mercer County, Kentucky",
        "type": "event",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)", "Edward O. Guerrant"],
        "events": ["Church organized by Guerrant and Uncle Joe"],
        "date_range": "1880s-1890s",
        "description": "Church organized by Edward O. Guerrant and Uncle Joe Hopper during their evangelistic work.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Hazel Green, Wolfe County",
        "search_query": "Hazel Green, Wolfe County, Kentucky",
        "type": "event",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Presbyterian Church organized (1896)"],
        "date_range": "1896",
        "description": "Mountain town in Wolfe County where a Presbyterian church was organized in 1896 through Uncle Joe's evangelistic work.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Somerset, Kentucky",
        "search_query": "Somerset, Pulaski County, Kentucky",
        "type": "event",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Evangelistic work location"],
        "date_range": "1880s-1900s",
        "description": "Town where Uncle Joe Hopper conducted evangelistic work.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Lawrenceburg, Kentucky",
        "search_query": "Lawrenceburg, Anderson County, Kentucky",
        "type": "event",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Evangelistic work location"],
        "date_range": "1880s-1900s",
        "description": "Town where Uncle Joe Hopper conducted evangelistic work.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Scottsville, Allen County",
        "search_query": "Scottsville, Allen County, Kentucky",
        "type": "event",
        "family_members": ["Joseph Hamilton Hopper (Uncle Joe)"],
        "events": ["Church organized"],
        "date_range": "1880s-1900s",
        "description": "Town in Allen County where a church was organized through Uncle Joe's evangelistic ministry.",
        "blog_posts": ["/post/uncle-joe-hopper-by-joseph-hopper/"],
    },
    {
        "name": "Corbin, Kentucky",
        "search_query": "Corbin, Whitley County, Kentucky",
        "type": "event",
        "family_members": ["Joseph Hopper"],
        "events": ["Preaching location"],
        "date_range": "1917-1919",
        "description": "Town where Joseph Hopper preached during his early Kentucky ministry.",
        "blog_posts": ["/post/siblings-of-joseph-hopper/"],
    },
    {
        "name": "Heidelburg, Lee County",
        "search_query": "Heidelberg, Lee County, Kentucky",
        "type": "educational",
        "family_members": ["Hershey Longenecker"],
        "events": ["Built Beechwood Seminary mission school building (1911)"],
        "date_range": "1911",
        "description": "Mountain village in Lee County where Hershey Longenecker and his brother Elmer built the Beechwood Seminary mission school building for Dr. Guerrant's Soul Winners Society.",
        "blog_posts": [],
    },
    {
        "name": "Beechwood Seminary, Heidelburg",
        "search_query": "Heidelberg, Lee County, Kentucky",
        "type": "educational",
        "family_members": ["Hershey Longenecker"],
        "events": ["Mission school built by Longenecker (1911)", "Elmer Longenecker served as principal"],
        "date_range": "1911-1913",
        "description": "Presbyterian mission school in the mountains of Lee County built by Hershey Longenecker. His brother Elmer remained as principal after construction was complete.",
        "blog_posts": [],
        "fallback_coords": {"lat": 37.5833, "lon": -83.7333},  # Heidelberg, Lee County approximate
    },
    {
        "name": "Stearns, Kentucky",
        "search_query": "Stearns, McCreary County, Kentucky",
        "type": "event",
        "family_members": ["Hershey Longenecker"],
        "events": ["Preaching assignment from Transylvania Presbytery"],
        "date_range": "1913",
        "description": "Mining town where the Presbytery of Transylvania sent Hershey Longenecker to preach before he entered Louisville Presbyterian Seminary.",
        "blog_posts": [],
    },
    {
        "name": "Rousseau, Quicksand Creek",
        "search_query": "Quicksand, Breathitt County, Kentucky",
        "type": "event",
        "family_members": ["Hershey Longenecker"],
        "events": ["Preached, taught school, lived in rough house beside church"],
        "date_range": "1912-1913",
        "description": "Remote mountain location on Quicksand Creek, 16 miles from the railroad, where Hershey Longenecker lived in a roughly built house beside the church, preaching and teaching a little school during the winter.",
        "blog_posts": [],
    },
]


def geocode_location(geolocator: Nominatim, query: str, retries: int = 3) -> Optional[Dict]:
    """
    Geocode a location with retry logic and error handling.

    Respects Nominatim's rate limit of 1 request per second.
    """
    for attempt in range(retries):
        try:
            # Rate limiting: 1 request per second
            time.sleep(1)

            location = geolocator.geocode(query, timeout=10)
            if location:
                return {
                    "lat": location.latitude,
                    "lon": location.longitude,
                    "display_name": location.address
                }
            else:
                print(f"  No results found for: {query}")
                return None

        except GeocoderTimedOut:
            if attempt == retries - 1:
                print(f"  Timeout after {retries} attempts: {query}")
                return None
            print(f"  Timeout, retrying... (attempt {attempt + 1})")

        except GeocoderServiceError as e:
            print(f"  Geocoder service error: {e}")
            return None

    return None


def create_geojson_feature(location_data: Dict, coords: Dict) -> Dict:
    """Create a GeoJSON Feature from location data and coordinates."""
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [coords["lon"], coords["lat"]]  # GeoJSON is [longitude, latitude]
        },
        "properties": {
            "name": location_data["name"],
            "type": location_data["type"],
            "family_members": location_data.get("family_members", []),
            "events": location_data.get("events", []),
            "date_range": location_data.get("date_range", ""),
            "description": location_data["description"],
            "blog_posts": location_data.get("blog_posts", []),
            "geocoded_address": coords.get("display_name", "")
        }
    }


def main():
    """Main function to geocode locations and generate GeoJSON file."""
    print("Hopper Family Kentucky Locations Geocoder")
    print("=" * 50)
    print(f"Total locations to process: {len(LOCATIONS)}\n")

    # Initialize geocoder
    geolocator = Nominatim(user_agent="ulsterworldly-hopper-map")

    # Process locations
    features = []
    failed_locations = []

    for i, loc in enumerate(LOCATIONS, 1):
        print(f"[{i}/{len(LOCATIONS)}] Geocoding: {loc['name']}")

        coords = None

        # Try geocoding
        if "fallback_coords" not in loc:
            coords = geocode_location(geolocator, loc["search_query"])
        else:
            print(f"  Using fallback coordinates")
            coords = loc["fallback_coords"]

        if coords:
            feature = create_geojson_feature(loc, coords)
            features.append(feature)
            print(f"  ✓ Success: {coords['lat']:.4f}, {coords['lon']:.4f}")
        else:
            failed_locations.append(loc["name"])
            print(f"  ✗ Failed to geocode")

    # Create GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "Hopper Family Kentucky Locations",
            "description": "Kentucky locations connected to the Hopper family Presbyterian heritage",
            "generated": time.strftime("%Y-%m-%d"),
            "total_locations": len(features)
        },
        "features": features
    }

    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / "static" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write GeoJSON file
    output_path = output_dir / "hopper-locations.geojson"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Successfully geocoded: {len(features)} locations")
    print(f"Failed to geocode: {len(failed_locations)} locations")

    if failed_locations:
        print("\nFailed locations:")
        for loc in failed_locations:
            print(f"  - {loc}")
        print("\nConsider adding fallback coordinates for failed locations.")

    print(f"\nGeoJSON file saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
