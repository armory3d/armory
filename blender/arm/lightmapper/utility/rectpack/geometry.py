from math import sqrt



class Point(object):

    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)

    def __repr__(self):
        return "P({}, {})".format(self.x, self.y)

    def distance(self, point):
        """
        Calculate distance to another point
        """
        return sqrt((self.x-point.x)**2+(self.y-point.y)**2)

    def distance_squared(self, point):
        return (self.x-point.x)**2+(self.y-point.y)**2


class Segment(object):
    
    __slots__ = ('start', 'end')

    def __init__(self, start, end):
        """
        Arguments:
            start (Point): Segment start point
            end (Point): Segment end point
        """
        assert(isinstance(start, Point) and isinstance(end, Point))
        self.start = start
        self.end = end

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            None
        return self.start==other.start and self.end==other.end

    def __repr__(self):
        return "S({}, {})".format(self.start, self.end)
    
    @property
    def length_squared(self):
        """Faster than length and useful for some comparisons"""
        return self.start.distance_squared(self.end)

    @property
    def length(self):
        return self.start.distance(self.end)

    @property
    def top(self):
        return max(self.start.y, self.end.y)
    
    @property
    def bottom(self):
        return min(self.start.y, self.end.y)

    @property
    def right(self):
        return max(self.start.x, self.end.x)

    @property
    def left(self):
        return min(self.start.x, self.end.x)


class HSegment(Segment):
    """Horizontal Segment""" 

    def __init__(self, start, length):
        """
        Create an Horizontal segment given its left most end point and its
        length.

        Arguments:
            - start (Point): Starting Point
            - length (number): segment length
        """
        assert(isinstance(start, Point) and not isinstance(length, Point))
        super(HSegment, self).__init__(start, Point(start.x+length, start.y))

    @property
    def length(self):
        return self.end.x-self.start.x


class VSegment(Segment):
    """Vertical Segment"""

    def __init__(self, start, length):
        """
        Create a Vertical segment given its bottom most end point and its
        length.
        
        Arguments:
            - start (Point): Starting Point
            - length (number): segment length
        """
        assert(isinstance(start, Point) and not isinstance(length, Point))
        super(VSegment, self).__init__(start, Point(start.x, start.y+length))

    @property
    def length(self):
        return self.end.y-self.start.y
    


class Rectangle(object):
    """Basic rectangle primitive class.
    x, y-> Lower right corner coordinates
    width - 
    height - 
    """
    __slots__ = ('width', 'height', 'x', 'y', 'rid')

    def __init__(self, x, y, width, height, rid = None):
        """
        Args:
            x (int, float):
            y (int, float):
            width (int, float):
            height (int, float):
            rid (int):
        """
        assert(height >=0 and width >=0)

        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.rid = rid

    @property
    def bottom(self):
        """
        Rectangle bottom edge y coordinate
        """
        return self.y

    @property
    def top(self):
        """
        Rectangle top edge y coordiante
        """
        return self.y+self.height

    @property
    def left(self):
        """
        Rectangle left ednge x coordinate
        """
        return self.x

    @property
    def right(self):
        """
        Rectangle right edge x coordinate
        """
        return self.x+self.width

    @property
    def corner_top_l(self):
        return Point(self.left, self.top)

    @property
    def corner_top_r(self):
        return Point(self.right, self.top)

    @property
    def corner_bot_r(self):
        return Point(self.right, self.bottom)

    @property
    def corner_bot_l(self):
        return Point(self.left, self.bottom)

    def __lt__(self, other):
        """
        Compare rectangles by area (used for sorting)
        """
        return self.area() < other.area()
    
    def __eq__(self, other):
        """
        Equal rectangles have same area.
        """
        if not isinstance(other, self.__class__):
            return False

        return (self.width == other.width and \
                self.height == other.height and \
                self.x == other.x and \
                self.y == other.y)

    def __hash__(self):
        return hash((self.x, self.y, self.width, self.height))

    def __iter__(self):
        """
        Iterate through rectangle corners
        """
        yield self.corner_top_l
        yield self.corner_top_r
        yield self.corner_bot_r
        yield self.corner_bot_l

    def __repr__(self):
        return "R({}, {}, {}, {})".format(self.x, self.y, self.width, self.height)

    def area(self):
        """
        Rectangle area
        """
        return self.width * self.height

    def move(self, x, y):
        """
        Move Rectangle to x,y coordinates

        Arguments:
            x (int, float): X coordinate
            y (int, float): Y coordinate
        """
        self.x = x
        self.y = y

    def contains(self, rect):
        """
        Tests if another rectangle is contained by this one

        Arguments:
            rect (Rectangle): The other rectangle

        Returns:
            bool: True if it is container, False otherwise
        """
        return (rect.y >= self.y and \
                rect.x >= self.x and \
                rect.y+rect.height <= self.y+self.height and \
                rect.x+rect.width  <= self.x+self.width)

    def intersects(self, rect, edges=False):
        """
        Detect intersections between this and another Rectangle.

        Parameters:
            rect (Rectangle): The other rectangle.
            edges (bool): True to consider rectangles touching by their
                edges or corners to be intersecting.
                (Should have been named include_touching)

        Returns:
            bool: True if the rectangles intersect, False otherwise
        """
        if edges:
            if (self.bottom > rect.top or self.top < rect.bottom or\
                self.left > rect.right or self.right < rect.left):
                return False
        else:
            if (self.bottom >= rect.top or self.top <= rect.bottom or
                self.left >= rect.right or self.right <= rect.left):
                return False

        return True

    def intersection(self, rect, edges=False):
        """
        Returns the rectangle resulting of the intersection between this and another 
        rectangle. If the rectangles are only touching by their edges, and the 
        argument 'edges' is True the rectangle returned will have an area of 0.
        Returns None if there is no intersection.
        
        Arguments:
             rect (Rectangle): The other rectangle.
             edges (bool): If True Rectangles touching by their edges are 
                considered to be intersection. In this case a rectangle of 
                0 height or/and width will be returned.

        Returns:
            Rectangle: Intersection.
            None: There was no intersection.
        """
        if not self.intersects(rect, edges=edges):
            return None
        
        bottom = max(self.bottom, rect.bottom)
        left = max(self.left, rect.left)
        top = min(self.top, rect.top)
        right = min(self.right, rect.right)

        return Rectangle(left, bottom, right-left, top-bottom)

    def join(self, other):
        """
        Try to join a rectangle to this one, if the result is also a rectangle 
        and the operation is successful and this rectangle is modified to the union.

        Arguments:
            other (Rectangle): Rectangle to join

        Returns:
            bool: True when successfully joined, False otherwise
        """
        if self.contains(other):
            return True

        if other.contains(self):
            self.x = other.x
            self.y = other.y
            self.width = other.width
            self.height = other.height
            return True

        if not self.intersects(other, edges=True):
            return False

        # Other rectangle is Up/Down from this
        if  self.left == other.left and self.width == other.width:
            y_min = min(self.bottom, other.bottom)
            y_max = max(self.top, other.top)  
            self.y = y_min
            self.height = y_max-y_min
            return True

        # Other rectangle is Right/Left from this
        if  self.bottom == other.bottom and self.height == other.height:
            x_min = min(self.left, other.left)
            x_max = max(self.right, other.right)
            self.x = x_min
            self.width = x_max-x_min
            return True

        return False

