# map_generator.py
"""
Willow Creek Town Map Generator

Creates a visual map of Willow Creek showing all locations organized by streets/districts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Tuple
import os

# Town layout - organized by districts and streets
TOWN_LAYOUT = {
    # Downtown / Main Street District
    "Main Street": {
        "color": "#8b4513",
        "locations": [
            ("Main Street Diner", (2, 8)),
            ("Willow Creek Bar & Grill", (3, 8)),
            ("Willow Creek Police Station", (2.5, 7)),
            ("Willow Creek Grocery", (4, 8)),
            ("Main Street Shops", (3.5, 7)),
        ]
    },

    # Residential / Maple Street
    "Maple Street": {
        "color": "#228b22",
        "locations": [
            ("Willow Creek Daycare Center", (1, 5)),
            ("Namaste Yoga Studio", (2, 5)),
            ("Voss Massage Studio", (2.5, 5)),
            ("Maple Street Fire Department", (3, 5)),
        ]
    },

    # Healthcare / Magnolia District
    "Magnolia District": {
        "color": "#ff69b4",
        "locations": [
            ("Willow Creek Clinic", (7, 6)),
            ("Magnolia Mental Health Center", (7.5, 6)),
        ]
    },

    # Education District
    "Education District": {
        "color": "#4169e1",
        "locations": [
            ("Willow Creek High School", (5, 3)),
            ("Willow Creek Pre-School", (6, 3)),
        ]
    },

    # Civic District
    "Civic District": {
        "color": "#daa520",
        "locations": [
            ("Willow Creek Town Hall", (1.5, 9)),
            ("Willow Creek Public Library", (0.5, 7)),
            ("Sycamore Post Office", (1, 6)),
        ]
    },

    # Industrial District
    "Industrial District": {
        "color": "#696969",
        "locations": [
            ("Blake's Auto Repair", (8, 2)),
            ("Hanson Auto Shop", (8.5, 2)),
            ("County Roads Depot", (9, 2)),
            ("Thompson Carpentry", (8, 1.5)),
        ]
    },

    # Recreation District
    "Recreation": {
        "color": "#32cd32",
        "locations": [
            ("Willow Creek Park", (4.5, 5)),
            ("Maple Lanes Bowling Alley", (7, 2)),
        ]
    },

    # Shopping Complex
    "Mall Complex": {
        "color": "#ff6347",
        "locations": [
            ("Willow Creek Mall", (9, 6)),
            ("Mall - Food Court", (9.2, 6.3)),
            ("Mall - Arcade", (9.5, 6)),
        ]
    },

    # Religious
    "Religious": {
        "color": "#9370db",
        "locations": [
            ("Willow Creek Lutheran Church", (6, 8)),
            ("Oak Street Church", (6.5, 8)),
        ]
    },

    # Specialized / Outskirts
    "Outskirts": {
        "color": "#2f4f4f",
        "locations": [
            ("Willow Creek Naval Base", (1, 1)),
            ("Offshore Oil Rig", (0, 0)),
            ("Engineering Firm", (8, 7)),
            ("Art Cooperative", (5, 9)),
        ]
    },

    # Residential Areas (Houses)
    "Residential": {
        "color": "#dda0dd",
        "locations": [
            ("Blake House", (3, 3)),
            ("Carter House", (3.5, 3)),
            ("Madison House", (4, 3.5)),
            ("Sturm House", (4.5, 3)),
            ("Thompson House", (5, 4)),
        ]
    }
}


def generate_town_map(output_path: str = "willow_creek_map.png", show_plot: bool = False):
    """
    Generate a visual map of Willow Creek and save it as an image.

    Args:
        output_path: Where to save the map image
        show_plot: Whether to display the plot interactively
    """
    fig, ax = plt.subplots(figsize=(16, 12))
    fig.patch.set_facecolor('#1a1410')
    ax.set_facecolor('#0f0c09')

    # Set up the plot
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10.5)
    ax.set_aspect('equal')

    # Title
    ax.set_title('Willow Creek Town Map',
                 fontsize=24,
                 fontweight='bold',
                 color='#d4af37',
                 pad=20)

    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Add grid lines for streets
    for i in range(11):
        ax.axhline(i, color='#3a3a3a', linewidth=0.5, alpha=0.5)
        ax.axvline(i, color='#3a3a3a', linewidth=0.5, alpha=0.5)

    # Plot each district
    legend_elements = []

    for district_name, district_data in TOWN_LAYOUT.items():
        color = district_data["color"]
        locations = district_data["locations"]

        for loc_name, (x, y) in locations:
            # Draw location marker
            circle = patches.Circle((x, y), 0.15,
                                   facecolor=color,
                                   edgecolor='#d4af37',
                                   linewidth=2,
                                   alpha=0.8)
            ax.add_patch(circle)

            # Add location label
            ax.text(x, y - 0.35, loc_name,
                   fontsize=7,
                   ha='center',
                   va='top',
                   color='#f5e6d3',
                   bbox=dict(boxstyle='round,pad=0.3',
                            facecolor='#1a1410',
                            edgecolor=color,
                            alpha=0.9))

        # Add to legend
        legend_elements.append(patches.Patch(facecolor=color,
                                             edgecolor='#d4af37',
                                             label=district_name))

    # Add legend
    ax.legend(handles=legend_elements,
             loc='upper right',
             fontsize=9,
             facecolor='#1a1410',
             edgecolor='#d4af37',
             framealpha=0.95,
             labelcolor='#f5e6d3')

    # Add compass rose
    compass_x, compass_y = 0.2, 9.5
    ax.annotate('N', xy=(compass_x, compass_y + 0.3),
               fontsize=14, ha='center', color='#d4af37', fontweight='bold')
    ax.arrow(compass_x, compass_y, 0, 0.2,
            head_width=0.1, head_length=0.1,
            fc='#d4af37', ec='#d4af37')

    # Add street labels
    street_labels = [
        ("Main St", 2.5, 9.8),
        ("Maple St", 2, 5.5),
        ("Industrial Rd", 8.5, 1.2),
        ("School Ln", 5.5, 2.5),
    ]

    for label, x, y in street_labels:
        ax.text(x, y, label,
               fontsize=10,
               fontweight='bold',
               color='#8b6914',
               bbox=dict(boxstyle='round,pad=0.4',
                        facecolor='#0f0c09',
                        edgecolor='#8b6914',
                        alpha=0.8))

    plt.tight_layout()

    # Save the map
    plt.savefig(output_path,
                dpi=300,
                bbox_inches='tight',
                facecolor='#1a1410')

    print(f"✅ Map saved to: {output_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()

    return output_path


def print_text_map():
    """Print a simple text-based map to console."""
    print("\n" + "=" * 60)
    print("WILLOW CREEK - LOCATION INDEX".center(60))
    print("=" * 60 + "\n")

    for district_name, district_data in TOWN_LAYOUT.items():
        print(f"\n📍 {district_name.upper()}")
        print("-" * 40)
        for loc_name, (x, y) in district_data["locations"]:
            print(f"   • {loc_name}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # Generate the map
    generate_town_map(show_plot=False)

    # Also print text version
    print_text_map()
