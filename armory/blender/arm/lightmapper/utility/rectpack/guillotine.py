from .pack_algo import PackingAlgorithm
from .geometry import Rectangle
import itertools
import operator


class Guillotine(PackingAlgorithm):
    """Implementation of several variants of Guillotine packing algorithm
    
    For a more detailed explanation of the algorithm used, see:
    Jukka Jylanki - A Thousand Ways to Pack the Bin (February 27, 2010)
    """
    def __init__(self, width, height, rot=True, merge=True, *args, **kwargs):
        """
        Arguments:
            width (int, float):
            height (int, float):
            merge (bool): Optional keyword argument
        """
        self._merge = merge
        super(Guillotine, self).__init__(width, height, rot, *args, **kwargs)
        

    def _add_section(self, section):
        """Adds a new section to the free section list, but before that and if 
        section merge is enabled, tries to join the rectangle with all existing 
        sections, if successful the resulting section is again merged with the 
        remaining sections until the operation fails. The result is then 
        appended to the list.

        Arguments:
            section (Rectangle): New free section.
        """
        section.rid = 0     
        plen = 0

        while self._merge and self._sections and plen != len(self._sections):
            plen = len(self._sections)
            self._sections = [s for s in self._sections if not section.join(s)]
        self._sections.append(section)


    def _split_horizontal(self, section, width, height):
        """For an horizontal split the rectangle is placed in the lower
        left corner of the section (section's xy coordinates), the top
        most side of the rectangle and its horizontal continuation,
        marks the line of division for the split.
        +-----------------+
        |                 |
        |                 |
        |                 |
        |                 |
        +-------+---------+
        |#######|         |
        |#######|         |
        |#######|         |
        +-------+---------+
        If the rectangle width is equal to the the section width, only one
        section is created over the rectangle. If the rectangle height is
        equal to the section height, only one section to the right of the
        rectangle is created. If both width and height are equal, no sections
        are created.
        """
        # First remove the section we are splitting so it doesn't 
        # interfere when later we try to merge the resulting split
        # rectangles, with the rest of free sections.
        #self._sections.remove(section)

        # Creates two new empty sections, and returns the new rectangle.
        if height < section.height:
            self._add_section(Rectangle(section.x, section.y+height,
                section.width, section.height-height))

        if width < section.width:
            self._add_section(Rectangle(section.x+width, section.y,
                section.width-width, height))


    def _split_vertical(self, section, width, height):
        """For a vertical split the rectangle is placed in the lower
        left corner of the section (section's xy coordinates), the
        right most side of the rectangle and its vertical continuation,
        marks the line of division for the split.
        +-------+---------+
        |       |         |
        |       |         |
        |       |         |
        |       |         |
        +-------+         |
        |#######|         |
        |#######|         |
        |#######|         |
        +-------+---------+
        If the rectangle width is equal to the the section width, only one
        section is created over the rectangle. If the rectangle height is
        equal to the section height, only one section to the right of the
        rectangle is created. If both width and height are equal, no sections
        are created.
        """
        # When a section is split, depending on the rectangle size 
        # two, one, or no new sections will be created. 
        if height < section.height:
            self._add_section(Rectangle(section.x, section.y+height,
                width, section.height-height))
        
        if width < section.width:
            self._add_section(Rectangle(section.x+width, section.y,
                section.width-width, section.height))
        

    def _split(self, section, width, height):
        """
        Selects the best split for a section, given a rectangle of dimmensions
        width and height, then calls _split_vertical or _split_horizontal, 
        to do the dirty work.
       
        Arguments:
            section (Rectangle): Section to split
            width (int, float): Rectangle width
            height (int, float): Rectangle height
        """
        raise NotImplementedError


    def _section_fitness(self, section, width, height):
        """The subclass for each one of the Guillotine selection methods,
        BAF, BLSF.... will override this method, this is here only
        to asure a valid value return if the worst happens.
        """
        raise NotImplementedError

    def _select_fittest_section(self, w, h):
        """Calls _section_fitness for each of the sections in free section 
        list. Returns the section with the minimal fitness value, all the rest 
        is boilerplate to make the fitness comparison, to rotatate the rectangles,
        and to take into account when _section_fitness returns None because 
        the rectangle couldn't be placed.

        Arguments:
            w (int, float): Rectangle width
            h (int, float): Rectangle height

        Returns:
            (section, was_rotated): Returns the tuple 
                section (Rectangle): Section with best fitness
                was_rotated (bool): The rectangle was rotated 
        """
        fitn = ((self._section_fitness(s, w, h), s, False) for s in self._sections 
                if self._section_fitness(s, w, h) is not None)
        fitr = ((self._section_fitness(s, h, w), s, True) for s in self._sections 
                if self._section_fitness(s, h, w) is not None)

        if not self.rot:
            fitr = []

        fit = itertools.chain(fitn, fitr)
        
        try:
            _, sec, rot = min(fit, key=operator.itemgetter(0))
        except ValueError:
            return None, None

        return sec, rot


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

        # Obtain the best section to place the rectangle.
        section, rotated = self._select_fittest_section(width, height)
        if not section:
            return None
        
        if rotated:
            width, height = height, width
        
        # Remove section, split and store results
        self._sections.remove(section)
        self._split(section, width, height)
       
        # Store rectangle in the selected position
        rect = Rectangle(section.x, section.y, width, height, rid)
        self.rectangles.append(rect)
        return rect

    def fitness(self, width, height):
        """
        In guillotine algorithm case, returns the min of the fitness of all 
        free sections, for the given dimension, both normal and rotated
        (if rotation enabled.)
        """
        assert(width > 0 and height > 0)

        # Get best fitness section.
        section, rotated = self._select_fittest_section(width, height)
        if not section:
            return None
        
        # Return fitness of returned section, with correct dimmensions if the
        # the rectangle was rotated.
        if rotated:
            return self._section_fitness(section, height, width)
        else:
            return self._section_fitness(section, width, height)

    def reset(self):
        super(Guillotine, self).reset()
        self._sections = []
        self._add_section(Rectangle(0, 0, self.width, self.height))



