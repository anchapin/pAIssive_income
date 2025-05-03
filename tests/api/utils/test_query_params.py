"""
Tests for the query parameter utilities.
"""


import unittest
from datetime import datetime, timedelta

from api.utils.query_params import 

(
    FilterOperator,
    QueryParams,
    SortDirection,
    apply_filtering,
    apply_pagination,
    apply_sorting,
)


class TestQueryParams(unittest.TestCase):
    """Tests for the QueryParams class."""

    def test_init(self):
        """Test initialization of QueryParams."""
        # Test default values
        params = QueryParams()
        self.assertEqual(params.page, 1)
        self.assertEqual(params.page_size, 10)
        self.assertIsNone(params.sort_by)
        self.assertEqual(params.sort_dir, SortDirection.ASC)
        self.assertEqual(params.filters, {})
        self.assertEqual(params.filter_operators, {})
        self.assertEqual(params.offset, 0)
        self.assertEqual(params.limit, 10)

        # Test custom values
        params = QueryParams(
            page=2,
            page_size=20,
            sort_by="name",
            sort_dir=SortDirection.DESC,
            filters={"name": "test"},
            filter_operators={"name": FilterOperator.EQ},
        )
        self.assertEqual(params.page, 2)
        self.assertEqual(params.page_size, 20)
        self.assertEqual(params.sort_by, "name")
        self.assertEqual(params.sort_dir, SortDirection.DESC)
        self.assertEqual(params.filters, {"name": "test"})
        self.assertEqual(params.filter_operators, {"name": FilterOperator.EQ})
        self.assertEqual(params.offset, 20)
        self.assertEqual(params.limit, 20)

        # Test max page size
        params = QueryParams(page_size=200, max_page_size=100)
        self.assertEqual(params.page_size, 100)

    def test_from_request(self):
        """Test creating QueryParams from request parameters."""
        # Test simple parameters
        request_params = {
            "page": "2",
            "page_size": "20",
            "sort_by": "name",
            "sort_dir": "desc",
        }
        params = QueryParams.from_request(request_params)
        self.assertEqual(params.page, 2)
        self.assertEqual(params.page_size, 20)
        self.assertEqual(params.sort_by, "name")
        self.assertEqual(params.sort_dir, SortDirection.DESC)

        # Test filter parameters
        request_params = {
            "filter[name]": "test",
            "filter[age][gt]": "18",
            "filter[active]": "true",
            "filter[score][gte]": "4.5",
        }
        params = QueryParams.from_request(request_params)
        self.assertEqual(params.filters["name"], "test")
        self.assertEqual(params.filters["age"], 18)
        self.assertEqual(params.filters["active"], True)
        self.assertEqual(params.filters["score"], 4.5)
        self.assertEqual(params.filter_operators["name"], FilterOperator.EQ)
        self.assertEqual(params.filter_operators["age"], FilterOperator.GT)
        self.assertEqual(params.filter_operators["active"], FilterOperator.EQ)
        self.assertEqual(params.filter_operators["score"], FilterOperator.GTE)

        # Test allowed fields
        request_params = {
            "sort_by": "name",
            "filter[name]": "test",
            "filter[age]": "18",
        }
        params = QueryParams.from_request(
            request_params,
            allowed_sort_fields=["name", "created_at"],
            allowed_filter_fields=["name"],
        )
        self.assertEqual(params.sort_by, "name")
        self.assertEqual(params.filters, {"name": "test"})
        self.assertEqual(params.filter_operators, {"name": FilterOperator.EQ})

        # Test invalid sort field
        request_params = {"sort_by": "invalid"}
        params = QueryParams.from_request(
            request_params, allowed_sort_fields=["name", "created_at"]
        )
        self.assertIsNone(params.sort_by)


class TestPagination(unittest.TestCase):
    """Tests for the pagination utilities."""

    def test_apply_pagination(self):
        """Test applying pagination to a list of items."""
        items = list(range(100))

        # Test first page
        params = QueryParams(page=1, page_size=10)
        paginated, total = apply_pagination(items, params)
        self.assertEqual(paginated, list(range(10)))
        self.assertEqual(total, 100)

        # Test second page
        params = QueryParams(page=2, page_size=10)
        paginated, total = apply_pagination(items, params)
        self.assertEqual(paginated, list(range(10, 20)))
        self.assertEqual(total, 100)

        # Test last page
        params = QueryParams(page=10, page_size=10)
        paginated, total = apply_pagination(items, params)
        self.assertEqual(paginated, list(range(90, 100)))
        self.assertEqual(total, 100)

        # Test empty list
        params = QueryParams(page=1, page_size=10)
        paginated, total = apply_pagination([], params)
        self.assertEqual(paginated, [])
        self.assertEqual(total, 0)

        # Test page beyond total
        params = QueryParams(page=11, page_size=10)
        paginated, total = apply_pagination(items, params)
        self.assertEqual(paginated, [])
        self.assertEqual(total, 100)


