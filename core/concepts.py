"""
Concept map for the Adaptive Learning and Assessment Portal.

Each concept has a unique ID, a name, and a list of prerequisites.
"""

CONCEPTS = {
    "C1": {
        "name": "Variables and Functions",
        "prerequisites": [],
    },
    "C2": {
        "name": "Classes and Objects",
        "prerequisites": ["C1"],
    },
    "C3": {
        "name": "Encapsulation",
        "prerequisites": ["C2"],
    },
    "C4": {
        "name": "Inheritance",
        "prerequisites": ["C2"],
    },
    "C5": {
        "name": "Dependency Injection",
        "prerequisites": ["C4"],
    },
}