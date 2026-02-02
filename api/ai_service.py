import requests
import json
import os
import re
from dotenv import load_dotenv

# Load env in service as well to be safe, though settings loads it
load_dotenv()

# DEEPSEEK_API_KEY = "sk-7cc5ef44d8b4414ab24e6f9e13e82182" 
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def call_deepseek(system_prompt, user_prompt):
    print(f"--- Calling DeepSeek API ---")
    print(f"Key present: {bool(DEEPSEEK_API_KEY)}")
    
    if not DEEPSEEK_API_KEY:
        print("ERROR: No API Key found.")
        return None
        
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Force pure JSON mode in prompt if model doesn't support json_object
    system_prompt += "\n\nIMPORTANT: Return ONLY valid JSON."

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {
            "type": "text" # Change to text to avoid compatibility issues, we will parse json manually
        },
        "stream": False
    }
    
    try:
        print("Sending request...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        
        if response.status_code != 200:
            print(f"API Error Status: {response.status_code}")
            print(f"API Error Body: {response.text}")
            return None
            
        result = response.json()
        content = result['choices'][0]['message']['content']
        print("API Success! Content length:", len(content))
        
        # Clean markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        content = content.strip()
        
        # Basic cleanup for common AI JSON issues (like trailing commas)
        # This is a very basic regex and might not catch everything, but it's a start
        content = re.sub(r',\s*([\]}])', r'\1', content)
            
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If still failing, try to find the first { and last }
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]
                return json.loads(content)
            raise
    except Exception as e:
        print(f"DeepSeek API Exception: {e}")
        return None

def extract_course_structure(syllabus_text, thinking_type):
    """
    Extracts nodes (concepts) and edges (relationships) from syllabus based on specific pedagogical models.
    thinking_type: 'divergent' (Graph/Map) or 'convergent' (Tree/Logic)
    """
    
    if thinking_type == 'convergent':
        # 模式一：树形思维（逻辑型）- Tree Mode
        system_prompt = """
        You are a senior curriculum designer and logic analysis expert. Your task is to build a deep pedagogical logic tree based on the provided course syllabus.
        
        ## Core Objective
        Construct a "Linear Decomposition · Hierarchical Progression · Causal Connection" course logic system, clarifying the pre-requisite and post-requisite dependencies of knowledge.
        
        ## Output Format (JSON)
        {
            "nodes": [
                {
                    "id": 1, 
                    "label": "Node Name (Knowledge Point)", 
                    "shape": "box" (Main Branch) or "ellipse" (Sub-node), 
                    "color": "#HEXCODE",
                    "level": 0 (Root), 1 (Main Branch), 2 (Sub-node)...,
                    "title": "HTML Tooltip: Pre-requisite -> Application logic, and weight"
                }
            ],
            "edges": [
                {
                    "from": 1, 
                    "to": 2, 
                    "arrows": "to",
                    "color": {"color": "#HEXCODE"},
                    "label": "Relation Type (Strong/Weak)"
                }
            ],
            "concepts": ["List of core concepts"]
        }
        
        ## Detailed Requirements
        1. **Root Node**: Course Total Objective (Level 0, Color #FFD54F).
        2. **Main Branches**: Core modules divided by week/chapter (Level 1, Color #FFCC80).
        3. **Sub-nodes**: Specific knowledge points, arranged in "Basic -> Advanced -> Application" hierarchy (Level 2+, Color #FFE0B2).
        4. **Connection Logic**:
           - **Strict Hierarchy**: Edges must go from parent to child (Level N -> Level N+1).
           - **Strong Connection (Red Edge #EF5350)**: Must master; pre-requisite directly supports subsequent content.
           - **Weak Connection (Blue Edge #42A5F5)**: Good to know; auxiliary knowledge.
        5. **Coverage**: Must cover 100% of core knowledge points in the syllabus, no omissions.
        6. **Tooltip**: Briefly explain the impact weight of the knowledge point on subsequent learning in the node title (e.g., Weight 90%).
        """
    else:
        # 模式二：发散性（图型思维）- Graph Mode
        system_prompt = """
        You are an interdisciplinary knowledge integration expert. Your task is to build a full-domain course knowledge graph based on the provided course syllabus.
        
        ## Core Objective
        Construct a "Mesh Association · Multi-dimensional Radiation · Scenario Landing" knowledge network, breaking linear boundaries and emphasizing cross-module intersection and application.
        
        ## Output Format (JSON)
        {
            "nodes": [
                {
                    "id": 1, 
                    "label": "Node Name", 
                    "shape": "circle" (Basic) / "box" (Method) / "diamond" (Application) / "star" (Extension), 
                    "color": "#HEXCODE",
                    "title": "HTML Tooltip: Connection strength, functional positioning, and scenario application"
                }
            ],
            "edges": [
                {
                    "from": 1, 
                    "to": 2, 
                    "label": "★★★★★ (Strength)",
                    "color": {"color": "#HEXCODE"},
                    "dashes": false
                }
            ],
            "concepts": ["List of core concepts"]
        }
        
        ## Detailed Requirements
        1. **Core Anchor**: Course Core Literacy Goal (Center, Color #FFD54F).
        2. **Node Classification**:
           - Basic Concept (Circle, #FFF176)
           - Method/Technique (Box, #81D4FA)
           - Application Practice (Diamond, #A5D6A7)
           - Extension (Star, #CE93D8)
        3. **Link Logic**:
           - **Direct Application (Red Edge #EF5350)**: A directly solves B's problem.
           - **Similar Transfer (Blue Edge #29B6F6)**: A and B have similar logic, transferable.
           - **Cross-module Intersection (Green Edge #66BB6A)**: Module 1 combined with Module 2.
           - **Scenario Landing (Yellow Edge #FBC02D)**: Knowledge point -> Specific case/practice.
        4. **Coverage**: 100% cover knowledge points in the syllabus.
        5. **Structure**: Non-hierarchical, mesh network. Allow cross-connections between any nodes.
        """
    
    user_prompt = f"Please analyze the following syllabus content and strictly generate structured data according to the above model requirements:\n\n{syllabus_text[:20000]}" 
    
    return call_deepseek(system_prompt, user_prompt)