class GuillotineBaf(Guillotine):
    """Implements Best Area Fit (BAF) section selection criteria for 
    Guillotine algorithm.
    """
    def _section_fitness(self, section, width, height):
        if width > section.width or height > section.height:
            return None
        return section.area()-width*height


class GuillotineBlsf(Guillotine):
    """Implements Best Long Side Fit (BLSF) section selection criteria for 
    Guillotine algorithm.
    """
    def _section_fitness(self, section, width, height):
        if width > section.width or height > section.height:
            return None
        return max(section.width-width, section.height-height)


class GuillotineBssf(Guillotine):
    """Implements Best Short Side Fit (BSSF) section selection criteria for 
    Guillotine algorithm.
    """
    def _section_fitness(self, section, width, height):
        if width > section.width or height > section.height:
            return None
        return min(section.width-width, section.height-height)


class GuillotineSas(Guillotine):
    """Implements Short Axis Split (SAS) selection rule for Guillotine 
    algorithm.
    """
    def _split(self, section, width, height):
        if section.width < section.height:
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)
        


class GuillotineLas(Guillotine):
    """Implements Long Axis Split (LAS) selection rule for Guillotine 
    algorithm.
    """
    def _split(self, section, width, height):
        if section.width >= section.height:
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)



class GuillotineSlas(Guillotine):
    """Implements Short Leftover Axis Split (SLAS) selection rule for 
    Guillotine algorithm.
    """
    def _split(self, section, width, height):
        if section.width-width < section.height-height:
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)
        


class GuillotineLlas(Guillotine):
    """Implements Long Leftover Axis Split (LLAS) selection rule for 
    Guillotine algorithm.
    """
    def _split(self, section, width, height):
        if section.width-width >= section.height-height:
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)



class GuillotineMaxas(Guillotine):
    """Implements Max Area Axis Split (MAXAS) selection rule for Guillotine
    algorithm. Maximize the larger area == minimize the smaller area.
    Tries to make the rectangles more even-sized.
    """
    def _split(self, section, width, height):
        if width*(section.height-height) <= height*(section.width-width):
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)
        


class GuillotineMinas(Guillotine):
    """Implements Min Area Axis Split (MINAS) selection rule for Guillotine 
    algorithm. 
    """
    def _split(self, section, width, height):
        if width*(section.height-height) >= height*(section.width-width):
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)
       


# Guillotine algorithms GUILLOTINE-RECT-SPLIT, Selecting one
# Axis split, and one selection criteria.
class GuillotineBssfSas(GuillotineBssf, GuillotineSas):
    pass
class GuillotineBssfLas(GuillotineBssf, GuillotineLas):
    pass
class GuillotineBssfSlas(GuillotineBssf, GuillotineSlas):
    pass
class GuillotineBssfLlas(GuillotineBssf, GuillotineLlas):
    pass
class GuillotineBssfMaxas(GuillotineBssf, GuillotineMaxas):
    pass
class GuillotineBssfMinas(GuillotineBssf, GuillotineMinas):
    pass
class GuillotineBlsfSas(GuillotineBlsf, GuillotineSas):
    pass
class GuillotineBlsfLas(GuillotineBlsf, GuillotineLas):
    pass
class GuillotineBlsfSlas(GuillotineBlsf, GuillotineSlas):
    pass
class GuillotineBlsfLlas(GuillotineBlsf, GuillotineLlas):
    pass
class GuillotineBlsfMaxas(GuillotineBlsf, GuillotineMaxas):
    pass
class GuillotineBlsfMinas(GuillotineBlsf, GuillotineMinas):
    pass
class GuillotineBafSas(GuillotineBaf, GuillotineSas):
    pass
class GuillotineBafLas(GuillotineBaf, GuillotineLas):
    pass
class GuillotineBafSlas(GuillotineBaf, GuillotineSlas):
    pass
class GuillotineBafLlas(GuillotineBaf, GuillotineLlas):
    pass
class GuillotineBafMaxas(GuillotineBaf, GuillotineMaxas):
    pass
class GuillotineBafMinas(GuillotineBaf, GuillotineMinas):
    pass



