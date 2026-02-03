import requests
import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

import urllib3
urllib3.disable_warnings()

# Load env in service as well to be safe, though settings loads it
load_dotenv()

# API Keys and Endpoints
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
DOUBAO_ENDPOINT_ID = os.environ.get("DOUBAO_ENDPOINT_ID", "doubao-seed-1-6-flash-250828")

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def refine_syllabus_with_doubao(raw_text):
    """
    Uses Doubao (Ark) Agent to refine raw syllabus text into a clean, structured Markdown.
    """
    print(f"--- Calling Doubao Refiner Agent ---")
    if not ARK_API_KEY:
        print("ERROR: No Ark API Key found. Skipping refinement.")
        return raw_text

    try:
        client = OpenAI(
            api_key=ARK_API_KEY,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )

        system_prompt = """
        You are a Curriculum Data Specialist. Your task is to "dehydrate" and "structure" a messy course syllabus.
        
        ## Input
        Raw text from PDF/PPT/Word which may contain layout noise, page numbers, and redundant info.
        
        ## Output Requirements (Markdown Only)
        1. # Course Meta: (Course Name)
        2. # Weekly Schedule: (A Table with columns: Week/Lesson | Topic)
        3. # Assessment Plan: (List of Assignments, Quizzes, Exams with Week # and Weights)
        
        ## Rules
        - Remove ALL noise (copyright, disclaimers, etc.).
        - If the input is empty or junk, return "No valid content found".
        - Be concise but cover 100% of the teaching plan.
        - Ensure dates/weeks are accurate.
        - Only give the output mentioned above 
        """

        completion = client.chat.completions.create(
            model=DOUBAO_ENDPOINT_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please refine this syllabus content:\n\n{raw_text[:30000]}"}
            ],
        )

        refined_content = completion.choices[0].message.content
        print(f"Refinement Success! Length: {len(refined_content)}")
        return refined_content
    except Exception as e:
        print(f"Doubao Refinement Exception: {e}")
        return raw_text

def call_doubao(system_prompt, user_prompt):
    """
    Unified caller for Doubao (Ark) API to replace DeepSeek.
    """
    print(f"--- Calling Doubao API (Replacement for DeepSeek) ---")
    load_dotenv()
    ark_key = os.environ.get("ARK_API_KEY", "")
    # Using a slightly more powerful model for main analysis if possible, 
    # but defaulting to the flash model provided by user
    endpoint_id = os.environ.get("DOUBAO_ENDPOINT_ID", "doubao-seed-1-6-flash-250828")

    if not ark_key:
        print("ERROR: No Ark API Key found.")
        return None

    try:
        client = OpenAI(
            api_key=ark_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )
        
        # Doubao also benefits from JSON instruction
        system_prompt += "\n\nIMPORTANT: Return ONLY valid JSON."

        completion = client.chat.completions.create(
            model=endpoint_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # Doubao supports response_format in newer versions, 
            # but we use our manual parsing logic for safety
        )

        content = completion.choices[0].message.content
        print(f"Doubao Success! Raw content preview: {content[:100]}...")

        # --- Manual JSON Parsing (Enhanced for Doubao) ---
        # 1. Strip potential Markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        content = content.strip()

        # 2. FIX: Remove invalid control characters (like \n, \t inside strings that aren't escaped)
        # This is likely causing the "Invalid control character" error
        content = re.sub(r'[\x00-\x1F\x7F]', '', content)
        
        # 3. Basic cleanup for trailing commas
        content = re.sub(r',\s*([\]}])', r'\1', content)
            
        try:
            parsed_json = json.loads(content)
            print("JSON Parsing Successful.")
            return parsed_json
        except json.JSONDecodeError as je:
            print(f"JSON Parsing Failed: {je}")
            # Try a second-pass recovery by finding the first { and last }
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content_recovered = content[start:end+1]
                try:
                    parsed_json = json.loads(content_recovered)
                    print("JSON Parsing Successful after extraction.")
                    return parsed_json
                except:
                    print("JSON Parsing still failed after extraction.")
            print(f"Full problematic content: {content}")
            raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Doubao API Exception: {e}")
        return None

# --- DeepSeek API Commented Out ---
# def call_deepseek(system_prompt, user_prompt):
#     print(f"--- Calling DeepSeek API ---")
#     print(f"Key present: {bool(DEEPSEEK_API_KEY)}")
#     
#     if not DEEPSEEK_API_KEY:
#         print("ERROR: No API Key found.")
#         return None
#         
#     headers = {
#         "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     
#     # Force pure JSON mode in prompt if model doesn't support json_object
#     system_prompt += "\n\nIMPORTANT: Return ONLY valid JSON."
# 
#     data = {
#         "model": "deepseek-reasoner",
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ],
#         "response_format": {
#             "type": "text" # Change to text to avoid compatibility issues, we will parse json manually
#         },
#         "stream": False
#     }
#     
#     try:
#         print("Sending request...")
#         # verify=False is needed for some Mac environments with SSL issues
#         # Increased timeout to 120s for larger files like PPTX
#         response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=120, verify=False)
#         
#         if response.status_code != 200:
#             print(f"API Error Status: {response.status_code}")
#             print(f"API Error Body: {response.text}")
#             return None
#             
#         result = response.json()
#         content = result['choices'][0]['message']['content']
#         print(f"API Success! Raw content preview: {content[:100]}...")
#         
#         # Clean markdown code blocks if present
#         if "```json" in content:
#             content = content.split("```json")[1].split("```")[0]
#         elif "```" in content:
#             content = content.split("```")[1].split("```")[0]
#         
#         content = content.strip()
#         
#         # Basic cleanup for common AI JSON issues (like trailing commas)
#         content = re.sub(r',\s*([\]}])', r'\1', content)
#             
#         try:
#             parsed_json = json.loads(content)
#             print("JSON Parsing Successful.")
#             return parsed_json
#         except json.JSONDecodeError as je:
#             print(f"JSON Parsing Failed: {je}")
#             # If still failing, try to find the first { and last }
#             start = content.find('{')
#             end = content.rfind('}')
#             if start != -1 and end != -1:
#                 content = content[start:end+1]
#                 try:
#                     parsed_json = json.loads(content)
#                     print("JSON Parsing Successful after extraction.")
#                     return parsed_json
#                 except:
#                     print("JSON Parsing still failed after extraction.")
#             
#             print(f"Full problematic content: {content}")
#             raise
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         print(f"DeepSeek API Exception: {e}")
#         return None


