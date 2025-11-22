# api_endpoints.py
# API endpoints for the new game systems UI

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Optional
import json

# Import game manager
from game_manager import get_game_manager

router = APIRouter(prefix="/api")


@router.get("/portraits")
async def get_portraits():
    """Get all NPC portraits with relationship data"""
    try:
        game = get_game_manager()

        # Load NPC data
        npc_roster_path = Path("npc_roster.json")
        if not npc_roster_path.exists():
            npc_roster_path = Path("npc_data/npc_roster.json")

        if npc_roster_path.exists():
            with open(npc_roster_path, 'r') as f:
                npcs_data = json.load(f)
        else:
            return JSONResponse({"error": "NPC roster not found"}, status_code=404)

        # Enrich with relationship data
        portraits = []
        for npc_data in npcs_data:
            npc_name = npc_data.get("full_name", "Unknown")

            if npc_name == "Malcolm Newt":
                continue  # Skip player

            # Get relationship with player
            rel = game.relationships.get_relationship("Malcolm Newt", npc_name)

            portraits.append({
                "name": npc_name,
                "age": npc_data.get("age", 25),
                "occupation": npc_data.get("occupation", "Unknown"),
                "gender": npc_data.get("gender", "Unknown"),
                "portrait_url": f"/npc_portraits/{npc_name.replace(' ', '_')}.png",
                "friendship": rel.friendship_points,
                "romance": rel.romantic_points,
                "relationship_status": rel.status.name.replace('_', ' ').title(),
                "times_talked": rel.times_talked
            })

        # Sort by friendship level
        portraits.sort(key=lambda x: x["friendship"], reverse=True)

        return JSONResponse({"npcs": portraits})

    except Exception as e:
        return JSONResponse({"error": str(e), "npcs": []}, status_code=500)