class TestFiltering(unittest.TestCase):
    """Tests for the filtering utilities."""

    def setUp(self):
        """Set up test data."""
        self.items = [
            {
                "id": 1,
                "name": "Item 1",
                "price": 10.5,
                "active": True,
                "tags": ["a", "b"],
            },
            {
                "id": 2,
                "name": "Item 2",
                "price": 20.0,
                "active": False,
                "tags": ["b", "c"],
            },
            {
                "id": 3,
                "name": "Test 3",
                "price": 15.0,
                "active": True,
                "tags": ["a", "c"],
            },
            {"id": 4, "name": "Test 4", "price": 25.5, "active": True, "tags": ["d"]},
            {
                "id": 5,
                "name": "Item 5",
                "price": 5.0,
                "active": False,
                "tags": ["a", "b", "c"],
            },
        ]

    def test_apply_filtering_eq(self):
        """Test filtering with EQ operator."""
        params = QueryParams(
            filters={"active": True}, filter_operators={"active": FilterOperator.EQ}
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 3)
        self.assertEqual([item["id"] for item in filtered], [1, 3, 4])

    def test_apply_filtering_neq(self):
        """Test filtering with NEQ operator."""
        params = QueryParams(
            filters={"active": True}, filter_operators={"active": FilterOperator.NEQ}
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 2)
        self.assertEqual([item["id"] for item in filtered], [2, 5])

    def test_apply_filtering_gt(self):
        """Test filtering with GT operator."""
        params = QueryParams(
            filters={"price": 15.0}, filter_operators={"price": FilterOperator.GT}
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 2)
        self.assertEqual([item["id"] for item in filtered], [2, 4])

    def test_apply_filtering_gte(self):
        """Test filtering with GTE operator."""
        params = QueryParams(
            filters={"price": 15.0}, filter_operators={"price": FilterOperator.GTE}
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 3)
        self.assertEqual([item["id"] for item in filtered], [2, 3, 4])

    def test_apply_filtering_lt(self):
        """Test filtering with LT operator."""
        params = QueryParams(
            filters={"price": 15.0}, filter_operators={"price": FilterOperator.LT}
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 2)
        self.assertEqual([item["id"] for item in filtered], [1, 5])

    def test_apply_filtering_lte(self):
        """Test filtering with LTE operator."""
        params = QueryParams(
            filters={"price": 15.0}, filter_operators={"price": FilterOperator.LTE}
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 3)
        self.assertEqual([item["id"] for item in filtered], [1, 3, 5])

    def test_apply_filtering_contains(self):
        """Test filtering with CONTAINS operator."""
        params = QueryParams(
            filters={"name": "Test"}, filter_operators={"name": FilterOperator.CONTAINS}
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 2)
        self.assertEqual([item["id"] for item in filtered], [3, 4])

    def test_apply_filtering_starts_with(self):
        """Test filtering with STARTS_WITH operator."""
        params = QueryParams(
            filters={"name": "Item"},
            filter_operators={"name": FilterOperator.STARTS_WITH},
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 3)
        self.assertEqual([item["id"] for item in filtered], [1, 2, 5])

    def test_apply_filtering_ends_with(self):
        """Test filtering with ENDS_WITH operator."""
        params = QueryParams(
            filters={"name": "3"}, filter_operators={"name": FilterOperator.ENDS_WITH}
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 1)
        self.assertEqual([item["id"] for item in filtered], [3])

    def test_apply_filtering_multiple(self):
        """Test filtering with multiple conditions."""
        params = QueryParams(
            filters={"name": "Item", "price": 10.0},
            filter_operators={
                "name": FilterOperator.STARTS_WITH,
                "price": FilterOperator.GT,
            },
        )
        filtered = apply_filtering(self.items, params)
        # Items 1, 2, and 5 have names starting with "Item"
        # Items 1, 2, 3, and 4 have prices > 10.0 (note: 10.5 > 10.0)
        # Therefore, items 1 and 2 match both conditions
        self.assertEqual(len(filtered), 2)
        self.assertEqual(sorted([item["id"] for item in filtered]), [1, 2])


