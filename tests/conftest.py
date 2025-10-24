# Configuration file for pytest

# Test fixtures for common test data
import copy


# Test data for activities - a smaller set for testing
TEST_ACTIVITIES = {
    "Test Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 3,
        "participants": ["test1@mergington.edu"]
    },
    "Test Soccer Team": {
        "description": "Join the school soccer team for training and matches",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 5,
        "participants": []
    }
}


def get_fresh_test_activities():
    """Return a fresh copy of test activities."""
    return copy.deepcopy(TEST_ACTIVITIES)