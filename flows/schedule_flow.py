schedule_flow = {
    "day_of_week": {
        "prev": None,
        "next": "start_time",
        "prompt": "Enter the day of the week (e.g., Monday, Tuesday):",
        "data": {}
    },
    "start_time": {
        "prev": "day_of_week",
        "next": "end_time",
        "prompt": "Enter the start time (e.g., 14:00):",
        "data": {}
    },
    "end_time": {
        "prev": "start_time",
        "next": None,
        "prompt": "Enter the end time (e.g., 15:00):",
        "data": {}
    }
}