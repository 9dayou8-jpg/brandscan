from backend.app.prioritizer import deduplicate_issues


def test_deduplicate_issues_keeps_highest_scored_representative():
    issues = [
        {
            "id": "seo-title",
            "title": "Title 개선",
            "root_cause_id": "content-context-001",
            "resolution_group_id": "content-messaging-001",
            "score": 18,
        },
        {
            "id": "seo-description",
            "title": "Description 개선",
            "root_cause_id": "content-context-001",
            "resolution_group_id": "content-messaging-001",
            "score": 21,
        },
        {
            "id": "geo-question",
            "title": "질문형 콘텐츠 보강",
            "root_cause_id": "geo-structure-001",
            "resolution_group_id": "geo-content-001",
            "score": 16,
        },
    ]

    result = deduplicate_issues(issues)

    assert [item["id"] for item in result] == ["seo-description", "geo-question"]
    assert result[0]["related_issue_ids"] == ["seo-title"]
    assert result[0]["deduplicated_count"] == 2
