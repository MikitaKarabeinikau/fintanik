student_flow ={
    "name": {
        "prev": None,
        "next": "surname",
        "prompt": "Enter the student's name:",
        "data": {}
    },
    "surname": {
        "prev": "name",
        "next": "price",
        "prompt": "Enter the student's surname:",
        "data": {}
    },
    "price": {
        "prev": "surname",
        "next": "unpaid_lessons",
        "prompt": "Enter the student's price:",
        "data": {}
    },
    "unpaid_lessons": {
        "prev": "price",
        "next": "balance",
        "prompt": "Enter the number of unpaid lessons:",
        "data": {}
    },
    "balance": {
        "prev": "unpaid_lessons",
        "next": "payment_frequency",
        "prompt": "Enter the student's balance:",
        "data": {}
    },
    "payment_frequency": {
        "prev": "balance",
        "next": None,
        "prompt": "Enter the payment frequency (e.g., monthly, weekly):",
        "data": {}
    }
}