def generate_smart_tasks(course_name, nodes, count):
    """
    Generates study tasks based on the extracted nodes.
    """
    system_prompt = """
    You are a study planner. Generate specific, actionable study tasks based on the provided course concepts.
    
    Output Format: JSON
    {{
        "tasks": [
            "Task description 1",
            "Task description 2"
        ]
    }}
    """
    
    concepts_str = ", ".join([n['label'] for n in nodes[:10]]) # Use top 10 nodes context
    user_prompt = f"Course: {course_name}. Key Concepts: {concepts_str}. Generate {count} tasks that guide the student through these concepts logically."
    
    return call_deepseek(system_prompt, user_prompt)

def find_cross_connections(current_course_name, current_concepts, other_courses_data):
    """
    Finds connections between the current course and previous courses.
    other_courses_data: list of dicts {'name': 'Course B', 'concepts': ['c1', 'c2']}
    """
    if not other_courses_data:
        return []
        
    system_prompt = """
    You are a knowledge integration expert. Find semantic connections between the current course and previous courses.
    
    Output Format: JSON
    {{
        "cross_links": [
            {{"from_concept": "Concept in Current Course", "to_course": "Previous Course Name", "to_concept": "Concept in Previous Course", "reason": "Explanation"}}
        ]
    }}
    """
    
    others_str = json.dumps(other_courses_data)
    user_prompt = f"Current Course: {current_course_name}. Concepts: {current_concepts}. Previous Courses: {others_str}. Find relevant cross-course connections."
    
    result = call_deepseek(system_prompt, user_prompt)
    if result:
        return result.get('cross_links', [])
    return []