class TestSorting(unittest.TestCase):
    """Tests for the sorting utilities."""

    def setUp(self):
        """Set up test data."""
        self.items = [
            {"id": 1, "name": "Item C", "price": 10.5, "active": True},
            {"id": 2, "name": "Item A", "price": 20.0, "active": False},
            {"id": 3, "name": "Item E", "price": 15.0, "active": True},
            {"id": 4, "name": "Item B", "price": 25.5, "active": True},
            {"id": 5, "name": "Item D", "price": 5.0, "active": False},
        ]

    def test_apply_sorting_asc(self):
        """Test sorting in ascending order."""
        params = QueryParams(sort_by="name", sort_dir=SortDirection.ASC)
        sorted_items = apply_sorting(self.items, params)
        self.assertEqual(
            [item["name"] for item in sorted_items],
            ["Item A", "Item B", "Item C", "Item D", "Item E"],
        )

    def test_apply_sorting_desc(self):
        """Test sorting in descending order."""
        params = QueryParams(sort_by="name", sort_dir=SortDirection.DESC)
        sorted_items = apply_sorting(self.items, params)
        self.assertEqual(
            [item["name"] for item in sorted_items],
            ["Item E", "Item D", "Item C", "Item B", "Item A"],
        )

    def test_apply_sorting_numeric(self):
        """Test sorting numeric values."""
        params = QueryParams(sort_by="price", sort_dir=SortDirection.ASC)
        sorted_items = apply_sorting(self.items, params)
        self.assertEqual(
            [item["price"] for item in sorted_items], [5.0, 10.5, 15.0, 20.0, 25.5]
        )

    def test_apply_sorting_boolean(self):
        """Test sorting boolean values."""
        params = QueryParams(sort_by="active", sort_dir=SortDirection.ASC)
        sorted_items = apply_sorting(self.items, params)
        self.assertEqual(
            [item["active"] for item in sorted_items], [False, False, True, True, True]
        )

    def test_apply_sorting_none(self):
        """Test sorting with None values."""
        items = [
            {"id": 1, "name": "Item A", "price": 10.5},
            {"id": 2, "name": None, "price": 20.0},
            {"id": 3, "name": "Item B", "price": None},
            {"id": 4, "name": "Item C", "price": 25.5},
            {"id": 5, "name": None, "price": None},
        ]

        # Test sorting with None values (ascending)
        params = QueryParams(sort_by="name", sort_dir=SortDirection.ASC)
        sorted_items = apply_sorting(items, params)
        self.assertEqual(
            [item["name"] for item in sorted_items],
            ["Item A", "Item B", "Item C", None, None],
        )

        # Test sorting with None values (descending)
        params = QueryParams(sort_by="name", sort_dir=SortDirection.DESC)
        sorted_items = apply_sorting(items, params)
        self.assertEqual(
            [item["name"] for item in sorted_items],
            [None, None, "Item C", "Item B", "Item A"],
        )


