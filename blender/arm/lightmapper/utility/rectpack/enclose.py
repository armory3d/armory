import heapq # heapq.heappush, heapq.heappop
from .packer import newPacker, PackingMode, PackingBin, SORT_LSIDE
from .skyline import SkylineBlWm



class Enclose(object):

    def __init__(self, rectangles=[], max_width=None, max_height=None, rotation=True):
        """
        Arguments:
            rectangles (list): Rectangle to be enveloped
                [(width1, height1), (width2, height2), ...]
            max_width (number|None): Enveloping rectangle max allowed width.
            max_height (number|None): Enveloping rectangle max allowed height.
            rotation (boolean): Enable/Disable rectangle rotation.
        """
        # Enclosing rectangle max width
        self._max_width = max_width

        # Encloseing rectangle max height
        self._max_height = max_height

        # Enable or disable rectangle rotation
        self._rotation = rotation

        # Default packing algorithm
        self._pack_algo = SkylineBlWm
        
        # rectangles to enclose [(width, height), (width, height, ...)]
        self._rectangles = []
        for r in rectangles:
            self.add_rect(*r)

    def _container_candidates(self):
        """Generate container candidate list 
        
        Returns:
            tuple list: [(width1, height1), (width2, height2), ...] 
        """
        if not self._rectangles:
            return []

        if self._rotation:
            sides = sorted(side for rect in self._rectangles for side in rect)
            max_height = sum(max(r[0], r[1]) for r in self._rectangles)
            min_width = max(min(r[0], r[1]) for r in self._rectangles)
            max_width = max_height
        else:
            sides = sorted(r[0] for r in self._rectangles)
            max_height = sum(r[1] for r in self._rectangles)
            min_width = max(r[0] for r in self._rectangles)
            max_width = sum(sides)
        
        if self._max_width and self._max_width < max_width:
            max_width = self._max_width

        if self._max_height and self._max_height < max_height:
            max_height = self._max_height

        assert(max_width>min_width)
 
        # Generate initial container widths
        candidates = [max_width, min_width]

        width = 0
        for s in reversed(sides):
            width += s
            candidates.append(width)
        
        width = 0
        for s in sides:
            width += s
            candidates.append(width)

        candidates.append(max_width)
        candidates.append(min_width)
      
        # Remove duplicates and widths too big or small
        seen = set()
        seen_add = seen.add
        candidates = [x for x in candidates if not(x in seen or seen_add(x))] 
        candidates = [x for x in candidates if not(x>max_width or x<min_width)]
        
        # Remove candidates too small to fit all the rectangles
        min_area = sum(r[0]*r[1] for r in self._rectangles)
        return [(c, max_height) for c in candidates if c*max_height>=min_area]
   
    def _refine_candidate(self, width, height):
        """
        Use bottom-left packing algorithm to find a lower height for the 
        container.

        Arguments:
            width
            height

        Returns:
            tuple (width, height, PackingAlgorithm):
        """
        packer = newPacker(PackingMode.Offline, PackingBin.BFF, 
                pack_algo=self._pack_algo, sort_algo=SORT_LSIDE,
                rotation=self._rotation)
        packer.add_bin(width, height)
       
        for r in self._rectangles:
            packer.add_rect(*r)

        packer.pack()

        # Check all rectangles where packed
        if len(packer[0]) != len(self._rectangles):
            return None

        # Find highest rectangle
        new_height = max(packer[0], key=lambda x: x.top).top
        return(width, new_height, packer)

    def generate(self):
    
        # Generate initial containers
        candidates = self._container_candidates()
        if not candidates:
            return None

        # Refine candidates and return the one with the smaller area
        containers = [self._refine_candidate(*c) for c in candidates]
        containers = [c for c in containers if c]
        if not containers:
            return None

        width, height, packer = min(containers, key=lambda x: x[0]*x[1])

        packer.width = width
        packer.height = height
        return packer

    def add_rect(self, width, height):
        """
        Add anoter rectangle to be enclosed

        Arguments:
            width (number): Rectangle width
            height (number): Rectangle height
        """
        self._rectangles.append((width, height))


