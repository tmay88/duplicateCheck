import arcpy

class Toolbox(object):
    def __init__(self):
        self.label = "Duplicate Check Toolbox"
        self.alias = "Duplicate Check Toolbox"
        self.tools = [FullAddressDuplicateCheck, DetectDuplicatePolygons, DetectDuplicatePolygonsHeavy]

class FullAddressDuplicateCheck:
    def __init__(self):
        self.label = "Full Address Duplicate Check"
        self.description = "Checks for duplicates in a user-specified field then adds 'True' or 'False' to a new field named 'duplicate' based on whether or not a duplicate was found."
        self.canRunInBackground = False

    def getParameterInfo(self):
        input_fc = arcpy.Parameter(
            name="input_fc",
            displayName="Input Feature Class",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        input_field = arcpy.Parameter(
            name="input_field",
            displayName="Input Field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )

        input_field.parameterDependencies = [input_fc.name]
        
        params = [input_fc, input_field]

        # Set the list of fields for the 'Field' parameter
        try:
            if input_field.value:
                params[1].filter.list = [f.name for f in arcpy.ListFields(input_field.value)]
        except:
            pass

        return params

    def execute(self, params, messages):
        # Get input feature class and field from user
        input_fc = params[0].valueAsText
        input_field = params[1].valueAsText

        # Add "duplicate" field to input feature class
        arcpy.AddField_management(input_fc, "duplicate", "TEXT", field_length=5)
        messages.addMessage("Field 'duplicate' added to {}".format(input_fc))

        # Create list of non-null values from input field
        address_list = []
        with arcpy.da.SearchCursor(input_fc, input_field) as cursor:
            for row in cursor:
                if row[0] is not None:
                    address_list.append(row[0])
        messages.addMessage("Found {} non-null values in field '{}'".format(len(address_list), input_field))

        # Update "duplicate" field based on value counts
        with arcpy.da.UpdateCursor(input_fc, ["duplicate", input_field]) as cursor:
            for row in cursor:
                if row[1] is None:
                    row[0] = None
                elif address_list.count(row[1]) > 1:
                    row[0] = 'True'
                else:
                    row[0] = 'False'
                cursor.updateRow(row)
        messages.addMessage("'duplicate' field populated.")


class DetectDuplicatePolygons(object):
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Polygon Duplicate Check"
        self.description = "Adds x_centroid, y_centroid, and duplicate_geometry fields to input feature class, calculates centroids and checks for duplicates. **This will not mark the first found coordinate pair as 'True'"
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Input feature class parameter
        param0 = arcpy.Parameter(
            displayName="Input Feature Class",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [param0]
        return params

    def execute(self, parameters, messages):
        # Get input feature class
        in_features = parameters[0].valueAsText

        # Add new fields
        arcpy.AddField_management(in_features, "x_centroid", "DOUBLE")
        arcpy.AddField_management(in_features, "y_centroid", "DOUBLE")
        arcpy.AddField_management(in_features, "duplicate_geometry", "TEXT", field_length=5)

        # Calculate centroid coordinates and update duplicate_geometry field
        coord_counts = {}
        fields = ["SHAPE@TRUECENTROID", "x_centroid", "y_centroid", "duplicate_geometry"]
        with arcpy.da.UpdateCursor(in_features, fields) as cursor:
            for row in cursor:
                centroid = row[0]
                x = round(centroid[0], 7)
                y = round(centroid[1], 7)
                row[1] = x
                row[2] = y

                coord = (x, y)
                if coord in coord_counts:
                    coord_counts[coord] += 1
                    row[3] = "True"
                else:
                    coord_counts[coord] = 1
                    row[3] = "False"

                cursor.updateRow(row)

        messages.addMessage("Fields added and calculations complete.")

class DetectDuplicatePolygonsHeavy(object):
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Heavy Polygon Duplicate Check"
        self.description = "Adds x_centroid, y_centroid, and duplicate_geometry fields to input feature class, calculates centroids and checks for duplicates."
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Input feature class parameter
        param0 = arcpy.Parameter(
            displayName="Input Feature Class",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [param0]
        return params

    def execute(self, parameters, messages):
        # Get input feature class
        in_features = parameters[0].valueAsText

        # Add new fields
        arcpy.AddField_management(in_features, "x_centroid", "DOUBLE")
        arcpy.AddField_management(in_features, "y_centroid", "DOUBLE")
        arcpy.AddField_management(in_features, "all_duplicate_geometry", "TEXT", field_length=5)

        # Calculate centroid coordinates
        with arcpy.da.UpdateCursor(in_features, ["SHAPE@TRUECENTROID", "x_centroid", "y_centroid"]) as cursor:
            for row in cursor:
                centroid = row[0]
                x = round(centroid[0], 7)
                y = round(centroid[1], 7)
                row[1] = x
                row[2] = y
                cursor.updateRow(row)

        # Create a dictionary to store coordinate counts
        coord_counts = {}

        # Update duplicate geometry field based on value counts
        fields = ["x_centroid", "y_centroid", "all_duplicate_geometry"]
        with arcpy.da.UpdateCursor(in_features, fields) as cursor:
            for row in cursor:
                x_centroid = row[0]
                y_centroid = row[1]
                coord = (x_centroid, y_centroid)

                if coord in coord_counts:
                    # Increment count and mark as True
                    coord_counts[coord] += 1
                    row[2] = "True"
                else:
                    # First occurrence, mark as False
                    coord_counts[coord] = 1
                    row[2] = "False"

                cursor.updateRow(row)

        # Update duplicate_geometry field for all duplicates
        with arcpy.da.UpdateCursor(in_features, ["x_centroid", "y_centroid", "all_duplicate_geometry"]) as cursor:
            for row in cursor:
                x_centroid = row[0]
                y_centroid = row[1]
                coord = (x_centroid, y_centroid)

                if coord_counts[coord] > 1:
                    row[2] = "True"

                cursor.updateRow(row)

        messages.addMessage("Fields added and calculations complete.")









