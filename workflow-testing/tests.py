import pytest
from main import graph

@pytest.mark.parametrize(
    "email, expected_category, expected_priority_score",
    [
        ("Hello, I need help with my account. It's urgent.", "urgent", 10),
        ("Hello, I need to talk to you.", "normal", 5),
        ("Get 20% discount on your next purchase!", "spam", 1),
    ]
)
def test_full_graph(email, expected_category, expected_priority_score):
    response = graph.invoke({"email": email})
    assert response["category"] == expected_category
    assert response["priority_score"] == expected_priority_score

    