class TestAdvancedFiltering(unittest.TestCase):
    """Tests for advanced filtering scenarios."""

    def setUp(self):
        """Set up test data with complex fields."""
        self.now = datetime.now()
        self.items = [
            {
                "id": 1,
                "name": "Project Alpha",
                "details": {"category": "AI", "difficulty": "high"},
                "tags": ["python", "machine-learning", "nlp"],
                "created_at": self.now - timedelta(days=5),
                "stats": {"views": 100, "likes": 50},
            },
            {
                "id": 2,
                "name": "Project Beta",
                "details": {"category": "Web", "difficulty": "medium"},
                "tags": ["javascript", "react", "frontend"],
                "created_at": self.now - timedelta(days=3),
                "stats": {"views": 150, "likes": 75},
            },
            {
                "id": 3,
                "name": "Project Gamma",
                "details": {"category": "AI", "difficulty": "medium"},
                "tags": ["python", "tensorflow", "deep-learning"],
                "created_at": self.now - timedelta(days=1),
                "stats": {"views": 80, "likes": 40},
            },
        ]

    def test_nested_field_filtering(self):
        """Test filtering on nested object fields."""
        params = QueryParams(
            filters={"details.category": "AI"},
            filter_operators={"details.category": FilterOperator.EQ},
        )

        def nested_field_getter(item, field):
            if "." in field:
                main_field, sub_field = field.split(".")
                return item.get(main_field, {}).get(sub_field)
            return item.get(field)

        filtered = apply_filtering(self.items, params, nested_field_getter)
        self.assertEqual(len(filtered), 2)
        self.assertEqual([item["id"] for item in filtered], [1, 3])

    def test_date_range_filtering(self):
        """Test filtering by date range."""
        params = QueryParams(
            filters={"created_at": self.now - timedelta(days=4)},
            filter_operators={"created_at": FilterOperator.GT},
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 2)
        self.assertEqual([item["id"] for item in filtered], [2, 3])

    def test_array_field_filtering(self):
        """Test filtering by array field contents."""
        params = QueryParams(
            filters={"tags": "python"},
            filter_operators={"tags": FilterOperator.CONTAINS},
        )
        filtered = apply_filtering(self.items, params)
        self.assertEqual(len(filtered), 2)
        self.assertEqual([item["id"] for item in filtered], [1, 3])

    def test_case_insensitive_filtering(self):
        """Test case-insensitive filtering."""
        params = QueryParams(
            filters={"details.category": "ai"},
            filter_operators={"details.category": FilterOperator.EQ},
        )

        def case_insensitive_getter(item, field):
            if "." in field:
                main_field, sub_field = field.split(".")
                value = item.get(main_field, {}).get(sub_field)
            else:
                value = item.get(field)
            return value.lower() if isinstance(value, str) else value

        filtered = apply_filtering(self.items, params, case_insensitive_getter)
        self.assertEqual(len(filtered), 2)
        self.assertEqual([item["id"] for item in filtered], [1, 3])


class TestAdvancedSorting(unittest.TestCase):
    """Tests for advanced sorting scenarios."""

    def setUp(self):
        """Set up test data with complex fields."""
        self.now = datetime.now()
        self.items = [
            {
                "id": 1,
                "name": "Project Alpha",
                "priority": 1,
                "stats": {"score": 85},
                "created_at": self.now - timedelta(days=5),
            },
            {
                "id": 2,
                "name": "Project Beta",
                "priority": 1,
                "stats": {"score": 90},
                "created_at": self.now - timedelta(days=3),
            },
            {
                "id": 3,
                "name": "Project Gamma",
                "priority": 2,
                "stats": {"score": 85},
                "created_at": self.now - timedelta(days=1),
            },
        ]

    def test_multi_field_sorting(self):
        """Test sorting by multiple fields (priority desc, stats.score desc)."""

        def multi_field_getter(item, field):
            if field == "priority":
                return item["priority"]
            elif field == "stats.score":
                return item["stats"]["score"]
            return item.get(field)

        # Sort by priority (desc)
        params1 = QueryParams(sort_by="priority", sort_dir=SortDirection.DESC)
        sorted1 = apply_sorting(self.items, params1, multi_field_getter)

        # Then sort by score (desc)
        params2 = QueryParams(sort_by="stats.score", sort_dir=SortDirection.DESC)
        final_sorted = apply_sorting(sorted1, params2, multi_field_getter)

        expected_order = [
            3,
            2,
            1,
        ]  # Project Gamma (high priority), Beta (high score), Alpha
        self.assertEqual([item["id"] for item in final_sorted], expected_order)

    def test_case_insensitive_sorting(self):
        """Test case-insensitive sorting."""
        items = [
            {"id": 1, "name": "alpha"},
            {"id": 2, "name": "Beta"},
            {"id": 3, "name": "gamma"},
        ]

        def case_insensitive_getter(item, field):
            value = item.get(field)
            return value.lower() if isinstance(value, str) else value

        params = QueryParams(sort_by="name", sort_dir=SortDirection.ASC)
        sorted_items = apply_sorting(items, params, case_insensitive_getter)
        self.assertEqual([item["id"] for item in sorted_items], [1, 2, 3])

    def test_nested_field_sorting(self):
        """Test sorting by nested object fields."""

        def nested_field_getter(item, field):
            if "." in field:
                main_field, sub_field = field.split(".")
                return item.get(main_field, {}).get(sub_field)
            return item.get(field)

        params = QueryParams(sort_by="stats.score", sort_dir=SortDirection.DESC)
        sorted_items = apply_sorting(self.items, params, nested_field_getter)
        expected_order = [2, 1, 3]  # Beta (90), Alpha (85), Gamma (85)
        self.assertEqual([item["id"] for item in sorted_items], expected_order)


if __name__ == "__main__":
    unittest.main()