from fastapi import APIRouter

router = APIRouter()

@router.get("/jobs")
def get_jobs():
    return [
        {
            "title": "Electrician needed",
            "category": "Electrician",
            "location": "Thiruvanthapuram"
        },
        {
        "title": "Plumber Required",
        "category" : "Plumber",
        "location": "Kollam"
        }
    ]