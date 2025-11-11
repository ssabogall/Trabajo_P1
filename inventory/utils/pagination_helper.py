"""
Pagination utility for consistent pagination across the application.
This helper provides a reusable way to paginate querysets with consistent behavior.
"""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class PaginationHelper:
    """
    Helper class to handle pagination logic consistently across views.
    
    Usage:
        queryset = Product.objects.all()
        pagination = PaginationHelper(queryset, request, items_per_page=10, order_by='name')
        context = pagination.get_context()
    """
    
    def __init__(self, queryset, request, items_per_page=10, order_by=None):
        """
        Initialize the pagination helper.
        
        Args:
            queryset: Django QuerySet to paginate
            request: HTTP request object
            items_per_page: Number of items per page (default: 10)
            order_by: Field name to order by (default: None)
        """
        self.request = request
        self.items_per_page = items_per_page
        
        # Apply ordering if specified
        if order_by:
            queryset = queryset.order_by(order_by)
        
        self.queryset = queryset
        self.paginator = Paginator(queryset, items_per_page)
        self.page_number = request.GET.get('page', 1)
        
        # Get the current page
        try:
            self.page_obj = self.paginator.page(self.page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            self.page_obj = self.paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page
            self.page_obj = self.paginator.page(self.paginator.num_pages)
    
    def get_context(self):
        """
        Get the context dictionary for templates.
        
        Returns:
            dict: Context with pagination data
        """
        return {
            'page_obj': self.page_obj,
            'paginator': self.paginator,
            'page_range': self.get_page_range(),
            'current_page': self.page_obj.number,
            'total_pages': self.paginator.num_pages,
            'page_indicator': f"{self.page_obj.number}/{self.paginator.num_pages}",
            'has_previous': self.page_obj.has_previous(),
            'has_next': self.page_obj.has_next(),
            'previous_page_number': self.page_obj.previous_page_number() if self.page_obj.has_previous() else None,
            'next_page_number': self.page_obj.next_page_number() if self.page_obj.has_next() else None,
        }
    
    def get_page_range(self):
        """
        Get a smart page range for pagination display.
        Shows pages around the current page to avoid too many page numbers.
        
        Returns:
            range: Page range to display
        """
        current_page = self.page_obj.number
        total_pages = self.paginator.num_pages
        
        # Show all pages if total is 7 or less
        if total_pages <= 7:
            return range(1, total_pages + 1)
        
        # Show pages around current page
        if current_page <= 4:
            return range(1, 6)
        elif current_page >= total_pages - 3:
            return range(total_pages - 4, total_pages + 1)
        else:
            return range(current_page - 2, current_page + 3)
    
    def get_items(self):
        """
        Get the items for the current page.
        
        Returns:
            QuerySet: Items for current page
        """
        return self.page_obj.object_list
