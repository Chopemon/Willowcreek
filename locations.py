# core/locations.py

WILLOW_CREEK_LOCATIONS = {
    "hospital": {
        "name": "Willow Creek Hospital",
        "address": "1 Willow Creek Dr",
        "type": "Healthcare",
        "hours": "24/7",
        "services": ["Emergency Care", "Surgery", "Inpatient Care"],
        "description": "Small regional hospital serving Willow Creek and nearby towns."
    },
    "clinic": {
        "name": "Willow Creek Clinic",
        "address": "14 Magnolia Rd",
        "type": "Healthcare",
        "hours": "Mon–Fri 9 AM – 5 PM",
        "services": ["Family Medicine", "Checkups", "Minor Injuries"],
        "description": "Local clinic for non-emergency health issues."
    },
    "daycare": {
        "name": "Willow Creek Daycare Center",
        "address": "25 Maple St",
        "type": "Childcare",
        "hours": "Mon–Fri 7 AM – 6 PM",
        "services": ["Infants", "Toddlers", "Preschool Programs"],
        "description": "Daycare center for children aged 3–6, offering early childhood education."
    },
    
    "preschool": {
        "name": "Willow Creek Pre-School",
        "address": "30 Birch Rd",
        "type": "Education",
        "hours": "Mon–Fri 8 AM – 2 PM",
        "services": ["Pre-Kindergarten", "Early Education", "Play-based Learning"],
        "description": "Pre-school for kids aged 3–6, focusing on basic education and social skills."
    },

    "psychiatry": {
        "name": "Magnolia Mental Health Center",
        "address": "16 Magnolia Rd",
        "type": "Healthcare",
        "hours": "Mon–Fri 10 AM – 6 PM",
        "services": ["Therapy", "Psychiatry", "Counseling"],
        "description": "Discreet psychiatric practice serving the community."
    },
    "diner": {
        "name": "Main Street Diner",
        "address": "101 Main St",
        "type": "Restaurant",
        "hours": "Every day 7 AM – 10 PM",
        "services": ["Breakfast", "Lunch", "Coffee", "Pie"],
        "description": "Classic small-town diner where everyone eventually shows up."
    },
    "bar": {
        "name": "Willow Creek Bar & Grill",
        "address": "115 Main St",
        "type": "Bar & Restaurant",
        "hours": "Mon–Thu 4 PM – 11 PM, Fri–Sat 4 PM – 1 AM",
        "services": ["Drinks", "Burgers", "Karaoke Nights"],
        "description": "After-work hangout and late-night gossip hub."
    },
    "highSchool": {
        "name": "Willow Creek High School",
        "address": "400 School Ln",
        "type": "Education",
        "hours": "Mon–Fri 8 AM – 3 PM",
        "services": ["Grades 7–12", "Sports", "Clubs"],
        "description": "The only secondary school in town, where most teens intersect."
    },
    "church": {
        "name": "Willow Creek Lutheran Church",
        "address": "32 Chapel Rd",
        "type": "Religious",
        "hours": "Sun services 9 AM & 11 AM, Wed evening prayer",
        "services": ["Services", "Youth Group", "Community Events"],
        "description": "Traditional Lutheran church at the moral center of town life."
    },
    "park": {
        "name": "Willow Creek Park",
        "address": "2 Parkview Dr",
        "type": "Public",
        "hours": "Dawn to dusk",
        "features": ["Playground", "Walking Trails", "Pond", "Picnic Tables"],
        "description": "Green heart of town; kids, dog walkers, and loners all pass through here."
    },
    "yogaStudio": {
        "name": "Namaste Yoga Studio",
        "address": "207 Maple St",
        "type": "Wellness",
        "hours": "Class-based schedule",
        "services": ["Yoga Classes", "Workshops"],
        "description": "Small studio offering group classes and private sessions."
    },
    "massageStudio": {
        "name": "Voss Massage Studio",
        "address": "209 Maple St",
        "type": "Wellness",
        "hours": "By appointment",
        "services": ["Massage Therapy", "Sports Massage"],
        "description": "Discrete studio on Maple with a complicated reputation."
    },
    "autoShop": {
        "name": "Blake's Auto Repair",
        "address": "35 Industrial Rd",
        "type": "Service",
        "hours": "Mon–Sat 8 AM – 6 PM",
        "services": ["Car Repair", "Maintenance"],
        "description": "Local garage run by the Blake family; grease, tools, and quiet conversations."
    },
    "policeStation": {
        "name": "Willow Creek Police Station",
        "address": "75 Main St",
        "type": "Law Enforcement",
        "hours": "24/7",
        "services": ["Patrol", "Investigations"],
        "description": "Small station where everyone knows the officers by name."
    },
    "townHall": {
        "name": "Willow Creek Town Hall",
        "address": "10 Civic Plaza",
        "type": "Government",
        "hours": "Mon–Fri 9 AM – 4 PM",
        "services": ["Permits", "Records", "Council Meetings"],
        "description": "Bureaucratic center of the town and home of endless low-level drama."
    },
    "postOffice": {
        "name": "Sycamore Post Office",
        "address": "12 Sycamore Ln",
        "type": "Service",
        "hours": "Mon–Fri 8 AM – 5 PM, Sat 9 AM – 1 PM",
        "services": ["Mail", "Packages", "P.O. Boxes"],
        "description": "Mail hub and informal bulletin board for the whole town."
    },
    "fireStation": {
        "name": "Maple Street Fire Department",
        "address": "50 Maple St",
        "type": "Emergency Services",
        "hours": "24/7",
        "services": ["Fire", "Rescue"],
        "description": "Volunteer fire department with deep roots in the community."
    },
    "grocery": {
        "name": "Willow Creek Grocery",
        "address": "130 Main St",
        "type": "Retail",
        "hours": "Every day 8 AM – 10 PM",
        "services": ["Groceries", "Household Goods"],
        "description": "Small but busy grocery store where everyone eventually bumps into an ex."
    },
    "library": {
        "name": "Willow Creek Public Library",
        "address": "5 Library Ln",
        "type": "Education",
        "hours": "Mon–Sat 9 AM – 7 PM",
        "services": ["Books", "Study Space", "Public Computers"],
        "description": "Quiet refuge filled with stories and the rustle of old paper."
    },
    "mainStreetShops": {
        "name": "Main Street Shops",
        "address": "100–150 Main St",
        "type": "Retail",
        "hours": "Most shops 10 AM – 6 PM",
        "services": ["Small Boutiques", "Pharmacy", "Barber", "Antique Store"],
        "description": "Cluster of small independent shops along Main Street."
    },
    "bowlingAlley": {
        "name": "Maple Lanes Bowling Alley",
        "address": "22 Industrial Rd",
        "type": "Leisure",
        "hours": "Mon–Thu 3 PM – 11 PM, Fri–Sun 12 PM – 1 AM",
        "features": ["Lanes", "Arcade Corner", "Snack Bar", "Bar Area"],
        "description": "Old-school bowling alley with league nights, family outings, and cosmic bowling."
    },
    "mall": {
        "name": "Willow Creek Mall",
        "address": "300 Mall Rd",
        "type": "Retail Complex",
        "hours": "Mon–Sat 10 AM – 9 PM, Sun 11 AM – 6 PM",
        "services": ["Retail", "Food Court", "Arcade"],
        "description": "A slightly aging mall where teens loiter and adults pretend they are just running errands."
    },
    "arcade": {
        "name": "Galaxy Arcade",
        "address": "Inside Willow Creek Mall",
        "type": "Entertainment",
        "hours": "Mall Hours",
        "features": ["Arcade Machines", "Prize Counter"],
        "description": "Flashing lights, sticky floors, and the smell of popcorn—teen territory."
    },
    "foodCourt": {
        "name": "Willow Creek Mall Food Court",
        "address": "Inside Willow Creek Mall",
        "type": "Food Court",
        "hours": "Mall Hours",
        "services": ["Burger Barn", "Pho Express", "Pretzel King", "Bubble Tea"],
        "description": "Central gathering area of the mall, full of cheap food and overheard conversations."
    },
    "bowlingSnackBar": {
        "name": "Maple Lanes Snack Bar",
        "address": "Inside Maple Lanes Bowling Alley",
        "type": "Food",
        "hours": "Bowling Hours",
        "services": ["Burgers", "Fries", "Nachos", "Sodas"],
        "description": "Greasy comfort food fueling league nights and teen hangouts."
    },
    "militaryBase": {
        "name": "Willow Creek Military Outpost",
        "address": "County Rd 12",
        "type": "Military",
        "hours": "Restricted",
        "services": ["Training", "Operations"],
        "description": "Small military installation on the edge of town."
    },
    "sealBase": {
        "name": "Lakeside Research & Seal Station",
        "address": "Shoreline Rd",
        "type": "Research",
        "hours": "Restricted / Appointment Only",
        "services": ["Marine Research"],
        "description": "Research facility near the lake, mostly off-limits to the public."
    },
    "oilRig": {
        "name": "Offshore Oil Rig #7",
        "address": "25 miles offshore",
        "type": "Industrial",
        "hours": "24/7 (2 weeks on, 2 weeks off shifts)",
        "services": ["Oil Extraction", "Rig Operations"],
        "description": "Deep-water oil drilling platform where workers spend weeks at a time away from home."
    },
    "blackEmber": {
        "name": "Black Ember",
        "address": "17 Underground Alley",
        "type": "Tattoo Studio",
        "hours": "Tue–Sat 2 PM – 11 PM, by appointment after hours",
        "services": ["Custom Tattoos", "Cover-ups", "Piercings", "Tattoo Consultations"],
        "description": "Small underground tattoo studio with dark atmosphere and intimate vibe. Co-owned by Selene Arvidsson and Markus. Known for raven and geometric designs, attracts musicians, artists, and those seeking edgy body art. Late-night sessions blur lines between professional and personal."
    }
}

# Convenience lookups
LOCATIONS_BY_KEY = WILLOW_CREEK_LOCATIONS
LOCATIONS_BY_NAME = {data["name"]: key for key, data in WILLOW_CREEK_LOCATIONS.items()}
