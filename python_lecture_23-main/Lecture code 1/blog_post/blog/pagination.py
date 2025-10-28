from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)


class BlogPostPagination(PageNumberPagination):
    page_size = 2
    max_page_size = 100


class BlogPostLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 3
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100


# class BlogPostCursorPagination(CursorPagination):
#     page_size = 2
#     ordering = '-create_date'


class BlogPostCursorPagination(CursorPagination):
    page_size = 2
    ordering = '-id'
