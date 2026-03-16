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
    response = graph.invoke({"email": email}, config={
            "configurable":{
                "thread_id": "1"
            }
        },)
    assert response["category"] == expected_category
    assert response["priority_score"] == expected_priority_score

def test_individual_nodes():
    #categorize_email
    result = graph.nodes["categorize_email"].invoke(
        {"email": "check this offer."}
        )
    assert result["category"] == "spam"


    #assign_priority
    result = graph.nodes["assign_priority"].invoke(
        {"category": "spam"}
        )
    assert result["priority_score"] == 1

    #draft_response
    result = graph.nodes["draft_response"].invoke(
        {"category": "spam"}
        )
    assert "Go away!" in result["response"]

def test_partial_execution():
    graph.update_state(
        config={
            "configurable":{
                "thread_id": "1"
            }
        },
        values={
            "email": "Please check this offer.",
            "category": "spam",
        },
        as_node="categorize_email",
    )

    result = graph.invoke(
        None, 
        config={
            "configurable":{
                "thread_id": "1"
            }
        }, 
        interrupt_after="draft_response",
    )

    assert result["priority_score"] == 1

