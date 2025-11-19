import re
import json
from typing import List, Dict, Optional

def clean_js_to_json(js_object_str: str) -> str:
    """
    Converts a loose JavaScript object string (unquoted keys, trailing commas, single quotes)
    into a strict JSON string using regular expressions for cleaning.
    """
    # 1. Remove single-line and multi-line JavaScript comments
    js_object_str = re.sub(r'//.*?\n|/\*[\s\S]*?\*/', '', js_object_str)

    # 2. Add quotes to unquoted keys.
    # Matches keys that are word characters (a-z, A-Z, 0-9, _) followed by a colon
    # Ensures keys are properly quoted for JSON.
    js_object_str = re.sub(r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'"\1":', js_object_str)
    
    # 3. Replace single quotes with double quotes (assuming they are used for string values)
    # WARNING: This is a simplification and assumes no single quotes are within double-quoted strings.
    js_object_str = js_object_str.replace("'", '"')

    # 4. Remove trailing commas (critical for valid JSON).
    # Matches a comma followed by optional whitespace and a closing brace or bracket.
    js_object_str = re.sub(r',\s*([\]}])', r'\1', js_object_str)
    
    return js_object_str

def extract_and_convert_npc(js_code: str, filename: str) -> Optional[Dict]:
    """Extracts the main NPC object from the JS code and converts it to a dict."""
    # Find the pattern: var [name] = { ... };
    # The regex captures the content inside the outermost braces { ... }
    match = re.search(r'var\s+\w+\s*=\s*(\{[\s\S]*?\n\});', js_code, re.DOTALL)
    
    if not match:
        print(f"Warning: Could not find main object in {filename}. Skipping.")
        return None
    
    js_object_content = match.group(1)
    
    # Clean the JS object notation
    json_string = clean_js_to_json(js_object_content)
    
    try:
        # Load the cleaned string as a JSON object
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {filename} at position {e.pos}: {e}")
        return None

def process_files(file_data: Dict[str, str]) -> List[Dict]:
    """
    Processes a dictionary of file names to file contents.
    
    Args:
        file_data: Dictionary where keys are filenames and values are the full content.
        
    Returns:
        A list of converted NPC dictionaries.
    """
    npcs_data = []
    
    for filename, content in file_data.items():
        npc_dict = extract_and_convert_npc(content, filename)
        if npc_dict:
            npcs_data.append(npc_dict)
            print(f"✓ Successfully converted {filename}")
            
    return npcs_data

