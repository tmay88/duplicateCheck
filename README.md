# duplicateCheck
Checks for duplicate polygon geometries by finding the centroid then comparing the x/y of the point.

fullAddressDulicates - looks for identical strings such as two seperate polygons with the same full address listing.

duplicateCheck - will mark all identical polygons with 'True' except for the first of the pair found in the iteration; if no match is found, then 'False'

duplicateCheckHeavy - will mark all identical polygons with 'True'; this is used for deletion purposes where only one single identical polygon will remain. Ensures there are no overlapping geometries
