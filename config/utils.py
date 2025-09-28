from unfold.dataclasses import SearchResult

def search_callback(request, search_term):

    return [
        SearchResult(
            title="Some title",
            description="Extra content",
            link="https://example.com",
            icon="database",
        )
    ]