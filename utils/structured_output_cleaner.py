import json

def clean_json_output(raw_text):
    try:
        return json.loads(raw_text)
    except:
        return {
            "skills": [],
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "score": 0
        }