def extract_course_structure(syllabus_text, thinking_type):
    """
    Extracts nodes (concepts) and edges (relationships) from syllabus based on specific pedagogical models.
    thinking_type: 'divergent' (Graph/Map) or 'convergent' (Tree/Logic)
    """
    
    if thinking_type == 'convergent':
        # 模式一：树形思维（逻辑型）- Tree Mode
        system_prompt = """
        You are a senior curriculum designer and logic analysis expert. Your task is to build a deep pedagogical logic tree.
        
        ## Input Data Source
        You will receive a REFINED Markdown syllabus provided by a pre-processing Agent. This data is already cleaned and structured.
        
        ## Core Objective
        Construct a "Linear Decomposition · Hierarchical Progression · Causal Connection" course logic system, clarifying the pre-requisite and post-requisite dependencies of knowledge.
        
        ## Output Format (JSON)
        {
            "nodes": [
                {
                    "id": "unique_id", 
                    "label": "Node Name", 
                    "shape": "box" (Main Branch) or "ellipse" (Sub-node), 
                    "color": "#HEXCODE",
                    "level": 0 (Root), 1 (Main Branch), 2 (Sub-node)...,
                    "title": "HTML Tooltip: Explain WHY this follows previous node and its importance weight"
                }
            ],
            "edges": [
                {
                    "from": "id1", 
                    "to": "id2", 
                    "arrows": "to",
                    "color": {"color": "#HEXCODE"},
                    "label": "Strong/Weak"
                }
            ],
            "concepts": ["List of core concepts extracted"]
        }
        
        ## Detailed Requirements
        1. **Root Node**: Course Total Objective (Level 0, Color #FFD54F).
        2. **Main Branches**: Core modules/weeks (Level 1, Color #FFCC80).
        3. **Sub-nodes**: Specific knowledge points (Level 2+, Color #FFE0B2).
        4. **Connection Logic**:
           - **Strict Hierarchy**: Edges must go from parent to child or sequentially between weeks.
           - **Strong Connection (Red Edge #EF5350)**: Pre-requisite directly supports subsequent content.
           - **Weak Connection (Blue Edge #42A5F5)**: Auxiliary/Supportive.
        5. **Coverage**: 100% cover the provided refined syllabus.
        """
    else:
        # 模式二：发散性（图型思维）- Graph Mode
        system_prompt = """
        You are an interdisciplinary knowledge integration expert. Your task is to build a full-domain course knowledge graph.
        
        ## Input Data Source
        You will receive a REFINED Markdown syllabus provided by a pre-processing Agent.
        
        ## Core Objective
        Construct a "Mesh Association · Multi-dimensional Radiation · Scenario Landing" knowledge network, breaking linear boundaries and emphasizing cross-module intersection and application.
        
        ## Output Format (JSON)
        {
            "nodes": [
                {
                    "id": "unique_id", 
                    "label": "Node Name", 
                    "shape": "circle" (Basic) / "box" (Method) / "diamond" (Application) / "star" (Extension), 
                    "color": "#HEXCODE",
                    "title": "HTML Tooltip: Connection strength, functional positioning, and scenario application"
                }
            ],
            "edges": [
                {
                    "from": "id1", 
                    "to": "id2", 
                    "label": "★★★★★ (Strength)",
                    "color": {"color": "#HEXCODE"}
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
           - **Direct Application (Red Edge #EF5350)**: A solves B.
           - **Similar Transfer (Blue Edge #29B6F6)**: A/B are similar logic.
           - **Cross-module Intersection (Green Edge #66BB6A)**: Module 1 + Module 2.
           - **Scenario Landing (Yellow Edge #FBC02D)**: Knowledge -> Case study.
        4. **Structure**: Non-hierarchical mesh. Show how different weeks/topics connect horizontally.
        """
    
    user_prompt = f"Please analyze the following syllabus content and strictly generate structured data according to the above model requirements:\n\n{syllabus_text[:20000]}" 
    
    return call_doubao(system_prompt, user_prompt)

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
    
    return call_doubao(system_prompt, user_prompt)

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
    
    result = call_doubao(system_prompt, user_prompt)
    if result:
        return result.get('cross_links', [])
    return []