@router.get("/town-map")
async def get_town_map():
    """Get town map with location data - dynamically discovers all locations"""
    try:
        game = get_game_manager()

        # Collect all locations with NPCs
        location_data = {}
        if game.sim:
            for npc in game.sim.npcs:
                loc = getattr(npc, 'current_location', 'Unknown')
                if loc not in location_data:
                    location_data[loc] = {
                        'npcs': [],
                        'count': 0
                    }
                location_data[loc]['npcs'].append(npc.full_name)
                location_data[loc]['count'] += 1

        # Categorize locations for better positioning
        def categorize_location(name):
            name_lower = name.lower()
            if 'house' in name_lower or 'home' in name_lower:
                return 'residential'
            elif any(word in name_lower for word in ['school', 'daycare', 'clinic', 'station', 'diner', 'store', 'library', 'bar', 'gym', 'coffee']):
                return 'public'
            elif 'rig' in name_lower or 'research' in name_lower:
                return 'work'
            return 'other'

        # Auto-generate positions in a grid layout by category
        locations = []
        residential = []
        public = []
        work = []
        other = []

        for loc_name, data in sorted(location_data.items()):
            category = categorize_location(loc_name)
            loc_obj = {
                "name": loc_name,
                "occupants": data['count'],
                "npc_names": data['npcs'][:10],  # Show up to 10 names
                "activities": [],
                "is_open": True,
                "type": category
            }

            if category == 'residential':
                residential.append(loc_obj)
            elif category == 'public':
                public.append(loc_obj)
            elif category == 'work':
                work.append(loc_obj)
            else:
                other.append(loc_obj)

        # Position public buildings first (top rows)
        x, y = 50, 50
        for i, loc in enumerate(public):
            loc['x'] = x
            loc['y'] = y
            x += 180
            if x > 900:
                x = 50
                y += 120
            locations.append(loc)

        # Position work locations (middle)
        y += 120
        x = 50
        for loc in work:
            loc['x'] = x
            loc['y'] = y
            x += 180
            if x > 900:
                x = 50
                y += 120
            locations.append(loc)

        # Position residential (bottom rows, compact grid)
        y += 120
        x = 50
        for i, loc in enumerate(residential):
            loc['x'] = x
            loc['y'] = y
            x += 120
            if x > 900:
                x = 50
                y += 80
            locations.append(loc)

        # Position other
        for loc in other:
            loc['x'] = x
            loc['y'] = y
            x += 180
            if x > 900:
                x = 50
                y += 120
            locations.append(loc)

        return JSONResponse({"locations": locations, "total": len(locations)})

    except Exception as e:
        import traceback
        print(f"[TownMap] Error: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e), "locations": []}, status_code=500)


@router.get("/statistics")
async def get_statistics():
    """Get player statistics"""
    try:
        game = get_game_manager()
        dashboard = game.get_player_dashboard("Malcolm Newt")

        # Format for frontend
        return JSONResponse({
            "money": dashboard["money"],
            "money_earned": 0,  # TODO: Track in statistics
            "money_spent": 0,   # TODO: Track in statistics
            "npcs_met": dashboard["npcs_met"],
            "conversations": dashboard["conversations"],
            "friends": dashboard["friends"],
            "dates": dashboard["dates"],
            "top_skills": [
                {"name": skill.title(), "level": level}
                for skill, level in dashboard["top_skills"]
            ],
            "recent_memories": dashboard["recent_memories"][:5],
            "inventory_items": dashboard["inventory_items"],
            "reputation": dashboard["reputation_score"]
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/relationships")
async def get_relationships():
    """Get all active relationships"""
    try:
        game = get_game_manager()
        dashboard = game.get_player_dashboard("Malcolm Newt")

        return JSONResponse({
            "relationships": dashboard["relationships"]
        })

    except Exception as e:
        return JSONResponse({"error": str(e), "relationships": []}, status_code=500)


@router.get("/npc/{npc_name}")
async def get_npc_details(npc_name: str):
    """Get detailed information about a specific NPC"""
    try:
        game = get_game_manager()
        npc_info = game.get_npc_info(npc_name, "Malcolm Newt")

        return JSONResponse(npc_info)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/action/talk/{npc_name}")
async def talk_to_npc(npc_name: str):
    """Player talks to an NPC"""
    try:
        game = get_game_manager()
        xp_gained = game.talk_to_npc("Malcolm Newt", npc_name)

        return JSONResponse({
            "success": True,
            "message": f"You talked with {npc_name}.",
            "xp_gained": xp_gained
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/action/flirt/{npc_name}")
async def flirt_with_npc(npc_name: str):
    """Player flirts with an NPC"""
    try:
        game = get_game_manager()
        success, message = game.flirt_with_npc("Malcolm Newt", npc_name)

        return JSONResponse({
            "success": success,
            "message": message
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/action/give-gift/{npc_name}/{item_id}")
async def give_gift(npc_name: str, item_id: str):
    """Give a gift to an NPC"""
    try:
        game = get_game_manager()
        success, message = game.give_gift("Malcolm Newt", npc_name, item_id)

        return JSONResponse({
            "success": success,
            "message": message
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.get("/inventory")
async def get_inventory():
    """Get player's inventory"""
    try:
        game = get_game_manager()
        inventory = game.inventory.get_inventory("Malcolm Newt")

        items = []
        for item_id, quantity in inventory.items.items():
            item = game.inventory.get_item(item_id)
            if item:
                items.append({
                    "id": item_id,
                    "name": item.name,
                    "description": item.description,
                    "quantity": quantity,
                    "category": item.category.value,
                    "value": item.value
                })

        return JSONResponse({
            "money": inventory.money,
            "items": items,
            "used_slots": inventory.used_slots,
            "max_slots": inventory.max_slots
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/skills")
async def get_skills():
    """Get player's skills"""
    try:
        game = get_game_manager()

        skills = []
        if "Malcolm Newt" in game.skills.character_skills:
            for skill_type, skill in game.skills.character_skills["Malcolm Newt"].items():
                skills.append({
                    "name": skill_type.value.title(),
                    "level": skill.level,
                    "experience": skill.experience,
                    "next_level_xp": skill.next_level_xp,
                    "progress": skill.progress_to_next
                })

        return JSONResponse({"skills": skills})

    except Exception as e:
        return JSONResponse({"error": str(e), "skills": []}, status_code=500)


@router.get("/events/upcoming")
async def get_upcoming_events():
    """Get upcoming social events"""
    try:
        game = get_game_manager()

        if game.sim:
            current_day = game.sim.time.total_days
            upcoming = game.social_events.get_upcoming_events(current_day, days_ahead=7)

            events = []
            for event in upcoming:
                events.append({
                    "name": event.name,
                    "type": event.event_type.value,
                    "day": event.day,
                    "hour": event.start_hour,
                    "duration": event.duration_hours,
                    "location": event.location,
                    "host": event.host,
                    "attendees": len(event.attendees),
                    "is_invited": event.is_invited("Malcolm Newt")
                })

            return JSONResponse({"events": events})

        return JSONResponse({"events": []})

    except Exception as e:
        return JSONResponse({"error": str(e), "events": []}, status_code=500)


@router.get("/gossip")
async def get_recent_gossip():
    """Get recent town gossip"""
    try:
        game = get_game_manager()

        gossip_list = []
        for gossip in game.reputation.active_gossip[-10:]:  # Last 10 gossips
            gossip_list.append({
                "type": gossip.gossip_type.value,
                "subject": gossip.subject,
                "content": gossip.content,
                "spread_count": gossip.spread_count,
                "juiciness": gossip.juiciness
            })

        return JSONResponse({"gossip": gossip_list})

    except Exception as e:
        return JSONResponse({"error": str(e), "gossip": []}, status_code=500)