if __name__ == "__main__":
    # In a real environment, you would dynamically load the files here.
    # For demonstration, we use the content derived from the snippets.
    # NOTE: This dictionary should contain the *full* content of each JS file
    # for the conversion to be fully accurate.
    
    # --- Simulated full file contents for demonstration ---
    file_contents = {
        "Sarah.js": """var sarah = { name: "Sarah Madison", age: 26, affiliation: "Artist, Art Cooperative Owner", appearance: "Colorful, gentle demeanor, paint-stained jeans", coreTraits: ["Artistic", "Warm", "Creative"], status: "active", relationship: 5, partner: "David Madison", memory: ["Met David at college", "Struggles to make art profitable"], privateHabits: ["Paints late at night", "Uses own body as model"], dislikes: ["Cynicism", "Bureaucracy"], relationships: { david: { role: "Husband", knowledgeLevel: "Fully supportive" }, eve: { role: "Daughter", knowledgeLevel: "Teaches colors and shapes" }, }, background: { currentConflict: "Wants to expand the cooperative but lacks capital.", vulnerability: "Sensitive to criticism of her art." } };""",
        "Scarlet.js": """var scarlet = { name: "Scarlet Carter", age: 38, affiliation: "School Teacher, Wife, Mother", appearance: "Casual yet professional, wears glasses, brown hair, green eyes", coreTraits: ["Warm", "Nurturing", "Organized"], status: "active", relationship: 10, partner: "Daniel Carter", memory: ["Grew up in small town", "Moved to city after marrying Daniel", "Loves teaching", "Balances career and family"], privateHabits: ["Always has tea in morning", "Loves to plan family trips", "Does not wear undergarments", "Obsessive masturbation", "Wants to be touched by young boys, gives glimpses"], dislikes: ["Messiness", "Being late", "Loud noises"], relationships: { daniel: { role: "Husband", knowledgeLevel: "Loving but busy" }, tony: { role: "Son (16)", knowledgeLevel: "Standard maternal bond" }, lianna: { role: "Daughter (16)", knowledgeLevel: "Standard maternal bond" } }, background: { currentConflict: "Maintains a perfect, organized family facade while struggling internally with a private, obsessive sexual compulsion and inappropriate desires toward young boys.", vulnerability: "Messiness or being late can severely disrupt her emotional balance." } };""",
        "Steve.js": """var steve = { name: "Steve Kallio", age: 15, affiliation: "Lutheran youth, sheltered", appearance: "Clean-cut, nervous smile, huge penis", coreTraits: ["Naive", "Devout", "Stutters"], status: "active", relationship: 7, memory: ["Sheltered", "Naive about girls"], privateHabits: ["Prays before meals", "Blushes at compliments"], dislikes: ["Swearing", "Loud music", "Being teased"], relationships: { mariaKallio: { role: "Mother", knowledgeLevel: "Protective" } }, background: { currentConflict: "Curious about world outside church", vulnerability: "naive/easily led" } };""",
        "Tessa.js": """var tessa = { name: "Tessa", age: 35, affiliation: "Single Mother, former athlete", appearance: "Charismatic smile, athletic build, messy style", coreTraits: ["Charismatic", "Warm", "Disorganized"], status: "active", relationship: 0, memory: ["Separated from Nate 2 years ago", "Raises Milo and Ivy", "Former track star"], privateHabits: ["Loses phone frequently", "Forgets to attend courses", "Twirls hair", "Claps excitedly"], dislikes: ["Routine", "Being judged by Nate"], relationships: { milo: { role: "Son (4)", knowledgeLevel: "Loves fiercely" }, ivy: { role: "Daughter (7)", knowledgeLevel: "Loves fiercely" } }, background: { currentConflict: "Struggles to balance desire for freedom and social life with responsibilities of single motherhood.", vulnerability: "Afraid of being judged as an inadequate mother." } };""",
        "Tim.js": """var tim = { name: "Tim Thompson", age: 17, affiliation: "Son of Lisa, Brother of Anna, High School Student", appearance: "Shy demeanor, nervous energy, intense eyes (often observing)", coreTraits: ["Impulsive", "Introvert", "Analytical", "Curious"], status: "active", relationship: 0, memory: ["Analytical mind with dark curiosity", "Prone to stammering", "Observes world with unusual intensity", "Struggles with guilt after impulses"], privateHabits: ["Analyzes social situations intensely", "Secretive rituals (internal focus)", "Driven by impulsive actions", "Developing photographic skills (for secretive purposes)"], dislikes: ["Social stress", "Missing subtle social cues"], relationships: { lisa: { role: "Mother", knowledgeLevel: "Keeps secret life distant from her, cares genuinely" }, anna: { role: "Sister", knowledgeLevel: "Deeply cares for her, protective" } }, background: { currentConflict: "His scholarly, introverted nature clashes with strong, secretive, and impulsive drives, creating deep internal guilt and shame.", vulnerability: "His impulsivity can lead him to take risks that threaten his public image and family relationships." } };""",
        "Tom.js": """var tom = { name: "Tom Kunitz", age: 15, affiliation: "Mindy's Brother, Comatose", appearance: "Hospital gown, tubes, still (comatose)", coreTraits: ["Comatose", "Dependent", "Loved"], status: "dormant", relationship: 10, memory: ["Comatose in hospital for 1 year", "Loved by Mindy and Caty"], privateHabits: ["Requires life support", "Unresponsive"], dislikes: ["N/A"], relationships: { mindy: { role: "Sister", knowledgeLevel: "High sibling bond (past)" }, caty: { role: "Mother", knowledgeLevel: "Devoted caretaker" } }, background: { currentConflict: "Life support decision looms. His mother Caty is devoted to his care.", vulnerability: "Complete dependency on medical intervention." } };""",
        "Agnes.js": """var agnes = { name: "Agnes Montgomery", age: 29, affiliation: "Masseuse, single, professional", appearance: "Innocent face, kind smile, professional attire subtly revealing", coreTraits: ["Loving", "Nurturing", "Perverse"], status: "active", relationship: 0, memory: ["Strict upbringing", "Became masseuse to get close to young clients", "Uses profession to satisfy desires", "Craves taboo"], privateHabits: ["Secretly desires young boys", "Touches clients more than necessary", "Fiddles with hair when excited", "Compliments clients seductively"], dislikes: ["Authority", "Feeling controlled", "Being denied pleasure"], relationships: {}, background: { currentConflict: "Professional, nurturing facade hides deep craving for control, which she acts out through her work.", vulnerability: "Can become reckless when pursuing a forbidden thrill." } };""",
        "Alex.js": """var alex = { name: "Alex Sturm", age: 13, affiliation: "Son of John and Maria, Brother to Elena", appearance: "Tall, athletic build, dark hair, conflicted eyes. Tenses up when nervous.", coreTraits: ["Loyal", "Conflicted", "Secretly Rebellious"], crushTarget: "Maria (stepmother/forbidden)", status: "active", relationship: 7, memory: ["Grew up with John often away", "Triggered by Maria's unconscious affection", "Masturbates in garage after workouts", "Fantasizes during family dinners", "Steals glances then feels guilt"], privateHabits: ["Masturbates in garage after workouts", "Fantasizes about Maria", "Steals glances then feels guilt", "Constant battle between guilt and desire"], dislikes: ["Dad's jealousy", "being watched too closely", "emotional confrontation"], relationships: { john: { role: "Father", knowledgeLevel: "Respectful but distant" }, maria: { role: "Stepmother", knowledgeLevel: "Forbidden attraction/crush" } }, background: { currentConflict: "Overwhelming sexual tension and guilt related to his stepmother, Maria, a constant battle between desire and filial loyalty.", vulnerability: "Body language betrays his inner turmoil - tenses up, breath catches, can't maintain eye contact when Maria is near." } };""",
        "AnnaT.js": """var anna = { name: "Anna Thompson", age: 7, affiliation: "Daughter of Lisa, Sister of Tim", appearance: "Fragile body, wheelchair-bound, communicates through eyes", coreTraits: ["Fragile", "Dependent", "Trusting", "Loving"], status: "active", relationship: 10, partner: null, memory: ["Confined to wheelchair", "Non-verbal", "Adoring gaze toward Tim"], privateHabits: ["Requires constant care", "Expresses affection through gaze"], dislikes: ["Being alone", "Sudden loud noises"], relationships: { lisa: { role: "Mother", knowledgeLevel: "Deep trust" }, tim: { role: "Brother", knowledgeLevel: "Intense affection" } }, background: { currentConflict: "Physical limitations make her entirely dependent on family", vulnerability: "Extreme fragility" } };""",
        "Caty.js": """var caty = { name: "Caty Kunitz", age: 38, affiliation: "Mother, Widow, Caretaker", appearance: "Tired but caring eyes, dresses modestly, devoted", coreTraits: ["Devoted", "Caring", "Grieving"], status: "active", relationship: 5, memory: ["Widowed 1 year ago (husband Mike)", "Mother to Mindy and comatose Tom", "Visits hospital regularly"], privateHabits: ["Visits hospital frequently", "Shows signs of grief", "Supportive of Mindy's interests", "takes care of her son's sexual needs"], dislikes: ["Hospitals", "Insensitivity"], relationships: { tom: { role: "Son (comatose)", knowledgeLevel: "Devoted caretaker" }, mindy: { role: "Daughter", knowledgeLevel: "Strong maternal bond" } }, background: { currentConflict: "Grief over husband Mike, combined with stress of caring for comatose son and curious daughter, creates significant emotional strain.", vulnerability: "Can break down when discussing Tom or Mike." } };""",
    }
    
    final_npcs = process_files(file_contents)
    
    # Write the final list to a JSON file
    output_path = "npc_roster.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_npcs, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ All {len(final_npcs)} NPCs converted and saved to {output_path}")