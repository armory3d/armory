from .pack_algo import PackingAlgorithm
from .geometry import Rectangle
import itertools
import collections
import operator


first_item = operator.itemgetter(0)



class MaxRects(PackingAlgorithm):

    def __init__(self, width, height, rot=True, *args, **kwargs):
        super(MaxRects, self).__init__(width, height, rot, *args, **kwargs)
   
    def _rect_fitness(self, max_rect, width, height):
        """
        Arguments:
            max_rect (Rectangle): Destination max_rect
            width (int, float): Rectangle width
            height (int, float): Rectangle height

        Returns:
            None: Rectangle couldn't be placed into max_rect
            integer, float: fitness value 
        """
        if width <= max_rect.width and height <= max_rect.height:
            return 0
        else:
            return None

    def _select_position(self, w, h): 
        """
        Find max_rect with best fitness for placing a rectangle
        of dimentsions w*h

        Arguments:
            w (int, float): Rectangle width
            h (int, float): Rectangle height

        Returns:
            (rect, max_rect)
            rect (Rectangle): Placed rectangle or None if was unable.
            max_rect (Rectangle): Maximal rectangle were rect was placed
        """
        if not self._max_rects:
            return None, None

        # Normal rectangle
        fitn = ((self._rect_fitness(m, w, h), w, h, m) for m in self._max_rects 
                if self._rect_fitness(m, w, h) is not None)

        # Rotated rectangle
        fitr = ((self._rect_fitness(m, h, w), h, w, m) for m in self._max_rects 
                if self._rect_fitness(m, h, w) is not None)

        if not self.rot:
            fitr = []

        fit = itertools.chain(fitn, fitr)
        
        try:
            _, w, h, m = min(fit, key=first_item)
        except ValueError:
            return None, None

        return Rectangle(m.x, m.y, w, h), m

    def _generate_splits(self, m, r):
        """
        When a rectangle is placed inside a maximal rectangle, it stops being one
        and up to 4 new maximal rectangles may appear depending on the placement.
        _generate_splits calculates them.

        Arguments:
            m (Rectangle): max_rect rectangle
            r (Rectangle): rectangle placed

        Returns:
            list : list containing new maximal rectangles or an empty list
        """
        new_rects = []
        
        if r.left > m.left:
            new_rects.append(Rectangle(m.left, m.bottom, r.left-m.left, m.height))
        if r.right < m.right:
            new_rects.append(Rectangle(r.right, m.bottom, m.right-r.right, m.height))
        if r.top < m.top:
            new_rects.append(Rectangle(m.left, r.top, m.width, m.top-r.top))
        if r.bottom > m.bottom:
            new_rects.append(Rectangle(m.left, m.bottom, m.width, r.bottom-m.bottom))
        
        return new_rects

    def _split(self, rect):
        """
        Split all max_rects intersecting the rectangle rect into up to
        4 new max_rects.
        
        Arguments:
            rect (Rectangle): Rectangle

        Returns:
            split (Rectangle list): List of rectangles resulting from the split
        """
        max_rects = collections.deque()

        for r in self._max_rects:
            if r.intersects(rect):
                max_rects.extend(self._generate_splits(r, rect))
            else:
                max_rects.append(r)

        # Add newly generated max_rects
        self._max_rects = list(max_rects)

    def _remove_duplicates(self):
        """
        Remove every maximal rectangle contained by another one.
        """
        contained = set()
        for m1, m2 in itertools.combinations(self._max_rects, 2):
            if m1.contains(m2):
                contained.add(m2)
            elif m2.contains(m1):
                contained.add(m1)
        
        # Remove from max_rects
        self._max_rects = [m for m in self._max_rects if m not in contained]

    def fitness(self, width, height): 
        """
        Metric used to rate how much space is wasted if a rectangle is placed.
        Returns a value greater or equal to zero, the smaller the value the more 
        'fit' is the rectangle. If the rectangle can't be placed, returns None.

        Arguments:
            width (int, float): Rectangle width
            height (int, float): Rectangle height

        Returns:
            int, float: Rectangle fitness 
            None: Rectangle can't be placed
        """
        assert(width > 0 and height > 0)
        
        rect, max_rect = self._select_position(width, height)
        if rect is None:
            return None

        # Return fitness
        return self._rect_fitness(max_rect, rect.width, rect.height)

    def add_rect(self, width, height, rid=None):
        """
        Add rectangle of widthxheight dimensions.

        Arguments:
            width (int, float): Rectangle width
            height (int, float): Rectangle height
            rid: Optional rectangle user id

        Returns:
            Rectangle: Rectangle with placemente coordinates
            None: If the rectangle couldn be placed.
        """
        assert(width > 0 and height >0)

        # Search best position and orientation
        rect, _ = self._select_position(width, height)
        if not rect:
            return None
        
        # Subdivide all the max rectangles intersecting with the selected 
        # rectangle.
        self._split(rect)
    
        # Remove any max_rect contained by another 
        self._remove_duplicates()

        # Store and return rectangle position.
        rect.rid = rid
        self.rectangles.append(rect)
        return rect

    def reset(self):
        super(MaxRects, self).reset()
        self._max_rects = [Rectangle(0, 0, self.width, self.height)]




class MaxRectsBl(MaxRects):
    
    def _select_position(self, w, h): 
        """
        Select the position where the y coordinate of the top of the rectangle
        is lower, if there are severtal pick the one with the smallest x 
        coordinate
        """
        fitn = ((m.y+h, m.x, w, h, m) for m in self._max_rects 
                if self._rect_fitness(m, w, h) is not None)
        fitr = ((m.y+w, m.x, h, w, m) for m in self._max_rects 
                if self._rect_fitness(m, h, w) is not None)

        if not self.rot:
            fitr = []

        fit = itertools.chain(fitn, fitr)
        
        try:
            _, _, w, h, m = min(fit, key=first_item)
        except ValueError:
            return None, None

        return Rectangle(m.x, m.y, w, h), m


class MaxRectsBssf(MaxRects):
    """Best Sort Side Fit minimize short leftover side"""
    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None

        return min(max_rect.width-width, max_rect.height-height)
           
class MaxRectsBaf(MaxRects):
    """Best Area Fit pick maximal rectangle with smallest area
    where the rectangle can be placed"""
    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None
        
        return (max_rect.width*max_rect.height)-(width*height)


class MaxRectsBlsf(MaxRects):
    """Best Long Side Fit minimize long leftover side"""
    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None

        return max(max_rect.width-width, max_rect.height-height)
